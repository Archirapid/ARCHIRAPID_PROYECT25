# modules/marketplace/exportacion_cad_extendida.py

from modules.marketplace.documentacion import generar_plano_cad
import streamlit as st
import json

def generar_dxf(plan_json, superficie_finca):
    """
    Genera un archivo DXF con el plano CAD extendido del proyecto.
    Usa la función existente generar_plano_cad y agrega metadatos extendidos.

    Args:
        plan_json: Plan de vivienda con habitaciones y garage
        superficie_finca: Superficie total de la finca en m²

    Returns:
        str: Contenido del archivo DXF
    """
    # Generar DXF usando función existente
    dxf_basico = generar_plano_cad(plan_json)

    # Agregar metadatos extendidos al DXF
    dxf_extendido = f"""{dxf_basico}

999
ARCHIRAPID - PLANO EXTENDIDO
999
Superficie finca: {superficie_finca} m²
999
Versión: {st.session_state.get('version', 'N/D')}
999
Proyecto ID: {st.session_state.get('proyecto_id', 'N/D')}
999
Generado con IA - Revisar con arquitecto colegiado
0
ENDSEC
0
EOF
"""

    return dxf_extendido