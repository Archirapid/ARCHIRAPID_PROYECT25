# FastAPI mínima para ARCHIRAPID
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict

app = FastAPI(title="ARCHIRAPID API")

# Base de datos en memoria
fincas_db = [
    {'id': 1, 'direccion': 'Calle Mayor 1, Madrid', 'superficie_m2': 10500.0, 'ubicacion_geo': {'lat': 40.416, 'lng': -3.703}, 'max_construible_m2': 3500.0, 'estado': 'validada', 'pvp': 1500000, 'ref_catastral': '1234567AB1234N0001AA', 'foto_url': ['/static/no-photo.png']},
    {'id': 2, 'direccion': 'Av. Diagonal 200, Barcelona', 'superficie_m2': 8000.0, 'ubicacion_geo': {'lat': 41.385, 'lng': 2.173}, 'max_construible_m2': 2600.0, 'estado': 'validada', 'pvp': 1200000, 'ref_catastral': '9876543CD5678M0002BB', 'foto_url': ['/static/no-photo.png']},
    {'id': 3, 'direccion': 'Camino Real 5, Sevilla', 'superficie_m2': 6000.0, 'ubicacion_geo': {'lat': 37.389, 'lng': -5.984}, 'max_construible_m2': 2000.0, 'estado': 'validada', 'pvp': 800000, 'ref_catastral': '4567890EF9012O0003CC', 'foto_url': ['/static/no-photo.png']}
]
next_id = 4

class UbicacionGeo(BaseModel):
    lat: float
    lng: float

class Propietario(BaseModel):
    nombre: str
    email: str
    telefono: str
    dni: Optional[str] = None
    direccion: Optional[str] = None
    cuenta_bancaria: Optional[str] = None

class FincaCreate(BaseModel):
    direccion: str
    superficie_m2: float
    ref_catastral: Optional[str] = None
    foto_url: Optional[List[str]] = None
    ubicacion_geo: UbicacionGeo
    max_construible_m2: Optional[float] = 0.0
    retranqueos: Optional[Dict] = None
    propietario: Optional[Propietario] = None
    propietario_email: Optional[str] = None  # Mantener compatibilidad
    estado: Optional[str] = "pendiente"
    pvp: Optional[float] = None
    sync_intranet: Optional[bool] = False

@app.get("/")
def root():
    return {"message": "Backend ARCHIRAPID activo"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/fincas")
def list_fincas(propietario_email: Optional[str] = None):
    if propietario_email:
        # Filtrar fincas por email del propietario
        fincas_filtradas = []
        for finca in fincas_db:
            # Verificar tanto en propietario.email como en propietario_email (compatibilidad)
            propietario = finca.get("propietario", {})
            if (propietario.get("email") == propietario_email or
                finca.get("propietario_email") == propietario_email):
                fincas_filtradas.append(finca)
        return fincas_filtradas
    return fincas_db

@app.post("/fincas")
def create_finca(finca: FincaCreate):
    global next_id
    nueva_finca = finca.dict()
    nueva_finca["id"] = next_id
    next_id += 1
    fincas_db.append(nueva_finca)
    return {"id": nueva_finca["id"], "status": "creada", "finca": nueva_finca}