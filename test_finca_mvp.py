# Test de subida real de finca usando FincaMVP
from src.models.finca import FincaMVP
import uuid
import requests

def geocode_finca_mvp(finca: FincaMVP):
    """Actualiza finca.lat y finca.lon usando Nominatim. No lanza excepciones si falla."""
    try:
        address = f"{finca.direccion}, {finca.provincia}, España"
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": address,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "archirapid-mvp/1.0"}
        resp = requests.get(url, params=params, headers=headers, timeout=5)
        data = resp.json()
        if data:
            finca.lat = float(data[0]["lat"])
            finca.lon = float(data[0]["lon"])
    except Exception:
        finca.lat = None
        finca.lon = None

# Simulación de datos de formulario
finca_dict = {
    "id": str(uuid.uuid4()),
    "titulo": "Terreno en Sevilla",
    "direccion": "Calle Sol 123",
    "provincia": "Sevilla",
    "precio": 120000,
    "superficie_parcela": 200.0,
    "porcentaje_edificabilidad": 0.33,
    "superficie_edificable": 0,
    "lat": None,
    "lon": None,
    "solar_virtual": {},
    "estado": {"publicada": True}
}

# Crear instancia y calcular superficie edificable
finca = FincaMVP.desde_dict(finca_dict)
finca.calcular_superficie_edificable()

# Geocodificar finca
geocode_finca_mvp(finca)

# Simular guardado en base de datos (solo print)
print({
    "id": finca.id,
    "titulo": finca.titulo,
    "direccion": finca.direccion,
    "provincia": finca.provincia,
    "precio": finca.precio,
    "superficie_parcela": finca.superficie_parcela,
    "superficie_edificable": finca.superficie_edificable,
    "lat": finca.lat,
    "lon": finca.lon
})
