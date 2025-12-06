"""
Streamlit design utilities for ARCHIRAPID
"""

import streamlit as st
import json
from pathlib import Path
from modules.marketplace.utils import list_published_plots
from archirapid_extract.extract_pdf import extract_pdf_data

def main():
    st.write("Design Assistant loaded")  # debug
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

            # Extracción de datos del PDF
            if selected_plot.get('registry_note_path'):
                if st.button("🔍 Extraer Datos de la Nota Simple", key="extract"):
                    with st.spinner("Extrayendo datos del PDF..."):
                        extracted = extract_pdf_data(selected_plot['registry_note_path'])
                        if 'error' not in extracted:
                            st.session_state['extracted_data'] = extracted
                            st.success("✅ Datos extraídos exitosamente!")
                            st.json(extracted)
                        else:
                            st.error(f"Error en extracción: {extracted['error']}")
            else:
                st.warning("No hay PDF de nota simple asociado a esta finca.")

            if st.button("📊 Analizar Edificabilidad", key="analyze"):
                extracted = st.session_state.get('extracted_data', {})
                surface = extracted.get('surface_m2', selected_plot['surface_m2'])
                buildable = extracted.get('buildable_m2', surface * 0.8)
                edificability = {
                    "superficie_parcela": surface,
                    "edificabilidad_maxima": buildable,
                    "coeficiente_edificabilidad": buildable / surface if surface else 0.8,
                    "altura_maxima": 3,
                    "tipo_suelo": "Urbano" if extracted.get('is_urban', True) else "Rústico",
                    "recomendaciones": "Basado en datos extraídos del catastro"
                }
                st.session_state['edificability'] = edificability
                st.success("✅ Análisis completado!")
                st.json(edificability)

            # Store in session_state
            st.session_state['design_selected_plot'] = selected_plot

    with tab2:
        st.header("2. Configurar Diseño")
        selected_plot = st.session_state.get('design_selected_plot')
        if not selected_plot:
            st.warning("Primero selecciona una parcela en la pestaña anterior.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                extracted = st.session_state.get('extracted_data', {})
                max_hab = int((extracted.get('surface_m2', selected_plot['surface_m2']) / 20)) or 6
                tipo_vivienda = st.selectbox("Tipo de Vivienda", ["Unifamiliar", "Adosada", "Piso", "Chalet"], key="tipo")
                habitaciones = st.slider("Habitaciones", 1, max_hab, min(3, max_hab), key="hab")
                plantas = st.slider("Número de Plantas", 1, 3, 1, key="plantas")
            with col2:
                max_banos = habitaciones + 1
                banos = st.slider("Baños", 1, max_banos, min(2, max_banos), key="banos")
                garaje = st.checkbox("Incluir Garaje", key="garaje")
                jardin = st.checkbox("Incluir Jardín", key="jardin")

            # Selector de normas técnicas (IA guiada)
            st.subheader("📏 Normas Técnicas (Guiado por IA)")
            normas = st.selectbox("Selecciona normativa aplicable", ["CTE (España)", "Eurocódigo", "Normas Locales Portuguesas", "Personalizado"], key="normas")
            if normas == "CTE (España)":
                st.info("IA sugiere: Edificabilidad máxima 0.8, altura limitada a 3 plantas.")
            elif normas == "Eurocódigo":
                st.info("IA sugiere: Considerar cargas sísmicas, edificabilidad 0.7.")
            else:
                st.info("IA: Ajusta según normativa local.")

            # Preview
            st.subheader("Vista Previa del Diseño")
            preview_text = f"""
            **{tipo_vivienda}**
            - {habitaciones} habitaciones
            - {banos} baños
            - {plantas} plantas
            - {'Garaje incluido' if garaje else 'Sin garaje'}
            - {'Jardín incluido' if jardin else 'Sin jardín'}
            - Normativa: {normas}
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
                        "superficie_construida": min((selected_plot.get('surface_m2', 0) if isinstance(selected_plot, dict) else 0) * 0.8, habitaciones * 20 + banos * 10 + (50 if garaje else 0))
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

                # Gráfico de superficie
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots()
                parcel_surface = selected_plot.get('surface_m2', 100)
                built_surface = plano['superficie_construida']
                ax.bar(['Parcela', 'Construido'], [parcel_surface, built_surface], color=['blue', 'green'])
                ax.set_ylabel('Superficie (m²)')
                ax.set_title('Malla de Superficies')
                st.pyplot(fig)

                # Plano simple (mock con habitaciones)
                st.subheader("🏠 Plano Básico Generado")
                fig2, ax2 = plt.subplots()
                # Dibujar rectángulos para habitaciones (ejemplo)
                ax2.add_patch(plt.Rectangle((0, 0), 5, 4, fill=True, color='lightblue', label='Habitación 1'))
                ax2.add_patch(plt.Rectangle((5, 0), 3, 4, fill=True, color='lightgreen', label='Baño'))
                ax2.add_patch(plt.Rectangle((0, 4), 8, 3, fill=True, color='lightcoral', label='Sala'))
                ax2.text(2.5, 2, 'Hab 1', ha='center')
                ax2.text(6.5, 2, 'Baño', ha='center')
                ax2.text(4, 5.5, 'Sala', ha='center')
                ax2.set_xlim(0, 8)
                ax2.set_ylim(0, 7)
                ax2.set_title('Plano 2D Básico (Editable con IA próximamente)')
                ax2.legend()
                st.pyplot(fig2)
                st.caption("IA: Puedes mover habitaciones arrastrando (próximamente). Sugerencias: Optimiza para luz natural.")

    st.markdown("---")
    st.caption("Design Assistant v1.0 - Potenciado por IA. Funcionalidad completa próximamente.")