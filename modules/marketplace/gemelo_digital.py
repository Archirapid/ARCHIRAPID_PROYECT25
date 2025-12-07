# modules/marketplace/gemelo_digital.py
"""
Gemelo Digital Inteligente para ARCHIRAPID
Módulo que crea réplicas virtuales de proyectos con análisis IA en tiempo real.
Integración quirúrgica: no rompe código existente, reutiliza componentes.
"""

import streamlit as st
import plotly.graph_objects as go
import json
from modules.marketplace.utils import list_published_plots
from modules.marketplace.ai_engine import get_ai_response

def generar_plan_vivienda(plot_data, num_habitaciones, num_banos, con_garage, presupuesto_max):
    """
    Genera un plan de vivienda estructurado usando IA.
    Devuelve JSON con distribución de habitaciones y cálculos automáticos.

    Args:
        plot_data: Datos de la parcela del marketplace
        num_habitaciones: Número de habitaciones deseadas
        num_banos: Número de baños deseados
        con_garage: Si incluye garage
        presupuesto_max: Presupuesto máximo en euros

    Returns:
        dict: Plan estructurado en formato JSON
    """
    superficie_parcela = plot_data['surface_m2']
    m2_construibles = int(superficie_parcela * 0.33)  # 33% de edificabilidad

    prompt = f"""
    ERES UN ARQUITECTO EXPERTO EN DISEÑO DE VIVIENDAS EFICIENTES.

    Debes generar un PLAN DE VIVIENDA COMPLETO en formato JSON válido.

    DATOS DE ENTRADA:
    - Superficie parcela: {superficie_parcela} m²
    - Superficie construible máxima: {m2_construibles} m²
    - Habitaciones deseadas: {num_habitaciones}
    - Baños deseados: {num_banos}
    - Garage incluido: {"Sí" if con_garage else "No"}
    - Presupuesto máximo: €{presupuesto_max}

    INSTRUCCIONES:
    1. Calcula distribución óptima respetando normativa española
    2. Asigna m² realistas a cada habitación (salón 20-30m², dormitorios 10-18m², etc.)
    3. Incluye garage de 15-25m² si se solicita
    4. Mantén total_m2_construido ≤ {m2_construibles}
    5. Calcula presupuesto aproximado (€/m² construcción: 800-1200)

    FORMATO JSON REQUERIDO (responde SOLO con JSON válido):
    {{
        "distribucion": [
            {{"tipo": "salon", "nombre": "Salón-Comedor", "m2": 25, "descripcion": "Espacio principal con luz natural"}},
            {{"tipo": "dormitorio", "nombre": "Dormitorio Principal", "m2": 15, "descripcion": "Suite con baño en suite"}},
            {{"tipo": "cocina", "nombre": "Cocina", "m2": 10, "descripcion": "Cocina moderna integrada"}},
            {{"tipo": "bano", "nombre": "Baño Principal", "m2": 6, "descripcion": "Baño completo"}},
            {{"tipo": "garage", "nombre": "Garage", "m2": 20, "descripcion": "Para 2 vehículos"}} (solo si con_garage=true)
        ],
        "metricas": {{
            "total_m2_construidos": 76,
            "m2_parcela_usados": 76,
            "eficiencia_parcela": 23,
            "presupuesto_estimado": 76000,
            "tiempo_construccion_meses": 8
        }},
        "validaciones": {{
            "cumple_normativa": true,
            "edificabilidad_ok": true,
            "presupuesto_ok": true,
            "observaciones": "Distribución óptima para familia de 4 personas"
        }}
    }}
    """

    try:
        respuesta_ia = get_ai_response(prompt)

        # Intentar parsear el JSON
        try:
            plan_json = json.loads(respuesta_ia)
            return plan_json
        except json.JSONDecodeError:
            # Si no es JSON válido, extraer el JSON del texto
            import re
            json_match = re.search(r'\{.*\}', respuesta_ia, re.DOTALL)
            if json_match:
                plan_json = json.loads(json_match.group())
                return plan_json
            else:
                # Fallback: crear plan básico
                return crear_plan_fallback(num_habitaciones, num_banos, con_garage, m2_construibles)

    except Exception as e:
        st.error(f"Error generando plan con IA: {e}")
        return crear_plan_fallback(num_habitaciones, num_banos, con_garage, m2_construibles)

def crear_plan_fallback(num_habitaciones, num_banos, con_garage, m2_max):
    """Plan básico de fallback cuando la IA falla"""
    distribucion = []

    # Salón básico
    distribucion.append({
        "tipo": "salon",
        "nombre": "Salón-Comedor",
        "m2": min(25, m2_max // 4),
        "descripcion": "Espacio principal"
    })

    # Cocina
    distribucion.append({
        "tipo": "cocina",
        "nombre": "Cocina",
        "m2": 10,
        "descripcion": "Cocina funcional"
    })

    # Dormitorios
    for i in range(num_habitaciones):
        distribucion.append({
            "tipo": "dormitorio",
            "nombre": f"Dormitorio {i+1}",
            "m2": 12 if i == 0 else 10,
            "descripcion": "Habitación cómoda" if i == 0 else "Habitación secundaria"
        })

    # Baños
    for i in range(num_banos):
        distribucion.append({
            "tipo": "bano",
            "nombre": f"Baño {i+1}",
            "m2": 6 if i == 0 else 4,
            "descripcion": "Baño completo" if i == 0 else "Baño secundario"
        })

    # Garage si aplica
    if con_garage:
        distribucion.append({
            "tipo": "garage",
            "nombre": "Garage",
            "m2": 20,
            "descripcion": "Para 2 vehículos"
        })

    total_m2 = sum(item['m2'] for item in distribucion)

    return {
        "distribucion": distribucion,
        "metricas": {
            "total_m2_construidos": total_m2,
            "m2_parcela_usados": total_m2,
            "eficiencia_parcela": round((total_m2 / 100) * 100, 1),  # Asumiendo parcela de 100m² para cálculo
            "presupuesto_estimado": total_m2 * 1000,
            "tiempo_construccion_meses": 6
        },
        "validaciones": {
            "cumple_normativa": total_m2 <= m2_max,
            "edificabilidad_ok": total_m2 <= m2_max,
            "presupuesto_ok": True,
            "observaciones": "Plan básico generado automáticamente"
        }
    }

def main():
    """Interfaz principal del Gemelo Digital"""
    st.title("🏠 Gemelo Digital Inteligente")
    st.markdown("""
    **Simula y optimiza tu proyecto arquitectónico con IA en tiempo real**

    Este gemelo digital analiza tu parcela y genera recomendaciones inteligentes
    para eficiencia energética, distribución óptima y sostenibilidad.
    """)
    st.markdown("---")

    # Puente inteligente con marketplace existente
    st.subheader("📍 Seleccionar Parcela Base")
    plots = list_published_plots()

    if not plots:
        st.warning("No hay parcelas disponibles en el marketplace. Primero registra algunas parcelas.")
        return

    plot_options = {f"{p['title']} ({p['surface_m2']} m² - {p.get('location', 'Ubicación no especificada')})": p
                   for p in plots}
    selected_plot_name = st.selectbox("Selecciona una parcela del marketplace:",
                                     list(plot_options.keys()),
                                     key="gemelo_plot_select")
    selected_plot = plot_options[selected_plot_name] if selected_plot_name else None

    if selected_plot:
        # Mostrar información de la parcela
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Superficie", f"{selected_plot['surface_m2']} m²")
            st.metric("Precio", f"€{selected_plot['price']}")
            st.write(f"**Urbana:** {'Sí' if selected_plot.get('is_urban') else 'No'}")
            if selected_plot.get('cadastral_ref'):
                st.write(f"**Referencia:** {selected_plot['cadastral_ref']}")

        with col2:
            # Placeholder para ubicación (podría integrar mapa real)
            st.info("📍 Ubicación de la parcela seleccionada")

        st.markdown("---")

        # 🎯 NUEVO: Generador Interactivo de Plan de Vivienda
        st.subheader("🏠 Diseña Tu Vivienda - Guía Paso a Paso")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.markdown("**📋 Especificaciones de tu hogar**")

            # Sliders interactivos para el diseño
            num_habitaciones = st.slider("Número de habitaciones", 1, 6, 3, key="num_hab")
            num_banos = st.slider("Número de baños", 1, 4, 2, key="num_banos")
            con_garage = st.checkbox("Incluir garage", value=True, key="con_garage")
            presupuesto_max = st.slider("Presupuesto máximo (€)", 50000, 500000, 150000, key="presupuesto")

            # Botón para generar plan
            if st.button("🚀 Generar Plan de Vivienda con IA", type="primary", key="generar_plan"):
                with st.spinner("🎨 Creando distribución óptima con IA..."):
                    plan_generado = generar_plan_vivienda(
                        selected_plot, num_habitaciones, num_banos,
                        con_garage, presupuesto_max
                    )
                    st.session_state['plan_vivienda'] = plan_generado
                    st.success("✅ Plan generado exitosamente!")

        with col2:
            # Mostrar plan generado si existe
            if 'plan_vivienda' in st.session_state:
                plan = st.session_state['plan_vivienda']

                if 'distribucion' in plan:
                    st.markdown("**📐 Distribución Generada**")

                    # Mostrar resumen
                    metricas = plan.get('metricas', {})
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Superficie Construida", f"{metricas.get('total_m2_construidos', 0)} m²")
                    with col_b:
                        st.metric("Presupuesto Estimado", f"€{metricas.get('presupuesto_estimado', 0):,}")
                    with col_c:
                        st.metric("Tiempo Construcción", f"{metricas.get('tiempo_construccion_meses', 0)} meses")

                    # Mostrar habitaciones en una tabla bonita
                    st.markdown("**🏠 Habitaciones del Plan**")
                    for hab in plan['distribucion']:
                        tipo_icon = {
                            'salon': '🛋️', 'dormitorio': '🛏️', 'cocina': '🍳',
                            'bano': '🚿', 'garage': '🚗'
                        }.get(hab['tipo'], '🏠')

                        st.markdown(f"{tipo_icon} **{hab['nombre']}** - {hab['m2']} m²")
                        if 'descripcion' in hab:
                            st.caption(hab['descripcion'])

                    # Validaciones
                    validaciones = plan.get('validaciones', {})
                    if validaciones.get('cumple_normativa'):
                        st.success("✅ Diseño cumple normativa urbanística")
                    else:
                        st.warning("⚠️ Revisar cumplimiento normativo")

                else:
                    st.error("Error en el formato del plan generado")
            else:
                st.info("👆 Configura tus preferencias y genera un plan personalizado")

        st.markdown("---")

        # Análisis del gemelo digital (existente)
        st.subheader("🎛️ Parámetros del Gemelo Digital")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**🌡️ Condiciones Ambientales**")
            temperatura = st.slider("Temperatura exterior (°C)", -10, 45, 20, key="temp_gemelo")
            humedad = st.slider("Humedad relativa (%)", 0, 100, 60, key="hum_gemelo")
            orientacion = st.selectbox("Orientación principal", ["Norte", "Sur", "Este", "Oeste"], key="ori_gemelo")

        with col2:
            st.markdown("**👥 Uso y Ocupación**")
            ocupacion = st.slider("Nº ocupantes", 1, 12, 4, key="ocup_gemelo")
            uso_principal = st.selectbox("Uso principal", ["Vivienda", "Oficina", "Comercial", "Mixto"], key="uso_gemelo")
            horario_uso = st.selectbox("Horario de uso", ["Diurno", "Nocturno", "24h", "Esporádico"], key="hora_gemelo")

        with col3:
            st.markdown("**🏗️ Características Constructivas**")
            eficiencia_objetivo = st.selectbox("Eficiencia energética objetivo",
                                             ["A+", "A", "B", "C", "D"], key="efic_gemelo")
            material_muros = st.selectbox("Material principal muros",
                                        ["Madera", "Ladrillo", "Hormigón", "Bloque"], key="mat_gemelo")
            sistema_clima = st.checkbox("Sistema climatización", key="clima_gemelo")
            paneles_solares = st.checkbox("Paneles solares", key="solar_gemelo")

        # Botón de análisis IA
        if st.button("🚀 Analizar Gemelo Digital con IA", type="primary", key="analizar_gemelo"):
            analizar_gemelo_digital(selected_plot, temperatura, humedad, orientacion,
                                  ocupacion, uso_principal, horario_uso, eficiencia_objetivo,
                                  material_muros, sistema_clima, paneles_solares)

        # Visualización 3D del gemelo
        st.markdown("---")
        st.subheader("🏗️ Visualización 3D del Gemelo Digital")
        plan_actual = st.session_state.get('plan_vivienda')
        fig = crear_visualizacion_gemelo(selected_plot, temperatura, ocupacion,
                                       material_muros, sistema_clima, paneles_solares, plan_actual)
        st.plotly_chart(fig, use_container_width=True)

        # Información adicional
        with st.expander("ℹ️ Acerca del Gemelo Digital"):
            st.markdown("""
            **¿Qué es un Gemelo Digital?**
            - Réplica virtual inteligente de tu proyecto
            - Se alimenta de datos reales y simulados
            - Permite análisis predictivo y optimización

            **Beneficios:**
            - ✅ Optimización energética antes de construir
            - ✅ Análisis de eficiencia y sostenibilidad
            - ✅ Simulación de diferentes escenarios
            - ✅ Recomendaciones basadas en IA

            **Próximas ampliaciones:**
            - Integración con sensores IoT reales
            - Análisis de ciclo de vida del edificio
            - Simulaciones climáticas avanzadas
            - Certificaciones energéticas automáticas
            """)

def analizar_gemelo_digital(plot, temp, hum, ori, ocup, uso, horario, efic, mat, clima, solar):
    """Análisis inteligente del gemelo digital usando IA"""

    # Crear prompt detallado para IA
    prompt = f"""
    ERES UN ARQUITECTO Y ENGENIERO ESPECIALISTA EN EFICIENCIA ENERGÉTICA.

    Analiza este GEMENO DIGITAL de proyecto arquitectónico:

    **DATOS DE LA PARCELA:**
    - Superficie: {plot['surface_m2']} m²
    - Ubicación: {plot.get('location', 'No especificada')}
    - Tipo: {'Urbana' if plot.get('is_urban') else 'Rústica'}
    - Precio: €{plot['price']}

    **CONDICIONES AMBIENTALES:**
    - Temperatura exterior: {temp}°C
    - Humedad relativa: {hum}%
    - Orientación principal: {ori}

    **USO Y OCUPACIÓN:**
    - Número de ocupantes: {ocup}
    - Uso principal: {uso}
    - Horario de uso: {horario}

    **CARACTERÍSTICAS CONSTRUCTIVAS:**
    - Eficiencia energética objetivo: {efic}
    - Material principal muros: {mat}
    - Sistema climatización: {'Sí' if clima else 'No'}
    - Paneles solares: {'Sí' if solar else 'No'}

    **ANÁLISIS REQUERIDO:**
    1. **EFICIENCIA ENERGÉTICA ESTIMADA**: Califica (A+, A, B, C, D) y justifica
    2. **CONSUMO ENERGÉTICO ANUAL**: Estima kWh/año y €/año aproximado
    3. **RECOMENDACIONES DE MEJORA**: 3-5 sugerencias concretas y prioritarias
    4. **IMPACTO AMBIENTAL**: Emisiones CO2 estimadas y comparación con estándar
    5. **OPTIMIZACIONES ARQUITECTÓNICAS**: Mejoras en distribución, orientación, materiales

    **FORMATO DE RESPUESTA:**
    - Usa viñetas y encabezados claros
    - Sé específico y cuantitativo cuando sea posible
    - Incluye cálculos aproximados basados en normativa española
    - Prioriza soluciones realistas y económicamente viables
    """

    with st.spinner("🤖 IA analizando el gemelo digital... Esto puede tomar unos segundos"):
        try:
            analisis = get_ai_response(prompt)

            # Mostrar resultados
            st.success("✅ Análisis completado exitosamente!")

            # Tabs para organizar resultados
            tab1, tab2, tab3 = st.tabs(["📊 Eficiencia Energética", "💡 Recomendaciones", "🌱 Impacto Ambiental"])

            with tab1:
                st.subheader("📊 Evaluación Energética")
                # Aquí podríamos extraer métricas específicas del análisis
                st.write(analisis)

            with tab2:
                st.subheader("💡 Recomendaciones de Optimización")
                st.info("Las recomendaciones específicas se incluyen en el análisis completo arriba.")

            with tab3:
                st.subheader("🌱 Impacto Ambiental")
                st.info("El análisis ambiental detallado está incluido arriba.")

            # Guardar análisis en session_state para posibles exportaciones
            st.session_state['gemelo_analisis'] = {
                'plot': plot,
                'parametros': {
                    'temperatura': temp, 'humedad': hum, 'orientacion': ori,
                    'ocupacion': ocup, 'uso': uso, 'horario': horario,
                    'eficiencia': efic, 'material': mat, 'clima': clima, 'solar': solar
                },
                'analisis_ia': analisis,
                'timestamp': str(st.session_state.get('timestamp', 'now'))
            }

        except Exception as e:
            st.error(f"❌ Error en el análisis IA: {str(e)}")
            st.info("Verifica que la API key de OpenRouter esté configurada correctamente.")

def crear_visualizacion_gemelo(plot, temp, ocup, mat, clima, solar, plan_vivienda=None):
    """Crea visualización 3D dinámica del gemelo digital con habitaciones individuales"""

    fig = go.Figure()

    # Dimensiones base adaptadas a la parcela
    superficie = plot['surface_m2']
    lado = (superficie ** 0.5) * 0.8  # Aproximación cuadrada con factor de edificabilidad

    # Base de la parcela
    fig.add_trace(go.Mesh3d(
        x=[0, lado, lado, 0],
        y=[0, 0, lado, lado],
        z=[0, 0, 0, 0],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color='lightgreen',
        name='Parcela',
        opacity=0.3
    ))

    if plan_vivienda and 'distribucion' in plan_vivienda:
        # Visualización avanzada con habitaciones del plan
        habitaciones = plan_vivienda['distribucion']

        # Colores por tipo de habitación
        colores_por_tipo = {
            'salon': 'lightblue',
            'dormitorio': 'lightcoral',
            'cocina': 'orange',
            'bano': 'lightcyan',
            'garage': 'gray',
            'terraza': 'green',
            'pasillo': 'beige'
        }

        # Calcular posiciones y tamaños
        total_m2 = sum(h['m2'] for h in habitaciones if h['tipo'] != 'garage')
        lado_edificio = min(lado * 0.8, (total_m2 ** 0.5) * 1.2)

        # Posicionar habitaciones en una distribución lógica
        habitaciones_posicionadas = posicionar_habitaciones(habitaciones, lado_edificio)

        for hab in habitaciones_posicionadas:
            tipo = hab['tipo']
            color = colores_por_tipo.get(tipo, 'lightgray')

            # Crear cubo para cada habitación
            x0, y0 = hab['pos_x'], hab['pos_y']
            ancho, largo = hab['ancho'], hab['largo']
            altura = 3  # Altura estándar

            # Vertices del cubo
            x = [x0, x0+ancho, x0+ancho, x0, x0, x0+ancho, x0+ancho, x0]
            y = [y0, y0, y0+largo, y0+largo, y0, y0, y0+largo, y0+largo]
            z = [0, 0, 0, 0, altura, altura, altura, altura]

            fig.add_trace(go.Mesh3d(
                x=x, y=y, z=z,
                i=[0, 0, 0, 1, 4, 4, 2, 6, 4, 0, 3, 7],
                j=[1, 2, 3, 2, 5, 6, 6, 5, 1, 5, 2, 6],
                k=[2, 3, 0, 3, 6, 7, 3, 2, 6, 1, 6, 2],
                color=color,
                name=f"{hab['nombre']} ({hab['m2']}m²)",
                opacity=0.8,
                hovertext=f"{hab['nombre']}<br>{hab['m2']} m²<br>{hab.get('descripcion', '')}"
            ))

            # Añadir etiqueta de texto
            fig.add_trace(go.Scatter3d(
                x=[x0 + ancho/2],
                y=[y0 + largo/2],
                z=[altura + 0.5],
                mode='text',
                text=[hab['nombre']],
                textposition="middle center",
                showlegend=False
            ))

    else:
        # Visualización básica anterior (cuando no hay plan detallado)
        altura_base = 3  # Altura por planta
    plantas = max(1, min(3, ocup // 2))  # Estimación de plantas basada en ocupación
    altura_total = plantas * altura_base

    # Color adaptado al material
    colores_material = {
        'Madera': 'saddlebrown',
        'Ladrillo': 'firebrick',
        'Hormigón': 'gray',
        'Bloque': 'lightgray'
    }
    color_edificio = colores_material.get(mat, 'lightblue')

    # Estructura del edificio
    ancho_edificio = lado * 0.6
    largo_edificio = lado * 0.7

    fig.add_trace(go.Mesh3d(
        x=[lado*0.2, lado*0.2+ancho_edificio, lado*0.2+ancho_edificio, lado*0.2,
           lado*0.2, lado*0.2+ancho_edificio, lado*0.2+ancho_edificio, lado*0.2],
        y=[lado*0.15, lado*0.15, lado*0.15+largo_edificio, lado*0.15+largo_edificio,
           lado*0.15, lado*0.15, lado*0.15+largo_edificio, lado*0.15+largo_edificio],
        z=[0, 0, 0, 0, altura_total, altura_total, altura_total, altura_total],
        i=[0, 0, 0, 1, 4, 4, 2, 6, 4, 0, 3, 7],
        j=[1, 2, 3, 2, 5, 6, 6, 5, 1, 5, 2, 6],
        k=[2, 3, 0, 3, 6, 7, 3, 2, 5, 1, 6, 2],
        color=color_edificio,
        name=f'Edificio ({plantas} plantas)',
        opacity=0.8
    ))

    # Indicadores dinámicos
    indicadores = []

    # Temperatura
    color_temp = 'blue' if temp < 15 else 'red' if temp > 25 else 'orange'
    indicadores.append({
        'x': [lado*0.5], 'y': [lado*0.5], 'z': [altura_total + 1],
        'text': [f'🌡️ {temp}°C'],
        'color': color_temp
    })

    # Sistema climatización
    if clima:
        indicadores.append({
            'x': [lado*0.3], 'y': [lado*0.8], 'z': [altura_total + 0.5],
            'text': ['❄️ Climatización'],
            'color': 'lightblue'
        })

    # Paneles solares
    if solar:
        # Representar paneles en el techo
        fig.add_trace(go.Mesh3d(
            x=[lado*0.25, lado*0.75, lado*0.75, lado*0.25],
            y=[lado*0.2, lado*0.2, lado*0.3, lado*0.3],
            z=[altura_total, altura_total, altura_total, altura_total],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color='darkblue',
            name='Paneles Solares',
            opacity=0.9
        ))

    # Añadir indicadores
    for ind in indicadores:
        fig.add_trace(go.Scatter3d(
            x=ind['x'], y=ind['y'], z=ind['z'],
            mode='markers+text',
            text=ind['text'],
            textposition="top center",
            marker=dict(size=8, color=ind['color'])
        ))

    # Configuración de la escena
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Ancho (m)', autorange=True),
            yaxis=dict(title='Largo (m)', autorange=True),
            zaxis=dict(title='Altura (m)', autorange=True),
            aspectmode='data'
        ),
        title=f"Gemelo Digital - {plot['title']} ({superficie} m²)",
        height=600,
        showlegend=True
    )

    # Añadir controles de ayuda
    fig.update_layout(
        scene=dict(
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
        )
    )

    return fig

def posicionar_habitaciones(habitaciones, lado_edificio):
    """Posiciona habitaciones en el plano de forma lógica"""
    habitaciones_posicionadas = []
    x_actual = 0
    y_actual = 0
    fila_altura = 0

    for hab in habitaciones:
        m2 = hab['m2']
        lado_cuadrado = m2 ** 0.5  # Aproximación cuadrada

        # Si no cabe en la fila actual, pasar a nueva fila
        if x_actual + lado_cuadrado > lado_edificio:
            x_actual = 0
            y_actual += fila_altura
            fila_altura = lado_cuadrado

        hab_pos = hab.copy()
        hab_pos.update({
            'pos_x': x_actual,
            'pos_y': y_actual,
            'ancho': lado_cuadrado,
            'largo': lado_cuadrado
        })

        habitaciones_posicionadas.append(hab_pos)
        x_actual += lado_cuadrado
        fila_altura = max(fila_altura, lado_cuadrado)

    return habitaciones_posicionadas