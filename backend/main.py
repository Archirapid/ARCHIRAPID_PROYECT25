# FastAPI mínima para ARCHIRAPID
from fastapi import FastAPI

app = FastAPI(title="ARCHIRAPID API")

@app.get("/")
def root():
    return {"message": "Backend ARCHIRAPID activo"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/fincas")
def list_fincas():
    return [
        {'id': 1, 'direccion': 'Calle Mayor 1, Madrid', 'superficie_m2': 10500.0, 'ubicacion_geo': {'lat': 40.416, 'lng': -3.703}, 'max_construible_m2': 3500.0, 'estado': 'validada'},
        {'id': 2, 'direccion': 'Av. Diagonal 200, Barcelona', 'superficie_m2': 8000.0, 'ubicacion_geo': {'lat': 41.385, 'lng': 2.173}, 'max_construible_m2': 2600.0, 'estado': 'validada'},
        {'id': 3, 'direccion': 'Camino Real 5, Sevilla', 'superficie_m2': 6000.0, 'ubicacion_geo': {'lat': 37.389, 'lng': -5.984}, 'max_construible_m2': 2000.0, 'estado': 'validada'}
    ]