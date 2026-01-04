"""
Geocodificación para FincaMVP: asigna lat/lon usando dirección y provincia.
"""
from geopy.geocoders import Nominatim
import time

def geocode_finca_mvp(finca):
    """
    Modifica el objeto FincaMVP (o dict compatible) añadiendo lat/lon usando Nominatim.
    Si ya tiene lat/lon, no hace nada.
    """
    if getattr(finca, 'lat', None) and getattr(finca, 'lon', None):
        return finca
    direccion = getattr(finca, 'direccion', None) or (finca.get('direccion') if isinstance(finca, dict) else None)
    provincia = getattr(finca, 'provincia', None) or (finca.get('provincia') if isinstance(finca, dict) else None)
    if not direccion or not provincia:
        return finca
    geolocator = Nominatim(user_agent="archirapid_geocode", timeout=10)
    try:
        loc = geolocator.geocode(f"{direccion}, {provincia}, España")
        if loc:
            if hasattr(finca, 'lat'):
                finca.lat = loc.latitude
                finca.lon = loc.longitude
            elif isinstance(finca, dict):
                finca['lat'] = loc.latitude
                finca['lon'] = loc.longitude
    except Exception:
        time.sleep(1)
    return finca
