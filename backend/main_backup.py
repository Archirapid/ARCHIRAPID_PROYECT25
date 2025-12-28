# FastAPI mínima para fincas, proyectos y exportación
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import uvicorn

app = FastAPI(title="ARCHIRAPID API")

@app.get("/")
def root():
    return {"message": "Backend ARCHIRAPID activo"}

# ---- In-memory store (cambia a SQLite al final) ----
DB = {"fincas": {}, "proyectos": {}, "exports": {}}
SEQ = {"fincas": 1, "proyectos": 1, "exports": 1}

class Finca(BaseModel):
    direccion: str
    superficie_m2: float
    ref_catastral: Optional[str] = None
    foto_url: Optional[str] = None
    ubicacion_geo: Optional[Dict[str, float]] = None
    max_construible_m2: Optional[float] = None
    retranqueos: Optional[Dict[str, float]] = None
    propietario_email: Optional[str] = None
    estado: Optional[str] = "validada"

class Proyecto(BaseModel):
    finca_id: int
    nombre: str
    autor_tipo: str  # ia | user+ia | arquitecto
    version: int
    json_distribucion: Dict
    total_m2: float
    extras: Optional[Dict] = None
    precio_estimado: Optional[float] = 0.0

class ExportRequest(BaseModel):
    proyecto_id: int
    tipo: str  # pdf | cad | zip
    precio: float

@app.post("/fincas")
def crear_finca(f: Finca):
    fid = SEQ["fincas"]; SEQ["fincas"] += 1
    DB["fincas"][fid] = {**f.dict(), "id": fid}
    return {"id": fid, "status": "validada", "finca": DB["fincas"][fid]}

@app.get("/fincas/{fid}")
def get_finca(fid: int):
    f = DB["fincas"].get(fid)
    if not f: raise HTTPException(404, "Finca no encontrada")
    return f

@app.get("/fincas")
def list_fincas(propietario_email: Optional[str] = None, publicas: Optional[bool] = None):
    fincas = list(DB["fincas"].values())
    if propietario_email:
        fincas = [f for f in fincas if f.get("propietario_email") == propietario_email]
    if publicas is True:
        fincas = [f for f in fincas if not f.get("propietario_email")]
    return fincas

@app.post("/proyectos")
def crear_proyecto(p: Proyecto):
    pid = SEQ["proyectos"]; SEQ["proyectos"] += 1
    DB["proyectos"][pid] = {**p.dict(), "id": pid}
    return DB["proyectos"][pid]

@app.get("/proyectos/{pid}")
def get_proyecto(pid: int):
    pr = DB["proyectos"].get(pid)
    if not pr: raise HTTPException(404, "Proyecto no encontrado")
    return pr

@app.get("/proyectos")
def list_proyectos(finca_id: Optional[int] = None):
    projs = list(DB["proyectos"].values())
    if finca_id is not None:
        projs = [p for p in projs if p["finca_id"] == finca_id]
    return projs

@app.post("/export")
def exportar(req: ExportRequest):
    eid = SEQ["exports"]; SEQ["exports"] += 1
    DB["exports"][eid] = {"id": eid, "proyecto_id": req.proyecto_id, "tipo": req.tipo, "precio": req.precio, "status": "generado"}
    # Devuelve URL simulada; en MVP, mensaje de éxito
    return {"id": eid, "status": "generado", "download_url": f"/descargas/{eid}"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Ejecutar servidor si se llama directamente
if __name__ == "__main__":
    print("Ejecutando main.py directamente")
    import uvicorn
    print("Iniciando uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("Servidor terminado")