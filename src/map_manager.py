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


def mostrar_plots_on_map(province: str | None = None, query: str | None = None, width: int = 700, height: int = 500):
    """Muestra en el mapa las fincas de la base de datos aplicando filtros simples.

    Args:
        province: filtrar por provincia (si no es None)
        query: texto libre para buscar en localidad o título
    Returns:
        El objeto retornado por `st_folium`.
    """
    try:
        from src import db
    except Exception:
        return None

    db.ensure_tables()
    conn = db.get_conn()
    try:
        sql = "SELECT id,title,lat,lon,price,m2,province,locality FROM plots WHERE lat IS NOT NULL AND lon IS NOT NULL"
        params = []
        if province:
            sql += " AND province = ?"
            params.append(province)
        if query:
            sql += " AND (lower(locality) LIKE ? OR lower(title) LIKE ?)"
            q = f"%{query.lower()}%"
            params.extend([q, q])
        cur = conn.cursor()
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        # Determine map center
        lats = [r['lat'] for r in rows]
        lons = [r['lon'] for r in rows]
        if lats and lons:
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            zoom = 10
        else:
            center_lat, center_lon = 40.4168, -3.7038
            zoom = 6

        m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles='OpenStreetMap')

        for r in rows:
            try:
                popup = folium.Popup(f"<b>{r['title']}</b><br/>{r.get('locality','')}<br/>{r.get('m2','')} m² · €{r.get('price','—')}", max_width=260)
                folium.Marker([r['lat'], r['lon']], popup=popup, tooltip=r['title']).add_to(m)
            except Exception:
                continue

        return st_folium(m, width=width, height=height)
    finally:
        conn.close()