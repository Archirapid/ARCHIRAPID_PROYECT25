import base64
from src.models.finca import FincaMVP
import streamlit as st

def generar_svg_solar_virtual(finca: FincaMVP) -> str:
    """
    Genera un SVG simple de un solar virtual rectangular a partir de finca.solar_virtual.
    Escala: 1m = 1 unidad SVG.
    """
    ancho = finca.solar_virtual.get("ancho", 10)
    largo = finca.solar_virtual.get("largo", 20)
    superficie = finca.superficie_parcela
    # SVG viewBox con margen
    margin = 5
    svg_width = ancho + 2 * margin
    svg_height = largo + 2 * margin
    svg = f'''
    <svg width="300" height="300" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">
      <rect x="{margin}" y="{margin}" width="{ancho}" height="{largo}"
            fill="#b3d8ff" stroke="#003366" stroke-width="0.5" rx="2"/>
      <text x="{svg_width/2}" y="{svg_height/2 - 2}" text-anchor="middle" font-size="3" fill="#003366" font-weight="bold">Solar virtual</text>
      <text x="{svg_width/2}" y="{svg_height/2 + 3}" text-anchor="middle" font-size="2.5" fill="#003366">{superficie} m²</text>
    </svg>
    '''
    return svg

def mostrar_solar_virtual_svg(finca: FincaMVP):
    svg = generar_svg_solar_virtual(finca)
    svg_bytes = svg.encode("utf-8")
    svg_b64 = base64.b64encode(svg_bytes).decode("utf-8")
    st.markdown("""
    <div style='text-align:center;'>
      <h4>Plano conceptual del solar</h4>
      <img src='data:image/svg+xml;base64,{svg_b64}' style='border:1px solid #888; max-width:90%; height:auto;' />
    </div>
    """.format(svg_b64=svg_b64), unsafe_allow_html=True)
