from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import math
from modules.marketplace import ai_engine_groq as ai
from modules.marketplace.ascii_generator import ascii_square

app = FastAPI(title="ARCHIRAPID API de Planos", version="1.0.0")

class PlanoRequest(BaseModel):
    area_m2: float
    tipologia: str = "casa"  # casa, oficina, etc.
    use_ai: bool = True  # True para LLM, False para algoritmo

@app.post("/generar-plano")
async def generar_plano(request: PlanoRequest):
    """
    Genera un plano ASCII basado en área y tipología.
    """
    if request.area_m2 <= 0:
        raise HTTPException(status_code=400, detail="Área debe ser positiva")

    try:
        if request.use_ai:
            # Usar LLM
            lado = math.sqrt(request.area_m2)
            prompt = f"Genera plano ASCII para {request.area_m2} m², tipología {request.tipologia}: PLANO BASICO ({request.area_m2} m²) NORTE +----+ {lado:.1f}m | {request.tipologia.upper()} | +----+ {lado:.1f}m."
            plano = ai.generate_text(prompt)
            if "Error:" in plano:
                # Fallback a algoritmo
                plano = ascii_square(request.area_m2)
        else:
            # Usar algoritmo
            plano = ascii_square(request.area_m2)

        return {"plano": plano, "area_m2": request.area_m2, "tipologia": request.tipologia, "metodo": "AI" if request.use_ai else "Algoritmo"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "API de Planos ARCHIRAPID activa"}