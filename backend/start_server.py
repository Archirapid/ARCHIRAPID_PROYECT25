# Script para iniciar el backend de ARCHIRAPID
try:
    from main import app
    print("Import de main exitoso")
except Exception as e:
    print(f"Error importando main: {e}")
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/health")
    def health():
        return {"status": "ok"}

import uvicorn

if __name__ == "__main__":
    print("Iniciando servidor ARCHIRAPID...")
    uvicorn.run(app, host="0.0.0.0", port=8000)