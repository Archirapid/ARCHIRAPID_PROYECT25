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

        # Parámetros dinámicos del gemelo digital
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
        fig = crear_visualizacion_gemelo(selected_plot, temperatura, ocupacion,
                                       material_muros, sistema_clima, paneles_solares)
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

def crear_visualizacion_gemelo(plot, temp, ocup, mat, clima, solar):
    """Crea visualización 3D dinámica del gemelo digital"""

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

    # Edificio principal (adaptado a parámetros)
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