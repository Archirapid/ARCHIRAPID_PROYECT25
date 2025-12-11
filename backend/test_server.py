from fastapi import FastAPI
import uvicorn
import time

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    try:
        print("Iniciando servidor de prueba...")
        # Ejecutar en un thread separado para mantener el proceso vivo
        import threading
        def run_server():
            uvicorn.run(app, host="0.0.0.0", port=8001)
        
        server_thread = threading.Thread(target=run_server)
        server_thread.start()
        
        print("Servidor iniciado en thread separado")
        while True:
            time.sleep(1)
            print("Servidor corriendo...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()