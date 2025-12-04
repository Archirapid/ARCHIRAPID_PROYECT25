"""
Streamlit design utilities for ARCHIRAPID
"""

import streamlit as st
import json
from pathlib import Path
from modules.marketplace.utils import list_published_plots

def main():
    st.title("🏗️ Design Assistant")
    st.markdown("Herramienta de diseño asistido por IA para generar planos arquitectónicos basados en parcelas urbanas.")

    # Paso 1: Seleccionar Parcela
    st.header("1. 📍 Seleccionar Parcela")
    plots = list_published_plots()
    plot_options = {f"{p['title']} ({p['surface_m2']} m²)": p for p in plots}
    selected_plot_name = st.selectbox("Elige una parcela del marketplace:", list(plot_options.keys()))
    selected_plot = plot_options[selected_plot_name] if selected_plot_name else None

    if selected_plot:
        st.success(f"Parcela seleccionada: {selected_plot['title']}")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Superficie:** {selected_plot['surface_m2']} m²")
            st.write(f"**Precio:** €{selected_plot['price']}")
        with col2:
            st.write(f"**Urbana:** {'Sí' if selected_plot.get('is_urban') else 'No'}")
            st.write(f"**Referencia:** {selected_plot.get('cadastral_ref', 'N/A')}")

        # Paso 2: Análisis de Edificabilidad
        st.header("2. 🔍 Análisis de Edificabilidad")
        if st.button("Calcular Edificabilidad"):
            with st.spinner("Analizando parcela..."):
                # Simular cálculo basado en superficie
                surface = selected_plot['surface_m2']
                edificability = {
                    "superficie_parcela": surface,
                    "edificabilidad_maxima": surface * 0.8,  # 80% aproximado
                    "coeficiente_edificabilidad": 0.8,
                    "altura_maxima": 3,  # plantas
                    "tipo_suelo": "Urbano",
                    "recomendaciones": "Ideal para vivienda unifamiliar"
                }
                st.session_state['edificability'] = edificability
                st.success("Análisis completado!")
                st.json(edificability)

        # Paso 3: Parámetros de Diseño
        st.header("3. 🏠 Parámetros de Diseño")
        col1, col2, col3 = st.columns(3)
        with col1:
            tipo_vivienda = st.selectbox("Tipo de Vivienda", ["Unifamiliar", "Adosada", "Piso", "Chalet"])
        with col2:
            habitaciones = st.slider("Habitaciones", 1, 6, 3)
        with col3:
            banos = st.slider("Baños", 1, 4, 2)

        plantas = st.slider("Número de Plantas", 1, 3, 1)
        garaje = st.checkbox("Incluir Garaje")
        jardin = st.checkbox("Incluir Jardín")

        # Paso 4: Generar Plano
        st.header("4. 🎨 Generar Plano Arquitectónico")
        if st.button("Generar Plano con IA", type="primary"):
            with st.spinner("Generando plano con IA..."):
                # Simular generación de plano
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
                st.success("Plano generado exitosamente!")

        # Mostrar Plano
        if 'plano' in st.session_state:
            st.header("5. 📐 Plano Generado")
            plano = st.session_state['plano']
            st.subheader(f"Plano para {plano['tipo']}")
            st.write(f"**Superficie Construida:** {plano['superficie_construida']} m²")
            st.write(f"**Plantas:** {plano['plantas']}")
            st.write(f"**Habitaciones:** {plano['habitaciones']}, **Baños:** {plano['banos']}")
            if plano['garaje']:
                st.write("✅ Incluye Garaje")
            if plano['jardin']:
                st.write("✅ Incluye Jardín")

            # Simular visualización de plano
            st.image("https://via.placeholder.com/600x400/4CAF50/FFFFFF?text=Plano+Arquitectonico", caption="Vista preliminar del plano")

            # Opciones finales
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("💾 Guardar Plano"):
                    st.success("Plano guardado en tu cuenta!")
            with col2:
                if st.button("📥 Descargar PDF"):
                    st.info("Descarga PDF - Funcionalidad en desarrollo")
            with col3:
                if st.button("📧 Enviar a Arquitecto"):
                    st.info("Enviar a arquitecto registrado - Próximamente")

    else:
        st.info("Selecciona una parcela para comenzar el diseño.")

    st.markdown("---")
    st.caption("Design Assistant v1.0 - Funcionalidad en desarrollo. Próximamente: IA real, renderizados 3D, integración con AutoCAD.")