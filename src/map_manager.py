import folium
from streamlit_folium import st_folium
import os

def mostrar_mapa_con_plano(lat=40.4168, lon=-3.7038, plano_path=None, zoom=15):
    """
    Muestra un mapa interactivo con Folium, opcionalmente superponiendo un plano catastral.

    Args:
        lat (float): Latitud del centro del mapa
        lon (float): Longitud del centro del mapa
        plano_path (str): Ruta al archivo de imagen del plano (PNG)
        zoom (int): Nivel de zoom inicial

    Returns:
        None: Muestra el mapa en Streamlit
    """
    # Crear mapa base
    m = folium.Map(location=[lat, lon], zoom_start=zoom)

    # Si hay plano, superponerlo
    if plano_path and os.path.exists(plano_path):
        try:
            # Definir bounds aproximados (ajusta según coordenadas reales)
            bounds = [
                [lat - 0.005, lon - 0.005],  # Esquina suroeste
                [lat + 0.005, lon + 0.005]   # Esquina noreste
            ]

            # Añadir overlay de imagen
            folium.raster_layers.ImageOverlay(
                plano_path,
                bounds=bounds,
                opacity=0.7,
                name="Plano Catastral"
            ).add_to(m)

            # Añadir control de capas
            folium.LayerControl().add_to(m)

            # Añadir marcador en el centro
            folium.Marker(
                [lat, lon],
                popup="Centro del Plano",
                tooltip="Haz clic para más info"
            ).add_to(m)

        except Exception as e:
            print(f"Error superponiendo plano: {e}")

    # Mostrar en Streamlit
    return st_folium(m, width=700, height=500)