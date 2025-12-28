#!/usr/bin/env python3
"""
Script temporal para ejecutar el backend FastAPI
"""
from fastapi import FastAPI
import uvicorn

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
        {'id': 1, 'direccion': 'Calle Mayor 1, Madrid', 'superficie_m2': 10500.0, 'ubicacion_geo': {'lat': 40.416, 'lng': -3.703}, 'max_construible_m2': 3500.0, 'estado': 'validada', 'pvp': 1500000, 'ref_catastral': '1234567AB1234N0001AA', 'foto_url': ['/static/no-photo.png']},
        {'id': 2, 'direccion': 'Av. Diagonal 200, Barcelona', 'superficie_m2': 8000.0, 'ubicacion_geo': {'lat': 41.385, 'lng': 2.173}, 'max_construible_m2': 2600.0, 'estado': 'validada', 'pvp': 1200000, 'ref_catastral': '9876543CD5678M0002BB', 'foto_url': ['/static/no-photo.png']},
        {'id': 3, 'direccion': 'Camino Real 5, Sevilla', 'superficie_m2': 6000.0, 'ubicacion_geo': {'lat': 37.389, 'lng': -5.984}, 'max_construible_m2': 2000.0, 'estado': 'validada', 'pvp': 800000, 'ref_catastral': '4567890EF9012O0003CC', 'foto_url': ['/static/no-photo.png']}
    ]

if __name__ == "__main__":
    print("🚀 Iniciando backend ARCHIRAPID...")
    uvicorn.run(app, host="0.0.0.0", port=8000)