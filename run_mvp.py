#!/usr/bin/env python3
"""
Script de arranque combinado para ARCHIRAPID MVP
Lanza backend y frontend en paralelo para desarrollo
"""

import os
import subprocess
import sys
import shutil

def main():
    print("🚀 Iniciando MVP ARCHIRAPID...")
    print("=" * 50)

    # Verificar dependencias
    for dep in ["fastapi", "uvicorn", "streamlit"]:
        try:
            __import__(dep)
        except ImportError:
            print(f"❌ Dependencia faltante: {dep}. Instale con 'pip install {dep}'")
            sys.exit(1)

    # Verificar backend
    backend_dir = os.path.join(os.getcwd(), "backend")
    main_file = os.path.join(backend_dir, "main.py")
    if not os.path.exists(main_file):
        print("❌ No se encontró backend/main.py")
        sys.exit(1)

    # Puerto configurable
    port = os.environ.get("MVP_PORT", "8000")

    # Backend
    print("🔧 Iniciando backend FastAPI...")
    try:
        subprocess.Popen(
            ["uvicorn", "main:app", "--reload", "--port", port],
            cwd=backend_dir
        )
        print(f"✅ Backend iniciado en http://localhost:{port}")
    except Exception as e:
        print("❌ Error al iniciar Backend:", e)
        sys.exit(1)

    # Frontend
    print("🎨 Iniciando frontend Streamlit...")
    try:
        subprocess.Popen(
            ["streamlit", "run", "app.py"],
            cwd=os.getcwd()
        )
        print("✅ Frontend iniciado en http://localhost:8501")
    except Exception as e:
        print("❌ Error al iniciar Frontend:", e)
        sys.exit(1)

    print("\n" + "=" * 50)
    print("🎉 ¡MVP ARCHIRAPID corriendo en backend + frontend!")
    print(f"📍 Backend:  http://localhost:{port}")
    print("🌐 Frontend: http://localhost:8501")
    print("🛑 Presiona Ctrl+C para detener ambos servicios")
    print("=" * 50)

    # Mantener el script corriendo
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
        print("✅ Servicios detenidos")

if __name__ == "__main__":
    main()