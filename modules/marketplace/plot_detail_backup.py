# modules/marketplace/plot_detail.py
"""
Página de detalles completa de una finca
Muestra toda la información necesaria para que el cliente decida comprar
"""
import streamlit as st
import streamlit.components.v1 as components
import os
import json
import base64
import re
from pathlib import Path
from modules.marketplace.utils import calculate_edificability, reserve_plot
from modules.marketplace.catastro_api import fetch_by_ref_catastral
from modules.marketplace.marketplace import get_plot_image_path
from modules.marketplace.compatibilidad import get_proyectos_compatibles
from src import db

def generar_svg_solar_validado(superficie_parcela, max_construible, es_urbano=True):
    # Dimensiones del lienzo SVG
    width, height = 300, 250
    margin = 30

    # Color según tipo de suelo
    color_solar = "#e8f4f8" if es_urbano else "#fdf2e9" # Azul suave vs Naranja rústico
    color_borde = "#2980b9" if es_urbano else "#d35400"

    # 1. Dibujamos el Solar (La Parcela)
    solar_w = width - (margin * 2)
    solar_h = height - (margin * 2)

    # 2. Calculamos el área de construcción proporcional
    # Si la edificabilidad es el 33%, el cuadro interno ocupará esa proporción de área
    ratio = max_construible / superficie_parcela if superficie_parcela > 0 else 0
    factor_escala = ratio ** 0.5  # Raíz cuadrada para escala lineal

    const_w = solar_w * factor_escala
    const_h = solar_h * factor_escala

    # Centramos la construcción dentro del solar
    const_x = margin + (solar_w - const_w) / 2
    const_y = margin + (solar_h - const_h) / 2

    svg = f"""
    <svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
        <rect x="{margin}" y="{margin}" width="{solar_w}" height="{solar_h}"
              fill="{color_solar}" stroke="{color_borde}" stroke-width="2" />

        <rect x="{const_x}" y="{const_y}" width="{const_w}" height="{const_h}"
              fill="#2ecc71" fill-opacity="0.6" stroke="#27ae60" stroke-width="2" stroke-dasharray="4" />

        <text x="{width/2}" y="{margin-10}" text-anchor="middle" font-size="12" font-family="sans-serif" fill="#34495e">
            Parcela Real: {superficie_parcela} m²
        </text>
        <text x="{width/2}" y="{height-margin+20}" text-anchor="middle" font-size="11" font-family="sans-serif" fill="#27ae60">
            Máx. Edificable: {max_construible} m² ({int(ratio*100)}%)
        </text>
    </svg>
    """
    return svg

def get_all_plot_images(plot):
    """Obtener todas las imágenes de la finca"""
    images = []
    if plot.get('photo_paths'):
        try:
            paths = json.loads(plot['photo_paths']) if isinstance(plot.get('photo_paths'), str) else plot.get('photo_paths')
            if paths and isinstance(paths, list):
                for path in paths:
                    img_path = f"uploads/{path}"
                    if os.path.exists(img_path):
                        images.append(img_path)
        except (json.JSONDecodeError, TypeError):
            pass
    
    # Fallback a imagen única
    if not images:
        single_img = get_plot_image_path(plot)
        if single_img and os.path.exists(single_img):
            images.append(single_img)
    
    return images if images else ['assets/fincas/image1.jpg']

def get_project_images(proyecto):
    """Obtener todas las imágenes válidas de un proyecto"""
    images = []

    # Procesar foto principal
    foto_principal = proyecto.get('foto_principal')
    if foto_principal and os.path.exists(foto_principal):
        images.append(foto_principal)

    # Procesar galería de fotos
    galeria = proyecto.get('galeria_fotos', [])
    
    # Validar que galeria sea una lista y no un número
    if galeria and isinstance(galeria, list) and not any(isinstance(item, (int, float)) for item in galeria):
        for img_path in galeria:
            if img_path and isinstance(img_path, str) and img_path.strip() and img_path not in images and os.path.exists(img_path):
                images.append(img_path)

    # Si no hay imágenes válidas, usar fallback
    return images if images else ['assets/fincas/image1.jpg']

def show_plot_detail_page(plot_id: str):
    """Muestra la página completa de detalles de una finca"""
    
    # Limpiar sidebar para vista dedicada
    st.sidebar.empty()
    
    # Obtener datos de la finca
    conn = db.get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plots WHERE id = ?", (plot_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        st.error("❌ Finca no encontrada")
        if st.button("← Volver al mapa"):
            if 'selected_plot' in st.session_state:
                del st.session_state['selected_plot']
            st.rerun()
        return
    
    # Convertir row a dict
    plot = dict(row)
    
    import json

    # Normalizar solar_virtual: si viene como string JSON, convertirlo a dict
    solar_virtual = plot.get("solar_virtual")
    if isinstance(solar_virtual, str):
        try:
            solar_virtual = json.loads(solar_virtual)
        except Exception:
            solar_virtual = {}

    # Guardar de nuevo en plot para que el resto del código lo use correctamente
    plot["solar_virtual"] = solar_virtual
    
    # Título principal
    st.title(f"🏡 {plot.get('title', 'Finca sin título')}")
    
    # Botón volver
    if st.button("← Volver al mapa", key="back_to_map"):
        if 'selected_plot' in st.session_state:
            del st.session_state['selected_plot']
        st.rerun()
    
    st.markdown("---")
    
    # Galería de imágenes
    st.subheader("📸 Galería de Imágenes")
    images = get_all_plot_images(plot)
    
    if len(images) > 0:
        # Mostrar primera imagen grande
        col_img_main, col_img_thumb = st.columns([2, 1])
        with col_img_main:
            st.image(images[0], width=600, caption=plot.get('title', ''))
        
        with col_img_thumb:
            if len(images) > 1:
                st.caption("Más imágenes:")
                for i, img_path in enumerate(images[1:4]):  # Máximo 3 thumbnails
                    st.image(img_path, width=150)
    
    st.markdown("---")
    
    # Información principal en columnas
    col_info1, col_info2 = st.columns(2)
    
    with col_info1:
        st.subheader("📊 Información General")
        
        superficie = plot.get('surface_m2') or plot.get('m2') or 0
        precio = plot.get('price') or 0
        provincia = plot.get('province', 'N/A')
        localidad = plot.get('locality', plot.get('address', 'N/A'))
        
        st.metric("💰 Precio", f"€{precio:,.0f}")
        st.metric("📏 Superficie Total", f"{superficie} m²")
        
        # Edificabilidad
        edificabilidad = calculate_edificability(superficie, 0.33)
        st.metric("🏗️ Superficie Construible (33%)", f"{edificabilidad:.0f} m²")
        
        st.markdown(f"**📍 Ubicación:** {localidad}, {provincia}")
        st.markdown(f"**🏷️ Tipo:** {plot.get('type', 'Urbano')}")
        
        if plot.get('catastral_ref'):
            st.markdown(f"**📋 Referencia Catastral:** `{plot['catastral_ref']}`")
    
    with col_info2:
        st.subheader("📍 Ubicación en Mapa")
        try:
            import folium
            import streamlit.components.v1 as components
            lat = float(plot.get('lat', 40.4168))
            lon = float(plot.get('lon', -3.7038))
            m = folium.Map(location=[lat, lon], zoom_start=15, tiles="CartoDB positron")
            folium.Marker(
                [lat, lon],
                popup=plot.get('title', 'Finca'),
                icon=folium.Icon(color='red', icon='home', prefix='fa')
            ).add_to(m)
            components.html(m._repr_html_(), height=300)
        except Exception as e:
            st.error(f"Error mostrando mapa: {e}")
        # --- Mostrar plano 2D solar virtual ---
        try:
            from src.models.finca import FincaMVP
            from src.solar_virtual_svg import mostrar_solar_virtual_svg
            finca = FincaMVP.desde_dict(plot)
            mostrar_solar_virtual_svg(finca)
        except Exception as e:
            st.warning(f"No se pudo mostrar el plano 2D del solar virtual: {e}")

    st.markdown("### 🧭 Información del Solar")

    sv = plot.get("solar_virtual", {})

    forma = sv.get("forma", "No especificada")
    orient = sv.get("orientacion", "No especificada")
    ancho = sv.get("ancho", "—")
    largo = sv.get("largo", "—")

    st.write(f"**Forma del solar:** {forma}")
    st.write(f"**Orientación:** {orient}")
    st.write(f"**Ancho estimado:** {ancho} m")
    st.write(f"**Largo estimado:** {largo} m")
    
    st.markdown("---")

    st.markdown("### 🏗️ Configuración de la Casa")

    col_cfg1, col_cfg2 = st.columns(2)

    with col_cfg1:
        habitaciones = st.slider("Número de habitaciones", 1, 6, 3)
        banos = st.slider("Número de baños", 1, 4, 2)
        superficie_deseada = st.number_input("Superficie construida deseada (m²)", min_value=40, max_value=500, value=120)

    with col_cfg2:
        estilo = st.selectbox("Estilo arquitectónico", ["Moderno", "Mediterráneo", "Minimalista", "Rústico"])
        extras = st.multiselect("Extras opcionales", ["Piscina", "Garaje", "Sótano", "Terraza", "Porche"])
        presupuesto_max = st.number_input("Presupuesto máximo (€)", min_value=50000, max_value=2000000, value=250000)

    st.markdown("### 🤖 Validación y Diseño IA (MVP)")

    # --- INICIO DE LA CIRUGÍA ---
    import json
    from pathlib import Path

    # Intentamos localizar el informe real generado por compute_edificability.py
    # Lo buscamos en la raíz, que es donde el script lo guarda por defecto
    path_reporte = Path("catastro_output/validation_report.json")

    # Fallback: Valores por defecto de la base de datos
    superficie_final = plot['m2']
    max_construible = calculate_edificability(superficie_final) 
    tipo_suelo = "No Verificado"
    datos_validados = None

    if path_reporte.exists():
        try:
            with open(path_reporte, "r", encoding="utf-8") as f:
                datos_validados = json.load(f)
                # Si el ID del reporte coincide con la finca actual (opcional) 
                # o simplemente si el archivo existe, actualizamos valores:
                superficie_final = datos_validados.get('surface_m2', superficie_final)
                max_construible = datos_validados.get('max_buildable_m2', max_construible)
                tipo_suelo = datos_validados.get('soil_type', "URBANO")
        except Exception:
            pass # Si falla el JSON, el sistema sigue funcionando con los datos de DB
    # --- FIN DE LA CIRUGÍA ---
    
    st.write(f"**Superficie máxima construible:** {max_construible} m²")

    st.info("La IA revisará tus requisitos y generará una propuesta arquitectónica conceptual.")

    if st.button("✨ Generar Propuesta IA"):

        with st.spinner("Generando propuesta arquitectónica con IA..."):

            from modules.marketplace import ai_engine_groq as ai_engine

            # Lógica de corrección de m² construidos
            m2_deseados = superficie_deseada

            if not m2_deseados or m2_deseados <= 0:
                m2_correccion = max_construible
                motivo_correccion = (
                    "No se especificó superficie construida; se ha usado el máximo permitido por la edificabilidad."
                )
            elif m2_deseados > max_construible:
                m2_correccion = max_construible
                motivo_correccion = (
                    f"El usuario solicitó {m2_deseados} m² construidos, pero la edificabilidad máxima es de "
                    f"{max_construible} m². La propuesta se ha ajustado automáticamente a ese límite."
                )
            else:
                m2_correccion = m2_deseados
                motivo_correccion = (
                    f"El usuario solicitó {m2_deseados} m² construidos, dentro del máximo permitido de "
                    f"{max_construible} m²."
                )

            # Mostrar en UI
            st.write(f"**Superficie usada para el diseño:** {m2_correccion} m²")
            st.write(motivo_correccion)

            prompt = f"""
Actúas como arquitecto especializado en vivienda unifamiliar. 

DATOS DEL SOLAR
- Superficie total de parcela: {superficie_final:.0f} m²
- Superficie máxima construible (33%): {max_construible:.0f} m²
- Ubicación: {plot.get('localidad')}, {plot.get('provincia')}
- Tipo de solar: {plot.get('type') or "No especificado"}
- Referencia catastral: {plot.get('catastral_ref') or "No especificada"}

CONFIGURACIÓN DE LA VIVIENDA
- Superficie deseada por el usuario: {m2_deseados or "No especificada"} m²
- Superficie sobre la que se diseña el proyecto: {m2_correccion:.0f} m²
- Motivo de ajuste: {motivo_correccion}

1) PROPUESTA ARQUITECTÓNICA
Describe de forma clara y profesional:
- Concepto general de la vivienda. 
- Número de plantas y reparto aproximado de m² por planta.
- Distribución básica (zona de día, zona de noche, espacios exteriores).
- Criterios de orientación, luz natural y ventilación. 
- Materiales y estilo arquitectónico sugerido. 
- Consideraciones de sostenibilidad. 

2) SUPERFICIE Y NORMATIVA
Explica brevemente:
- Que el diseño se basa en {m2_correccion:.0f} m² construidos. 
- Qué pasaría si se intentara superar esa superficie. 

3) ESTIMACIÓN DE PRESUPUESTO
- Usa un rango de coste por m² razonable (por ejemplo, estándar y calidad media-alta).
- Calcula un rango aproximado de presupuesto para {m2_correccion:.0f} m²: 
  - Presupuesto orientativo mínimo. 
  - Presupuesto orientativo máximo. 
- Explica claramente que es una estimación orientativa, no vinculante.

4) PLANO DE DISTRIBUCIÓN (SVG DESPUÉS DE ===SVG_DISTRIBUCION===)

Después de la línea: 
===SVG_DISTRIBUCION===

Genera un SVG que represente la distribución interior de la vivienda siguiendo ESTRICTAMENTE estas reglas: 

**REGLAS OBLIGATORIAS:**

1. **Estructura base:**
   - Dibuja UN SOLO rectángulo principal (stroke negro, grosor 4) que representa el perímetro exterior de la vivienda
   - Dimensiones del viewBox: 600x400
   - Dimensiones del rectángulo principal: ancho=500, alto=300, posición x=50, y=50
   - Todas las estancias DEBEN estar DENTRO de este rectángulo, sin salirse ni flotar

2. **Organización de estancias (EJEMPLO OBLIGATORIO A SEGUIR):**
   - Divide el rectángulo principal en rectángulos contiguos (pegados entre sí, sin espacios vacíos)
   - Distribución típica recomendada: 
     * FILA SUPERIOR (y=50, altura=150):
       - Salón:  x=50, width=200 (~40 m²)
       - Comedor: x=250, width=150 (~25 m²)
       - Cocina: x=400, width=150 (~20 m²)
     * FILA INFERIOR (y=200, altura=150):
       - Habitación 1: x=50, width=150 (~30 m²)
       - Habitación 2: x=200, width=150 (~30 m²)
       - Habitación 3: x=350, width=100 (~25 m²)
       - Baño: x=450, width=100 (~20 m²)
   
3. **Proporciones:**
   - Cada estancia debe ser proporcional a sus m² reales
   - La suma total de superficies debe aproximarse a {m2_correccion:.0f} m²
   - Si una estancia ocupa 40m² de 120m² totales, debe ocupar ~33% del área visual

4. **Etiquetado (OBLIGATORIO):**
   - Dentro de cada rectángulo de estancia, escribe con <text>: 
     * Formato exacto: "Nombre (XX m²)"
     * text-anchor="middle"
     * Posición centrada en el rectángulo
     * font-size="12" o "14"
     * fill="black" o "#333"

5. **Elementos arquitectónicos:**
   - Puerta principal:  rectángulo pequeño (width=10, height=20) en x=295, y=345 (centro inferior), fill="brown"
   - Texto debajo: "Puerta principal" en y=385
   - Ventanas: líneas gruesas (stroke="blue", stroke-width="4") en bordes exteriores del perímetro
     * Ejemplo: <line x1="150" y1="50" x2="200" y2="50" stroke="blue" stroke-width="4"/>

6. **Formato técnico ESTRICTO:**
   - Comenzar EXACTAMENTE con:  <svg viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
   - Terminar EXACTAMENTE con: </svg>
   - Sin comentarios HTML dentro del SVG
   - Sin texto fuera del SVG
   - Paredes interiores: stroke="black", stroke-width="2"
   - Rellenos: tonos de gris (#E8E8E8, #D8D8D8, #C8C8C8, #E0E0E0, #B8B8B8)

**EJEMPLO DE REFERENCIA EXACTO (adapta solo nombres/m², NO la estructura):**

<svg viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
  <rect x="50" y="50" width="500" height="300" fill="none" stroke="black" stroke-width="4"/>
  
  <rect x="50" y="50" width="200" height="150" fill="#E8E8E8" stroke="black" stroke-width="2"/>
  <text x="150" y="125" text-anchor="middle" font-size="14" fill="#333">Salón (40 m²)</text>
  
  <rect x="250" y="50" width="150" height="150" fill="#D8D8D8" stroke="black" stroke-width="2"/>
  <text x="325" y="125" text-anchor="middle" font-size="14" fill="#333">Comedor (25 m²)</text>
  
  <rect x="400" y="50" width="150" height="150" fill="#C8C8C8" stroke="black" stroke-width="2"/>
  <text x="475" y="125" text-anchor="middle" font-size="14" fill="#333">Cocina (20 m²)</text>
  
  <rect x="50" y="200" width="150" height="150" fill="#E0E0E0" stroke="black" stroke-width="2"/>
  <text x="125" y="275" text-anchor="middle" font-size="14" fill="#333">Habitación 1 (30 m²)</text>
  
  <rect x="200" y="200" width="150" height="150" fill="#E0E0E0" stroke="black" stroke-width="2"/>
  <text x="275" y="275" text-anchor="middle" font-size="14" fill="#333">Habitación 2 (30 m²)</text>
  
  <rect x="350" y="200" width="100" height="150" fill="#E0E0E0" stroke="black" stroke-width="2"/>
  <text x="400" y="275" text-anchor="middle" font-size="12" fill="#333">Hab. 3 (25 m²)</text>
  
  <rect x="450" y="200" width="100" height="150" fill="#B8B8B8" stroke="black" stroke-width="2"/>
  <text x="500" y="275" text-anchor="middle" font-size="14" fill="#333">Baño (20 m²)</text>
  
  <rect x="295" y="345" width="10" height="20" fill="brown"/>
  <text x="300" y="385" text-anchor="middle" font-size="12" fill="black">Puerta principal</text>
  
  <line x1="150" y1="50" x2="200" y2="50" stroke="blue" stroke-width="4"/>
  <line x1="325" y1="50" x2="375" y2="50" stroke="blue" stroke-width="4"/>
  <line x1="550" y1="150" x2="550" y2="200" stroke="blue" stroke-width="4"/>
</svg>

**CRÍTICO:** 
- Adapta SOLO los nombres de estancias y m² al caso específico de {m2_correccion:.0f} m²
- NO cambies la estructura de rectángulo principal + estancias contiguas dentro
- NO hagas estancias flotantes ni separadas
- SIEMPRE respeta el formato exacto del ejemplo

Después del SVG, NO escribas nada más. 
"""

            try:
                # TRUCO DE INGENIERO: Generar texto y plano por separado para garantizar que aparezca
                # 1. Generamos el texto (resumen sin plano)
                resumen_prompt = f"""
Actúas como arquitecto especializado en vivienda unifamiliar.

DATOS DEL SOLAR
- Superficie total de parcela: {superficie_final:.0f} m²
- Superficie máxima construible (33%): {max_construible:.0f} m²
- Ubicación: {plot.get('localidad')}, {plot.get('provincia')}
- Tipo de solar: {plot.get('type') or "No especificado"}
- Referencia catastral: {plot.get('catastral_ref') or "No especificada"}

CONFIGURACIÓN DE LA VIVIENDA
- Superficie deseada por el usuario: {m2_deseados or "No especificada"} m²
- Superficie sobre la que se diseña el proyecto: {m2_correccion:.0f} m²
- Motivo de ajuste: {motivo_correccion}

PROPUESTA ARQUITECTÓNICA (máximo 200 palabras):
Describe de forma clara y profesional:
- Concepto general de la vivienda.
- Número de plantas y reparto aproximado de m² por planta.
- Distribución básica (zona de día, zona de noche, espacios exteriores).
- Criterios de orientación, luz natural y ventilación.
- Materiales y estilo arquitectónico sugerido.
- Consideraciones de sostenibilidad.

SUPERFICIE Y NORMATIVA:
Explica brevemente que el diseño se basa en {m2_correccion:.0f} m² construidos.

ESTIMACIÓN DE PRESUPUESTO:
- Usa un rango de coste por m² razonable (estándar y calidad media-alta).
- Calcula un rango aproximado de presupuesto para {m2_correccion:.0f} m².
- Explica claramente que es una estimación orientativa, no vinculante.
"""

                resumen = ai_engine.generate_text(resumen_prompt, max_tokens=600)
                st.success("Propuesta generada con éxito")

                st.markdown("### 🧩 Propuesta Arquitectónica IA")
                st.write(resumen)

                # Dentro de la vista de detalles
                if datos_validados:
                    svg_grafico = generar_svg_solar_validado(
                        superficie_parcela=datos_validados['surface_m2'],
                        max_construible=datos_validados['max_buildable_m2'],
                        es_urbano=(datos_validados['soil_type'] == "URBANO")
                    )
                    st.subheader("Plano conceptual")
                    components.html(svg_grafico, height=300)

                st.divider()

                # 2. Generamos el PLANO de forma independiente (¡Esto garantiza que salga!)
                st.subheader("📐 Esquema de Planta (IA)")
                plano_prompt = f"Vivienda unifamiliar de {m2_correccion:.0f} m² con salón, comedor, cocina, 3 habitaciones y baño"
                plano = ai_engine.generate_ascii_plan(plano_prompt)
                st.code(plano, language="text")  # Usamos st.code para que el dibujo no se descuadre

            except Exception as e:
                st.error(f"Error generando propuesta IA: {e}")

    # NUEVO BOTÓN: DOSSIER DE PRE-VENTA CON IA
    st.markdown("### 📄 Dossier de Pre-Venta con IA")

    if st.button("🤖 GENERAR DOSSIER DE PRE-VENTA (IA)", type="primary"):
        with st.spinner("Analizando memoria técnica y dimensiones..."):
            from modules.marketplace import ai_engine_groq as ai

            # Definir text_context para todo el flujo
            text_context = plot.get('description', '') or plot.get('title', 'Proyecto inmobiliario')

            # PASO 1: Extraer tabla de m2 (Pág 13 de la memoria)
            tabla_m2 = ai.extract_area_table(text_context)
            st.subheader("📊 Cuadro de Superficies Extraído")
            st.markdown(tabla_m2)

            # PASO 2: Generar el resumen corto (Para que no se corte)
            resumen = ai.generate_text(f"Resume brevemente el estilo de este proyecto: {text_context[:1000]}", max_tokens=250)
            st.write(resumen)

            st.divider()

            # PASO 3: EL PLANO (Llamada independiente con st.code)
            st.subheader("📐 Esquema de Distribución Sugerido")
            plano_visual = ai.generate_blueprint_from_data(tabla_m2)

            # El bloque st.code fuerza a la IA a mostrar el dibujo sin deformarlo
            st.code(plano_visual, language="text")

            st.success("✅ Análisis completado. Este proyecto cumple con la normativa detectada.")

    # Descripción
    if plot.get('description'):
        st.subheader("📝 Descripción")
        st.write(plot['description'])
        st.markdown("---")
    
    # Datos catastrales
    st.subheader("📋 Datos Catastrales")
    col_cat1, col_cat2 = st.columns(2)
    
    with col_cat1:
        st.markdown(f"**Superficie Total:** {superficie} m²")
        st.markdown(f"**Edificabilidad máxima:** {edificabilidad:.0f} m² (33%)")
        if plot.get('catastral_ref'):
            st.markdown(f"**Ref. Catastral:** `{plot['catastral_ref']}`")
        if plot.get('type'):
            st.markdown(f"**Tipo de Suelo:** {plot['type']}")
    
    with col_cat2:
        st.markdown(f"**Provincia:** {provincia}")
        st.markdown(f"**Localidad:** {localidad}")
        if plot.get('services'):
            st.markdown(f"**Servicios:** {plot['services']}")
        
        # Mostrar coordenadas GPS si están disponibles
        if plot.get('lat') and plot.get('lon'):
            st.markdown(f"**Coordenadas GPS:** {float(plot['lat']):.6f}, {float(plot['lon']):.6f}")

    st.markdown("---")

    # NUEVO BOTÓN: Análisis y Esquema Técnico
    if st.button("🤖 Generar Análisis y Esquema Técnico", type="primary"):
        # Cargamos datos reales del JSON de validación
        import json
        from pathlib import Path

        path_json = Path("catastro_output/validation_report.json")
        datos_verificados = {}
        if path_json.exists():
            with open(path_json, "r", encoding="utf-8") as f:
                datos_verificados = json.load(f)

        with st.spinner("Consultando con el Arquitecto IA..."):
            from modules.marketplace import ai_engine_groq as ai

            # LLAMADA 1: Resumen Profesional (Corto para que no se sature)
            # Usamos los datos del JSON para que la IA no invente
            project_info = plot.get('description', '') or plot.get('title', 'Proyecto inmobiliario')
            prompt_resumen = f"""
            Resume este proyecto inmobiliario: {project_info[:1500]}
            DATOS CLAVE: Superficie {datos_verificados.get('surface_m2')}m2,
            Edificabilidad {datos_verificados.get('max_buildable_m2')}m2.
            Sé directo y profesional.
            """
            resumen = ai.generate_text(prompt_resumen, max_tokens=500)
            st.markdown("### 📋 Resumen Ejecutivo")
            st.write(resumen)

            st.divider()

            # LLAMADA 2: El Plano ASCII (Independiente)
            st.markdown("### 📐 Esquema de Planta Sugerido")
            # Le pasamos los m2 reales para que el dibujo tenga sentido
            prompt_plano = f"Planta para una vivienda en parcela de {datos_verificados.get('surface_m2')}m2 con {datos_verificados.get('max_buildable_m2')}m2 construibles."
            plano_ascii = ai.generate_ascii_plan(prompt_plano)

            # ¡IMPORTANTE! Usar st.code para que las líneas no se tuerzan
            st.code(plano_ascii, language="text")

    # Validación de edificabilidad
    st.subheader("✅ Validación de Edificabilidad")
    if datos_validados is not None:
        if tipo_suelo == 'URBANO':
            st.success(f"✅ Viable: {max_construible}m² edificables")
        else:
            st.warning("⚠️ Restricciones detectadas")
    else:
        st.info("No hay reporte de validación disponible")
    
    st.markdown("---")
    
    # 🏗️ PROYECTOS ARQUITECTÓNICOS DISPONIBLES
    st.subheader("🏗️ Proyectos Arquitectónicos Disponibles")
    
    proyectos = get_proyectos_compatibles(plot_id)
    
    if not proyectos:
        st.info("No hay proyectos arquitectónicos compatibles disponibles para esta finca en este momento.")
    else:
        st.markdown(f"**Encontrados {len(proyectos)} proyecto(s) compatible(s) con esta finca**")
        st.caption("Estos proyectos están diseñados para superficies similares a la edificabilidad máxima de tu finca.")
        
        for proyecto in proyectos:
            with st.container():
                col_img, col_info, col_action = st.columns([1, 2, 1])
                
                with col_img:
                    # Obtener imágenes válidas del proyecto
                    project_images = get_project_images(proyecto)
                    img_path = project_images[0] if project_images else None

                    if img_path:
                        try:
                            st.image(img_path, width=120, caption="")
                        except Exception as e:
                            st.image("assets/fincas/image1.jpg", width=120, caption="Imagen no disponible")
                    else:
                        st.image("assets/fincas/image1.jpg", width=120, caption="Imagen no disponible")
                
                with col_info:
                    # Información del proyecto
                    nombre = proyecto.get("nombre", "Proyecto sin nombre")
                    total_m2 = proyecto.get("total_m2", 0)
                    precio_estimado = proyecto.get("precio_estimado", 0)
                    
                    st.markdown(f"**🏠 {nombre}**")
                    st.markdown(f"**📏 Superficie:** {total_m2} m²")
                    if precio_estimado > 0:
                        st.markdown(f"**💰 Coste estimado:** €{precio_estimado:,.0f}")
                    else:
                        st.markdown("**💰 Coste estimado:** Consultar")
                    
                    # Mostrar etiquetas si existen
                    etiquetas = proyecto.get("etiquetas", [])
                    if etiquetas:
                        tags_text = " • ".join(etiquetas)
                        st.caption(f"🏷️ {tags_text}")
                
                with col_action:
                    # Botón para ver proyecto completo
                    if st.button("👁️ Ver proyecto", key=f"ver_proyecto_{proyecto.get('id', nombre)}", width='stretch'):
                        # Verificar si el usuario está logueado
                        buyer_email = st.session_state.get('buyer_email')
                        buyer_name = st.session_state.get('buyer_name')
                        
                        if buyer_email and buyer_name:
                            st.success(f"✅ Redirigiendo a detalles del proyecto: {nombre}")
                            st.info("Aquí podrás ver todos los planos, especificaciones técnicas y contactar con el arquitecto.")
                            # TODO: Implementar navegación a página de detalles del proyecto
                        else:
                            st.warning("🔐 Para ver los detalles completos del proyecto necesitas estar registrado.")
                            st.info("Regístrate abajo para acceder a toda la información del proyecto.")
                
                st.markdown("---")
    
    # Información adicional de IA si está disponible
    if plot.get('plano_catastral_path') and os.path.exists(plot['plano_catastral_path']):
        st.markdown("---")
        st.subheader("🤖 Datos Extraídos por IA")
        col_ia1, col_ia2 = st.columns(2)
        
        with col_ia1:
            st.info("📄 Documento analizado por Gemini AI")
            if plot.get('m2'):
                st.metric("Superficie Registrada", f"{plot['m2']} m²")
            if plot.get('locality'):
                st.metric("Municipio Detectado", plot['locality'])
        
        with col_ia2:
            # Mostrar preview del PDF si existe
            try:
                pdf_path = plot['plano_catastral_path']
                if os.path.exists(pdf_path):
                    st.success("✅ Plano Catastral disponible")
                    with open(pdf_path, 'rb') as f:
                        pdf_data = f.read()
                        b64 = base64.b64encode(pdf_data).decode()
                        href = f"data:application/pdf;base64,{b64}"
                        st.markdown(f'[📄 Ver Plano Catastral Completo]({href})', unsafe_allow_html=True)
                else:
                    st.warning("Plano catastral no encontrado")
            except Exception as e:
                st.error(f"Error cargando plano: {e}")
    
    st.markdown("---")
    
    # Funcionalidades de IA
    st.subheader("🤖 Herramientas de IA")
    
    col_gemelo, col_diseno = st.columns(2)
    
    with col_gemelo:
        st.markdown("### 🏗️ Gemelo Digital")
        st.markdown("Crea una réplica virtual 3D de tu proyecto")
        if st.button("🚀 Crear Gemelo Digital", key="btn_gemelo", type="secondary"):
            # Guardar el ID de la parcela actual para el gemelo digital
            st.session_state["selected_plot_for_gemelo"] = plot_id
            st.session_state["page"] = "gemelo_digital"
            st.success("🔄 Redirigiendo al Gemelo Digital...")
            st.info("Allí podrás diseñar tu vivienda en 3D con IA")
            st.rerun()
    
    with col_diseno:
        st.markdown("### 🏠 Diseño con IA")
        st.markdown("Arquitecto virtual para diseñar tu casa")
        if st.button("🎨 Diseñar con IA", key="btn_diseno", type="secondary"):
            # Guardar el ID de la parcela actual para el diseñador
            st.session_state["selected_plot_for_design"] = plot_id
            st.session_state["page"] = "disenador_vivienda"
            st.success("🔄 Redirigiendo al Arquitecto Virtual...")
            st.info("Un asistente IA te guiará paso a paso")
            st.rerun()
    
    st.markdown("---")
    
    # Acciones: Reservar o Comprar
    st.subheader("💳 Acciones")
    
    # Verificar si ya está registrado
    buyer_email = st.session_state.get('buyer_email')
    buyer_name = st.session_state.get('buyer_name')
    
    if not buyer_email or not buyer_name:
        # Formulario de registro primero
        st.info("📝 Por favor completa tus datos para proceder con la reserva o compra")
        
        with st.form("register_buyer"):
            col_reg1, col_reg2 = st.columns(2)
            with col_reg1:
                nombre = st.text_input("Nombre *", key="reg_nombre")
                apellidos = st.text_input("Apellidos *", key="reg_apellidos")
                email_reg = st.text_input("Email *", key="reg_email")
                telefono = st.text_input("Teléfono *", key="reg_telefono")
            with col_reg2:
                direccion = st.text_area("Dirección *", key="reg_direccion")
                provincia_reg = st.text_input("Provincia *", key="reg_provincia")
                pais = st.selectbox("País *", ["España", "Portugal", "Otro"], key="reg_pais", index=0)
            
            submitted_reg = st.form_submit_button("✅ Registrar y Continuar", type="primary")
            
            if submitted_reg:
                if not all([nombre, apellidos, email_reg, telefono, direccion, provincia_reg]):
                    st.error("Por favor completa todos los campos obligatorios (*)")
                else:
                    st.session_state['buyer_name'] = f"{nombre} {apellidos}"
                    st.session_state['buyer_email'] = email_reg
                    st.session_state['buyer_phone'] = telefono
                    st.session_state['buyer_address'] = direccion
                    st.session_state['buyer_province'] = provincia_reg
                    st.session_state['buyer_country'] = pais
                    st.success("✅ Datos guardados. Ahora puedes reservar o comprar.")
                    st.rerun()
    else:
        # Ya registrado, mostrar botones de acción
        st.success(f"✅ Registrado como: {buyer_name} ({buyer_email})")
        
        col_reserve, col_buy = st.columns(2)
        
        with col_reserve:
            reservation_amount = precio * 0.10
            st.markdown(f"### 💰 Reservar (10%)")
            st.markdown(f"**Importe:** €{reservation_amount:,.0f}")
            st.caption("Reserva la finca pagando el 10% del precio total")
            
            if st.button("🔒 Reservar Finca", key="btn_reserve", type="primary"):
                try:
                    rid = reserve_plot(
                        plot_id,
                        buyer_name,
                        buyer_email,
                        reservation_amount,
                        kind="reservation"
                    )
                    st.success(f"✅ Reserva realizada exitosamente!")
                    st.info(f"**ID de Reserva:** `{rid}`")
                    st.info(f"**Importe:** €{reservation_amount:,.0f}")
                    st.info(f"📧 Recibirás un email de confirmación en {buyer_email}")
                    st.info(f"🔗 Accede a tu portal de cliente para gestionar tu reserva")
                    
                    # Guardar email en session_state para auto-login
                    st.session_state['auto_owner_email'] = buyer_email
                    st.balloons()
                    st.info("🔄 Redirigiendo a tu portal de cliente...")
                    # Redirigir a portal cliente (será manejado en app.py)
                    st.session_state['role'] = 'cliente'
                    st.session_state['current_page'] = 'client_portal'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al procesar la reserva: {str(e)}")
        
        with col_buy:
            st.markdown(f"### 🏠 Comprar (100%)")
            st.markdown(f"**Importe Total:** €{precio:,.0f}")
            st.caption("Compra la finca completa")
            
            if st.button("💳 Comprar Finca", key="btn_buy", type="primary"):
                try:
                    rid = reserve_plot(
                        plot_id,
                        buyer_name,
                        buyer_email,
                        precio,
                        kind="purchase"
                    )
                    st.success(f"✅ Compra realizada exitosamente!")
                    st.info(f"**ID de Transacción:** `{rid}`")
                    st.info(f"**Importe:** €{precio:,.0f}")
                    st.info(f"📧 Recibirás un email de confirmación en {buyer_email}")
                    st.info(f"🔗 Accede a tu portal de cliente para gestionar tu compra")
                    
                    # Guardar email en session_state para auto-login
                    st.session_state['auto_owner_email'] = buyer_email
                    st.balloons()
                    st.info("🔄 Redirigiendo a tu portal de cliente...")
                    # Redirigir a portal cliente (será manejado en app.py)
                    st.session_state['role'] = 'cliente'
                    st.session_state['current_page'] = 'client_portal'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al procesar la compra: {str(e)}")
    
    st.markdown("---")
    
    # Nuevo botón para análisis de terreno
    st.markdown("### 📊 Análisis Técnico de Terreno")
    st.markdown("Análisis profesional de viabilidad basado en datos catastrales validados")
    
    import json
    from pathlib import Path
    
    # Ruta quirúrgica al reporte generado por tu script
    PATH_VALIDACION = Path("catastro_output/validation_report.json")
    
    if st.button("🪄 Análisis Experto (Datos Verificados)", type="primary"):
        if PATH_VALIDACION.exists():
            with open(PATH_VALIDACION, "r", encoding="utf-8") as f:
                datos_finca = json.load(f)
            
            with st.spinner("Consultando inteligencia técnica..."):
                # Intentar obtener contexto OCR para análisis más completo
                ocr_context = ""
                ocr_paths = [
                    Path("archirapid_extract/catastro_output/ocr_text.txt"),
                    Path("archirapid_extract/catastro_output/extracted_text.txt")
                ]
                
                for ocr_path in ocr_paths:
                    if ocr_path.exists():
                        try:
                            with open(ocr_path, "r", encoding="utf-8") as f:
                                ocr_context = f.read()[:2000]  # Limitar a 2000 caracteres
                            break
                        except Exception:
                            continue
                
                # Usar análisis completo si hay contexto OCR, sino usar versión ligera
                from modules.marketplace.ai_engine_groq import generate_validated_analysis, generar_analisis_ligero
                
                if ocr_context.strip():
                    respuesta = generate_validated_analysis(datos_finca, ocr_context)
                else:
                    respuesta = generar_analisis_ligero(datos_finca)
                
                st.info("### 📋 Informe de Viabilidad")
                st.markdown(respuesta)
        else:
            st.warning("⚠️ No se encuentra el reporte de validación. Ejecuta primero 'compute_edificability.py'.")

