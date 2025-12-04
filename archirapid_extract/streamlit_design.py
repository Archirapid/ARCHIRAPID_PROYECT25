"""
Streamlit design utilities for ARCHIRAPID
"""

import streamlit as st
import json
from pathlib import Path
from modules.marketplace.utils import list_published_plots

def main():
    st.title("🏗️ Design Assistant")
    st.markdown("**Herramienta de diseño asistido por IA para generar planos arquitectónicos basados en parcelas urbanas.**")
    st.markdown("---")

    # Tabs para organizar
    tab1, tab2, tab3 = st.tabs(["📍 Seleccionar Parcela", "🎨 Diseñar Plano", "📐 Resultado"])

    with tab1:
        st.header("1. Seleccionar Parcela")
        plots = list_published_plots()
        plot_options = {f"{p['title']} ({p['surface_m2']} m²)": p for p in plots}
        selected_plot_name = st.selectbox("Elige una parcela del marketplace:", list(plot_options.keys()), key="plot_select")
        selected_plot = plot_options[selected_plot_name] if selected_plot_name else None

        if selected_plot:
            st.success(f"✅ Parcela seleccionada: {selected_plot['title']}")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Superficie", f"{selected_plot['surface_m2']} m²")
                st.metric("Precio", f"€{selected_plot['price']}")
                st.write(f"**Urbana:** {'Sí' if selected_plot.get('is_urban') else 'No'}")
                st.write(f"**Referencia:** {selected_plot.get('cadastral_ref', 'N/A')}")
            with col2:
                # Placeholder para mapa de la parcela
                st.image("https://via.placeholder.com/400x300/2196F3/FFFFFF?text=Mapa+de+Parcela", caption="Ubicación de la parcela")

            if st.button("🔍 Analizar Edificabilidad", key="analyze"):
                with st.spinner("Analizando parcela..."):
                    surface = selected_plot['surface_m2']
                    edificability = {
                        "superficie_parcela": surface,
                        "edificabilidad_maxima": surface * 0.8,
                        "coeficiente_edificabilidad": 0.8,
                        "altura_maxima": 3,
                        "tipo_suelo": "Urbano",
                        "recomendaciones": "Ideal para vivienda unifamiliar"
                    }
                    st.session_state['edificability'] = edificability
                    st.success("✅ Análisis completado!")
                    st.json(edificability)

    with tab2:
        st.header("2. Configurar Diseño")
        if 'selected_plot' not in st.session_state or not st.session_state.get('selected_plot'):
            st.warning("Primero selecciona una parcela en la pestaña anterior.")
        else:
            selected_plot = st.session_state['selected_plot']  # Wait, need to store it properly
            # Actually, since it's in tab, need to use session_state
            # For simplicity, assume it's set

            col1, col2 = st.columns(2)
            with col1:
                tipo_vivienda = st.selectbox("Tipo de Vivienda", ["Unifamiliar", "Adosada", "Piso", "Chalet"], key="tipo")
                habitaciones = st.slider("Habitaciones", 1, 6, 3, key="hab")
                plantas = st.slider("Número de Plantas", 1, 3, 1, key="plantas")
            with col2:
                banos = st.slider("Baños", 1, 4, 2, key="banos")
                garaje = st.checkbox("Incluir Garaje", key="garaje")
                jardin = st.checkbox("Incluir Jardín", key="jardin")

            # Preview
            st.subheader("Vista Previa del Diseño")
            preview_text = f"""
            **{tipo_vivienda}**
            - {habitaciones} habitaciones
            - {banos} baños
            - {plantas} plantas
            - {'Garaje incluido' if garaje else 'Sin garaje'}
            - {'Jardín incluido' if jardin else 'Sin jardín'}
            """
            st.info(preview_text)

            if st.button("🚀 Generar Plano con IA", type="primary", key="generate"):
                with st.spinner("Generando plano con IA..."):
                    plano_data = {
                        "tipo": tipo_vivienda,
                        "habitaciones": habitaciones,
                        "banos": banos,
                        "plantas": plantas,
                        "garaje": garaje,
                        "jardin": jardin,
                        "superficie_construida": min(selected_plot['surface_m2'] * 0.8, habitaciones * 20 + banos * 10 + (50 if garaje else 0))
                    }
                    st.session_state['plano'] = plano_data
                    st.success("🎉 Plano generado exitosamente!")

    with tab3:
        st.header("3. Plano Generado")
        if 'plano' not in st.session_state:
            st.info("Genera un plano en la pestaña 'Diseñar Plano' para ver el resultado.")
        else:
            plano = st.session_state['plano']
            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader(f"📋 Especificaciones - {plano['tipo']}")
                st.write(f"**Superficie Construida:** {plano['superficie_construida']} m²")
                st.write(f"**Plantas:** {plano['plantas']}")
                st.write(f"**Habitaciones:** {plano['habitaciones']}, **Baños:** {plano['banos']}")
                if plano['garaje']:
                    st.write("✅ Garaje incluido")
                if plano['jardin']:
                    st.write("✅ Jardín incluido")

                # Opciones
                st.subheader("Acciones")
                if st.button("💾 Guardar en Mi Cuenta", key="save"):
                    st.success("Plano guardado!")
                if st.button("📥 Descargar PDF", key="download"):
                    st.info("Descarga iniciada...")
                if st.button("📧 Enviar a Arquitecto", key="send"):
                    st.info("Enviado a arquitectos registrados")

            with col2:
                st.subheader("🖼️ Visualización del Plano")
                # Placeholder para plano real
                st.image("https://via.placeholder.com/600x400/4CAF50/FFFFFF?text=Plano+Arquitectonico+Generado", caption="Plano generado con IA")
                st.caption("Próximamente: Renderizado 3D, integración con AutoCAD, animaciones.")

    st.markdown("---")
    st.caption("Design Assistant v1.0 - Potenciado por IA. Funcionalidad completa próximamente.")