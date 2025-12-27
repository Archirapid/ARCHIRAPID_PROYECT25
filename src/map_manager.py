import folium
import streamlit as st
import streamlit.components.v1 as components
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

    # Mostrar en Streamlit: render HTML directamente para evitar problemas con el componente
    try:
        components.html(m._repr_html_(), height=500)
    except Exception:
        return None


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

        # Removed debug traces to avoid noisy output in Streamlit
        # Determine map center as mean of returned coords
        lats = [r['lat'] for r in rows if r['lat'] is not None]
        lons = [r['lon'] for r in rows if r['lon'] is not None]
        if lats and lons:
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            # country-level view suitable for Spain/Portugal
            zoom = 6
        else:
            center_lat, center_lon = 40.4168, -3.7038
            zoom = 6

        m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom, tiles='OpenStreetMap')

        # Add more visible markers with red home icon and informative popup
        for r in rows:
            try:
                title = r['title'] or ''
                locality = r['locality'] or ''
                m2 = r['m2'] if r['m2'] is not None else ''
                price = r['price'] if r['price'] is not None else '—'
                # Enlace a más detalles (de momento que al menos se vea)
                details_link = f"<br/><a href='http://localhost:8501/?selected_plot={r['id']}' target='_blank'>Ver más detalles</a>"
                popup_html = f"<b>{title}</b><br/>{locality}<br/>{m2} m² · €{price}{details_link}"
                popup = folium.Popup(popup_html, max_width=300)
                icon = folium.Icon(color='red', icon='home')
                folium.Marker([r['lat'], r['lon']], popup=popup, tooltip=title, icon=icon).add_to(m)
            except Exception:
                continue

        try:
            return components.html(m._repr_html_(), height=height)
        except Exception:
            return None
    finally:
        conn.close()
    # Fallback return (safety): attempt to render if not already returned
    try:
        return components.html(m._repr_html_(), height=height)
    except Exception:
        return None