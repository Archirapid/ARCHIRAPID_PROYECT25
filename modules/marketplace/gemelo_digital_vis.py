# modules/marketplace/gemelo_digital_vis.py

import plotly.graph_objects as go
import random
import streamlit as st
from modules.marketplace.data_access import get_proyecto

def create_gemelo_3d(plan_json: dict):
    """
    Renderiza un modelo 3D básico de la vivienda a partir del JSON de la IA.
    - Centra los cubos en la parcela.
    - Escala visualmente los cubos para que se vean proporcionados.
    - Superpone los cubos sobre el plano base de la parcela.
    """
    fig = go.Figure()

    # ✅ Coordenadas base de la parcela (simulada como cuadrado de 100x100 m)
    parcela_x = [10, 90, 90, 10, 10]
    parcela_y = [10, 10, 90, 90, 10]
    parcela_z = [0] * len(parcela_x)

    fig.add_trace(go.Scatter3d(
        x=parcela_x,
        y=parcela_y,
        z=parcela_z,
        mode="lines",
        line=dict(color="brown", width=4),
        name="Parcela"
    ))

    # ✅ Centro de la parcela
    centro_x = 50
    centro_y = 50

    # ✅ Escala visual para que los cubos se vean bien
    escala_visual = 2.5

    # ✅ Posición inicial relativa al centro
    offset_x = -20
    offset_y = -20

    colores = ["lightblue", "lightgreen", "lightpink", "lightyellow", "lavender", "beige", "lightgray"]

    # ✅ Dibujar habitaciones
    if "habitaciones" in plan_json:
        for idx, hab in enumerate(plan_json["habitaciones"]):
            nombre = hab.get("nombre", f"Habitación {idx+1}")
            m2 = hab.get("m2", 10)

            lado = int((m2) ** 0.5) * escala_visual
            altura = 3

            x0 = centro_x + offset_x
            x1 = x0 + lado
            y0 = centro_y + offset_y
            y1 = y0 + lado
            z0, z1 = 0, altura

            fig.add_trace(go.Mesh3d(
                x=[x0, x1, x1, x0, x0, x1, x1, x0],
                y=[y0, y0, y1, y1, y0, y0, y1, y1],
                z=[z0, z0, z0, z0, z1, z1, z1, z1],
                i=[0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 4, 5],
                j=[1, 2, 3, 5, 6, 7, 5, 6, 7, 6, 0, 1],
                k=[2, 3, 0, 6, 7, 4, 6, 7, 4, 7, 5, 2],
                opacity=0.5,
                color=random.choice(colores),
                name=nombre
            ))

            fig.add_trace(go.Scatter3d(
                x=[(x0+x1)/2], y=[(y0+y1)/2], z=[altura+0.5],
                mode="text",
                text=[f"{nombre} ({m2} m²)"],
                textposition="top center"
            ))

            offset_x += lado + 5  # Separación entre cubos

    # ✅ Dibujar garage si existe
    if "garage" in plan_json:
        m2 = plan_json["garage"].get("m2", 20)
        lado = int((m2) ** 0.5) * escala_visual
        altura = 3

        x0 = centro_x + offset_x
        x1 = x0 + lado
        y0 = centro_y + offset_y
        y1 = y0 + lado
        z0, z1 = 0, altura

        fig.add_trace(go.Mesh3d(
            x=[x0, x1, x1, x0, x0, x1, x1, x0],
            y=[y0, y0, y1, y1, y0, y0, y1, y1],
            z=[z0, z0, z0, z0, z1, z1, z1, z1],
            i=[0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 4, 5],
            j=[1, 2, 3, 5, 6, 7, 5, 6, 7, 6, 0, 1],
            k=[2, 3, 0, 6, 7, 4, 6, 7, 4, 7, 5, 2],
            opacity=0.5,
            color="gray",
            name="Garage"
        ))

        fig.add_trace(go.Scatter3d(
            x=[(x0+x1)/2], y=[(y0+y1)/2], z=[altura+0.5],
            mode="text",
            text=[f"Garage ({m2} m²)"],
            textposition="top center"
        ))

    fig.update_layout(scene=dict(
        xaxis_title="Ancho (m)",
        yaxis_title="Largo (m)",
        zaxis_title="Altura (m)"
    ))

    return fig


def mostrar_visualizacion_3d():
    """
    Función segura para mostrar la visualización 3D del proyecto vigente.
    Verifica que exista un proyecto activo antes de renderizar.
    """
    st.subheader("🌐 Visualización 3D del proyecto vigente")

    proyecto_id = st.session_state.get("proyecto_id")
    plan_json = st.session_state.get("plan_json")

    if not proyecto_id or not plan_json:
        st.info("ℹ️ No hay proyecto vigente. Genera o selecciona un plan primero.")
        return

    # Recuperar proyecto guardado (última versión)
    proyecto = get_proyecto(proyecto_id)
    if not proyecto:
        st.error("❌ Proyecto no encontrado en base de datos.")
        return

    # Renderizar malla 3D con el plan vigente
    try:
        fig = create_gemelo_3d(plan_json)
        st.plotly_chart(fig, use_container_width=True)

        # Mostrar información de la versión
        version = proyecto.get('version', st.session_state.get('version', 'N/D'))
        st.caption(f"📋 Proyecto ID: {proyecto_id} • Versión: {version}")

    except Exception as e:
        st.warning(f"⚠️ Error en visualización 3D: {e}")
        st.info("💡 Intenta regenerar el plan si el problema persiste.")