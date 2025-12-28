#!/usr/bin/env python3
"""
Script para ejecutar ARCHIRAPID con backend API completo
Fase 4: Arquitectura cliente-servidor integrada
"""

import subprocess
import sys
import time
import os
import signal
import threading

def check_backend_health():
    """Verificar que el backend esté funcionando"""
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """Iniciar el backend API"""
    print("🚀 Iniciando backend API...")
    backend_cmd = [sys.executable, "backend/api.py"]
    return subprocess.Popen(backend_cmd, cwd=os.getcwd())

def start_frontend():
    """Iniciar el frontend Streamlit"""
    print("🎨 Iniciando frontend Streamlit...")
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"]
    return subprocess.Popen(frontend_cmd, cwd=os.getcwd())

def main():
    print("🏗️ ARCHIRAPID FASE 4: Arquitectura Cliente-Servidor Completa")
    print("=" * 60)

    # Iniciar backend
    backend_process = start_backend()
    time.sleep(3)  # Esperar a que inicie

    # Verificar backend
    if check_backend_health():
        print("✅ Backend API operativo en http://127.0.0.1:8000")
    else:
        print("❌ Backend API no responde")
        backend_process.terminate()
        return

    # Iniciar frontend
    frontend_process = start_frontend()
    time.sleep(2)

    print("\n🌐 Servicios ARCHIRAPID Fase 4:")
    print("  📡 Backend API: http://127.0.0.1:8000")
    print("  🎨 Frontend: http://localhost:8501")
    print("\n💡 Presiona Ctrl+C para detener todos los servicios")

    try:
        # Mantener procesos vivos
        while True:
            if backend_process.poll() is not None:
                print("❌ Backend se detuvo inesperadamente")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend se detuvo inesperadamente")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")

    # Limpiar procesos
    print("🧹 Limpiando procesos...")
    backend_process.terminate()
    frontend_process.terminate()

    backend_process.wait()
    frontend_process.wait()

    print("✅ Todos los servicios detenidos")

if __name__ == "__main__":
    main()