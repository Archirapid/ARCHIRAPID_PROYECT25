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

    # ========================================================================
    # SECCIÓN 1: FICHA TÉCNICA DEL TERRENO (Visible para todos)
    # ========================================================================

    st.header("📋 Ficha Técnica del Terreno")

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
        st.subheader("📊 Datos del Terreno")

        superficie = plot.get('surface_m2') or plot.get('m2') or 0
        precio = plot.get('price') or 0
        provincia = plot.get('province', 'N/A')
        localidad = plot.get('locality', plot.get('address', 'N/A'))

        st.metric("💰 Precio", f"€{precio:,.0f}")
        st.metric("📏 Superficie Total", f"{superficie} m²")

        # Cálculo de edificabilidad (33%)
        max_edificable = calculate_edificability(superficie, 0.33)
        st.metric("🏗️ Máximo Construible (33%)", f"{max_edificable:.0f} m²")

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

    st.markdown("---")

    # Botón de acción principal: Reservar o Comprar
    st.subheader("📝 ¿Interesado en esta finca?")

    # Estado de expansión del formulario
    show_form = st.session_state.get(f'form_expanded_{plot_id}', False)

    if st.button("📝 Reservar o Comprar Finca", type="primary"):
        st.session_state[f'form_expanded_{plot_id}'] = not show_form
        st.rerun()

    # Formulario de contacto (expandible)
    if st.session_state.get(f'form_expanded_{plot_id}', False):
        st.markdown("### 📋 Formulario de Contacto")

        col_form1, col_form2 = st.columns(2)

        with col_form1:
            buyer_name = st.text_input("Nombre completo *", key=f"name_{plot_id}")
            buyer_email = st.text_input("Email *", key=f"email_{plot_id}")

        with col_form2:
            buyer_phone = st.text_input("Teléfono", key=f"phone_{plot_id}")
            reservation_type = st.selectbox(
                "Tipo de interés",
                ["Reserva (10%)", "Compra completa (100%)"],
                key=f"type_{plot_id}"
            )

        # Calcular importe según tipo
        if reservation_type == "Reserva (10%)":
            amount = precio * 0.1
            amount_text = f"€{amount:,.0f} (10% del precio total)"
        else:
            amount = precio
            amount_text = f"€{amount:,.0f} (precio completo)"

        st.markdown(f"**Importe a pagar:** {amount_text}")

        if st.button("✅ Confirmar y Proceder", type="primary", key=f"confirm_{plot_id}"):
            if not buyer_name or not buyer_email:
                st.error("Por favor completa nombre y email")
            else:
                try:
                    kind = "reservation" if "Reserva" in reservation_type else "purchase"
                    rid = reserve_plot(
                        plot_id,
                        buyer_name,
                        buyer_email,
                        amount,
                        kind=kind
                    )
                    st.success(f"✅ Operación realizada exitosamente!")
                    st.info(f"**ID de Transacción:** `{rid}`")
                    st.info(f"**Importe:** {amount_text}")
                    st.info(f"📧 Recibirás un email de confirmación en {buyer_email}")
                    st.info(f"🔗 Accede a tu portal de cliente para gestionar tu operación")

                    # Guardar email en session_state para auto-login
                    st.session_state['auto_owner_email'] = buyer_email
                    st.balloons()
                    st.info("🔄 Redirigiendo a tu portal de cliente...")
                    # Redirigir a portal cliente (será manejado en app.py)
                    st.session_state['role'] = 'cliente'
                    st.session_state['current_page'] = 'client_portal'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al procesar la operación: {str(e)}")

    st.markdown("---")

    # ========================================================================
    # SECCIÓN 2: HERRAMIENTAS DE PROYECTO (Condicional)
    # ========================================================================

    # Control de visibilidad de la sección 2
    show_tools = st.session_state.get(f'tools_expanded_{plot_id}', False)

    # Botón para mostrar/ocultar herramientas de proyecto
    col_tools_toggle, _ = st.columns([1, 3])
    with col_tools_toggle:
        if st.button("🔧 Explorar Posibilidades de Proyecto", type="secondary"):
            st.session_state[f'tools_expanded_{plot_id}'] = not show_tools
            st.rerun()

    if show_tools:
        st.header("🏗️ Herramientas de Proyecto")

        # Diseño IA
        st.subheader("🎨 Diseño con IA")

        col_cfg1, col_cfg2 = st.columns(2)

        with col_cfg1:
            habitaciones = st.slider("Número de habitaciones", 1, 6, 3, key=f"hab_{plot_id}")
            banos = st.slider("Número de baños", 1, 4, 2, key=f"banos_{plot_id}")
            superficie_deseada = st.number_input("Superficie construida deseada (m²)",
                                               min_value=40, max_value=int(max_edificable),
                                               value=min(120, int(max_edificable)),
                                               key=f"sup_{plot_id}")

        with col_cfg2:
            estilo = st.selectbox("Estilo arquitectónico",
                                ["Moderno", "Mediterráneo", "Minimalista", "Rústico"],
                                key=f"estilo_{plot_id}")
            extras = st.multiselect("Extras opcionales",
                                  ["Piscina", "Garaje", "Sótano", "Terraza", "Porche"],
                                  key=f"extras_{plot_id}")
            presupuesto_max = st.number_input("Presupuesto máximo (€)",
                                            min_value=50000, max_value=2000000, value=250000,
                                            key=f"presupuesto_{plot_id}")

        st.info("La IA revisará tus requisitos y generará una propuesta arquitectónica conceptual.")

        if st.button("✨ Generar Propuesta IA", key=f"generate_{plot_id}"):

            with st.spinner("Generando propuesta arquitectónica con IA..."):

                from modules.marketplace import ai_engine_groq as ai_engine

                # Lógica de corrección de m² construidos
                m2_deseados = superficie_deseada

                if not m2_deseados or m2_deseados <= 0:
                    m2_correccion = max_edificable
                    motivo_correccion = (
                        "No se especificó superficie construida; se ha usado el máximo permitido por la edificabilidad."
                    )
                elif m2_deseados > max_edificable:
                    m2_correccion = max_edificable
                    motivo_correccion = (
                        f"El usuario solicitó {m2_deseados} m² construidos, pero la edificabilidad máxima es de "
                        f"{max_edificable} m². La propuesta se ha ajustado automáticamente a ese límite."
                    )
                else:
                    m2_correccion = m2_deseados
                    motivo_correccion = (
                        f"El usuario solicitó {m2_deseados} m² construidos, dentro del máximo permitido de "
                        f"{max_edificable} m²."
                    )

                # Mostrar en UI
                st.write(f"**Superficie usada para el diseño:** {m2_correccion} m²")
                st.write(motivo_correccion)

                prompt = f"""
Actúas como arquitecto especializado en vivienda unifamiliar.

DATOS DEL SOLAR
- Superficie total de parcela: {superficie:.0f} m²
- Superficie máxima construible (33%): {max_edificable:.0f} m²
- Ubicación: {localidad}, {provincia}
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
"""

                try:
                    respuesta = ai_engine.generate_text(prompt)

                    # Mostrar respuesta
                    st.markdown("### 🏠 Propuesta Arquitectónica Generada")

                    # Separar texto y SVG
                    if "===SVG_DISTRIBUCION===" in respuesta:
                        partes = respuesta.split("===SVG_DISTRIBUCION===")
                        texto_respuesta = partes[0].strip()
                        svg_plano = partes[1].strip() if len(partes) > 1 else ""

                        st.markdown(texto_respuesta)

                        if svg_plano:
                            st.markdown("### 📐 Plano de Distribución")
                            components.html(svg_plano, height=450)
                    else:
                        st.markdown(respuesta)

                except Exception as e:
                    st.error(f"Error generando propuesta: {str(e)}")

        st.markdown("---")

        # Proyectos Compatibles
        st.subheader("🏢 Proyectos Compatibles")

        # Filtrar proyectos cuya superficie construida <= 33% de la finca actual
        proyectos_compatibles = get_proyectos_compatibles(max_edificable)

        if proyectos_compatibles:
            st.info(f"Se encontraron {len(proyectos_compatibles)} proyectos compatibles con esta finca (superficie ≤ {max_edificable:.0f} m²)")

            for proyecto in proyectos_compatibles[:5]:  # Máximo 5 proyectos
                with st.expander(f"🏗️ {proyecto.get('titulo', 'Proyecto sin título')}"):

                    col_proj1, col_proj2 = st.columns(2)

                    with col_proj1:
                        st.write(f"**Superficie:** {proyecto.get('superficie_construida', 0)} m²")
                        st.write(f"**Presupuesto:** €{proyecto.get('presupuesto_estimado', 0):,.0f}")
                        st.write(f"**Arquitecto:** {proyecto.get('arquitecto', 'No especificado')}")

                    with col_proj2:
                        # Mostrar imágenes del proyecto
                        imagenes_proyecto = get_project_images(proyecto)
                        if imagenes_proyecto:
                            st.image(imagenes_proyecto[0], width=200, caption=proyecto.get('titulo', ''))

                    if proyecto.get('descripcion'):
                        st.markdown(f"**Descripción:** {proyecto['descripcion']}")

                    if st.button(f"📋 Ver Detalles Completos", key=f"detail_{proyecto.get('id', 'unknown')}"):
                        st.info("Funcionalidad de detalles completos pendiente de implementación")
        else:
            st.info("No se encontraron proyectos compatibles en la base de datos.")

        st.markdown("---")

        # Gemelo Digital
        st.subheader("🤖 Gemelo Digital")

        st.markdown("Crea una réplica virtual 3D de tu proyecto arquitectónico")

        if st.button(f"🚀 Crear Gemelo Digital", key=f"btn_gemelo_{plot_id}", type="secondary"):
            # Guardar el ID de la parcela actual para el gemelo digital
            st.session_state["selected_plot_for_gemelo"] = plot_id
            st.session_state["page"] = "gemelo_digital"
            st.success("🔄 Redirigiendo al Gemelo Digital...")
            st.info("Allí podrás diseñar tu vivienda en 3D con IA")
            st.rerun()

        st.markdown("---")

        # Análisis Técnico de Terreno
        st.subheader("📊 Análisis Técnico de Terreno")
        st.markdown("Análisis profesional de viabilidad basado en datos catastrales validados")

        import json
        from pathlib import Path

        # Ruta quirúrgica al reporte generado por tu script
        PATH_VALIDACION = Path("catastro_output/validation_report.json")

        if st.button("🪄 Análisis Experto (Datos Verificados)", key=f"analysis_{plot_id}", type="primary"):
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