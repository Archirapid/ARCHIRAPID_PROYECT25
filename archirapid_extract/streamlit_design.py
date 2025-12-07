"""
Streamlit design utilities for ARCHIRAPID
"""

import streamlit as st
import json
from pathlib import Path
from modules.marketplace.utils import list_published_plots
from archirapid_extract.extract_pdf import extract_pdf_data
import matplotlib.pyplot as plt
import numpy as np
from streamlit_drawable_canvas import st_canvas
import plotly.graph_objects as go

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
        selected_plot_name = st.selectbox("Elige una parcela del marketplace:", list(plot_options.keys()), key="design_plot_select")
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

            # Interactive 2D Canvas
            st.markdown("---")
            canvas_result = interactive_2d_canvas()

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

                # 3D Visualization
                st.markdown("---")
                generate_3d_visualization(plano, selected_plot)

    st.markdown("---")
    st.caption("Design Assistant v1.0 - Potenciado por IA. Funcionalidad completa próximamente.")


def interactive_2d_canvas():
    """Interactive 2D canvas for drawing floor plans"""
    st.subheader("🎨 Lienzo Interactivo 2D")
    st.markdown("Dibuja tu plano de planta directamente en el lienzo. Usa las herramientas para crear habitaciones, paredes y elementos.")

    # Canvas configuration
    stroke_width = st.slider("Grosor del trazo", 1, 25, 3)
    stroke_color = st.color_picker("Color del trazo", "#000000")
    bg_color = st.color_picker("Color de fondo", "#FFFFFF")
    drawing_mode = st.selectbox(
        "Modo de dibujo:",
        ("freedraw", "line", "rect", "circle", "transform"),
        key="drawing_mode"
    )

    # Create canvas
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        height=400,
        width=600,
        drawing_mode=drawing_mode,
        key="canvas",
    )

    if canvas_result.image_data is not None:
        st.session_state['canvas_image'] = canvas_result.image_data

    # Tools and templates
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Limpiar Lienzo"):
            st.rerun()
        if st.button("📐 Plantilla Básica"):
            st.info("Próximamente: Carga plantillas predefinidas")

    with col2:
        if st.button("💾 Guardar Dibujo"):
            if 'canvas_image' in st.session_state:
                st.success("Dibujo guardado en sesión!")
            else:
                st.warning("No hay dibujo para guardar")

    return canvas_result


def generate_3d_visualization(plano_data, selected_plot):
    """Generate 3D visualization using Plotly"""
    st.subheader("🏗️ Visualización 3D Interactiva")

    if not plano_data:
        st.info("Genera un plano primero para ver la visualización 3D.")
        return

    # Create 3D building model based on plano data
    floors = plano_data.get('plantas', 1)
    rooms = plano_data.get('habitaciones', 3)
    bathrooms = plano_data.get('banos', 2)
    has_garage = plano_data.get('garaje', False)
    has_garden = plano_data.get('jardin', False)

    # Base dimensions
    base_width = 10
    base_length = 12
    floor_height = 3

    # Create figure
    fig = go.Figure()

    # Ground floor
    fig.add_trace(go.Mesh3d(
        x=[0, base_width, base_width, 0, 0, base_width, base_width, 0],
        y=[0, 0, base_length, base_length, 0, 0, base_length, base_length],
        z=[0, 0, 0, 0, floor_height, floor_height, floor_height, floor_height],
        i=[0, 0, 0, 1],
        j=[1, 2, 3, 2],
        k=[2, 3, 0, 3],
        color='lightblue',
        name='Planta Baja'
    ))

    # Upper floors
    for floor in range(1, floors):
        z_base = floor * floor_height
        fig.add_trace(go.Mesh3d(
            x=[0, base_width, base_width, 0, 0, base_width, base_width, 0],
            y=[0, 0, base_length, base_length, 0, 0, base_length, base_length],
            z=[z_base, z_base, z_base, z_base, z_base + floor_height, z_base + floor_height, z_base + floor_height, z_base + floor_height],
            i=[0, 0, 0, 1],
            j=[1, 2, 3, 2],
            k=[2, 3, 0, 3],
            color='lightgray',
            name=f'Planta {floor + 1}'
        ))

    # Roof
    if floors > 1:
        z_roof = floors * floor_height
        fig.add_trace(go.Mesh3d(
            x=[-1, base_width + 1, base_width + 1, -1],
            y=[-1, -1, base_length + 1, base_length + 1],
            z=[z_roof, z_roof, z_roof, z_roof],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='brown',
            name='Tejado'
        ))

    # Add garage if selected
    if has_garage:
        fig.add_trace(go.Mesh3d(
            x=[base_width, base_width + 4, base_width + 4, base_width, base_width, base_width + 4, base_width + 4, base_width],
            y=[0, 0, 3, 3, 0, 0, 3, 3],
            z=[0, 0, 0, 0, 2.5, 2.5, 2.5, 2.5],
            i=[0, 0, 0, 1],
            j=[1, 2, 3, 2],
            k=[2, 3, 0, 3],
            color='gray',
            name='Garaje'
        ))

    # Add garden area
    if has_garden:
        fig.add_trace(go.Mesh3d(
            x=[-5, base_width + 5, base_width + 5, -5],
            y=[-5, -5, base_length + 5, base_length + 5],
            z=[-0.1, -0.1, -0.1, -0.1],
            i=[0, 0],
            j=[1, 2],
            k=[2, 3],
            color='green',
            name='Jardín'
        ))

    # Update layout for better visualization
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Ancho (m)'),
            yaxis=dict(title='Largo (m)'),
            zaxis=dict(title='Altura (m)'),
            aspectmode='data'
        ),
        title="Modelo 3D del Proyecto",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)

    # Controls info
    st.markdown("""
    **Controles 3D:**
    - **Rotar:** Click y arrastra
    - **Zoom:** Scroll del mouse
    - **Pan:** Click derecho y arrastra
    """)