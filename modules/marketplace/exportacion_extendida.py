# modules/marketplace/exportacion_extendida.py

from modules.marketplace.documentacion import generar_memoria_constructiva
import streamlit as st

def generar_pdf_memoria(plan_json, superficie_finca, ubicacion):
    """
    Genera un PDF con la memoria constructiva extendida del proyecto.
    Usa la función existente generar_memoria_constructiva y la formatea como PDF.

    Args:
        plan_json: Plan de vivienda con habitaciones y garage
        superficie_finca: Superficie total de la finca en m²
        ubicacion: Ubicación geográfica de la finca

    Returns:
        bytes: Contenido del PDF para descarga
    """
    # Generar texto de memoria usando función existente
    memoria_texto = generar_memoria_constructiva(plan_json, superficie_finca)

    # Agregar información extendida
    memoria_extendida = f"""
MEMORIA CONSTRUCTIVA EXTENDIDA - ARCHIRAPID
==========================================

UBICACIÓN: {ubicacion or 'No especificada'}

{memoria_texto}

DETALLES ADICIONALES:
- Proyecto generado con IA
- Versión: {st.session_state.get('version', 'N/D')}
- Fecha de generación: {st.session_state.get('fecha_generacion', 'Actual')}

NOTA: Esta memoria es generada automáticamente y debe ser revisada por un arquitecto colegiado.
"""

    # Convertir a bytes (simulación de PDF - en producción usar reportlab o similar)
    return memoria_extendida.encode('utf-8')


def bloque_exportacion():
    """
    Bloque unificado de exportación que incluye PDF y CAD.
    Verifica que exista un proyecto activo antes de permitir descargas.
    """
    st.subheader("📄 Exportación del proyecto vigente")

    proyecto_id = st.session_state.get("proyecto_id")
    plan_json = st.session_state.get("plan_json")
    finca_id = st.session_state.get("finca_id")

    if not proyecto_id or not plan_json or not finca_id:
        st.info("ℹ️ No hay proyecto vigente. Genera o selecciona un plan primero.")
        return

    # Importar aquí para evitar dependencias circulares
    from modules.marketplace.data_access import get_proyecto
    from modules.marketplace.exportacion_cad_extendida import generar_dxf

    proyecto = get_proyecto(proyecto_id)
    if not proyecto:
        st.error("❌ Proyecto no encontrado en base de datos.")
        return

    # Obtener datos de la finca
    from modules.marketplace.data_access import get_finca
    finca = get_finca(finca_id)
    if not finca:
        st.error("❌ Finca no encontrada en base de datos.")
        return

    superficie_finca = finca.get("superficie_m2", 0)
    ubicacion = finca.get("ubicacion_geo", "No especificada")

    try:
        col1, col2 = st.columns(2)

        with col1:
            # PDF extendido
            if st.button("📄 Descargar Memoria Extendida (PDF)", type="primary", use_container_width=True):
                pdf_bytes = generar_pdf_memoria(plan_json, superficie_finca, ubicacion)
                st.download_button(
                    "⬇️ Descargar PDF",
                    pdf_bytes,
                    file_name=f"memoria_extendida_proyecto_{proyecto_id}_v{st.session_state.get('version', 1)}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        with col2:
            # CAD extendido
            if st.button("🏗️ Descargar Plano CAD Extendido (DXF)", type="primary", use_container_width=True):
                dxf_text = generar_dxf(plan_json, superficie_finca)
                st.download_button(
                    "⬇️ Descargar DXF",
                    dxf_text.encode("utf-8"),
                    file_name=f"plano_extendido_proyecto_{proyecto_id}_v{st.session_state.get('version', 1)}.dxf",
                    mime="application/octet-stream",
                    use_container_width=True
                )

        # Información del proyecto
        version = proyecto.get('version', st.session_state.get('version', 'N/D'))
        st.caption(f"📋 Proyecto ID: {proyecto_id} • Versión: {version} • Finca: {finca.get('titulo', 'N/D')}")

    except Exception as e:
        st.error(f"❌ Error en la exportación: {e}")
        st.info("💡 Intenta regenerar el proyecto si el problema persiste.")