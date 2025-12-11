#!/usr/bin/env python3
"""
Script de validación automática del entorno ARCHIRAPID MVP
Verifica dependencias, puertos y servicios antes de ejecutar backend/frontend
"""

import sys
import socket
import requests
import pkg_resources
from typing import List, Tuple, Dict

# Configuración
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"
BACKEND_PORT = 8000
FRONTEND_PORT = 8501

# Dependencias críticas con versiones exactas
REQUIRED_PACKAGES = {
    "fastapi": "0.104.1",
    "uvicorn": "0.24.0",
    "requests": "2.31.0",
    "pydantic": "2.5.0",
    "starlette": "0.27.0",
    "pandas": "2.1.4",
    "numpy": "1.26.4",
    "streamlit": "1.29.0",
    "plotly": "5.18.0",
    "folium": "0.15.1",
    "streamlit-folium": "0.15.0",
    "opencv-python": "4.9.0.80",
    "Pillow": "10.1.0",
    "PyMuPDF": "1.23.8"
}

def check_package_version(package_name: str, required_version: str) -> Tuple[bool, str]:
    """Verifica si un paquete está instalado con la versión correcta"""
    try:
        installed_version = pkg_resources.get_distribution(package_name).version
        if installed_version == required_version:
            return True, f"✅ {package_name}=={installed_version}"
        else:
            return False, f"❌ {package_name}: instalado {installed_version}, requerido {required_version}"
    except pkg_resources.DistributionNotFound:
        return False, f"❌ {package_name}: no instalado (requerido {required_version})"

def check_dependencies() -> Tuple[bool, List[str]]:
    """Verifica todas las dependencias críticas"""
    print("🔍 Verificando dependencias...")
    all_ok = True
    results = []

    for package, version in REQUIRED_PACKAGES.items():
        ok, message = check_package_version(package, version)
        results.append(message)
        if not ok:
            all_ok = False

    return all_ok, results

def check_port_free(port: int, service_name: str) -> Tuple[bool, str]:
    """Verifica si un puerto está libre"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()

        if result == 0:
            # Puerto ocupado
            return False, f"❌ Puerto {port} ({service_name}): ocupado"
        else:
            return True, f"✅ Puerto {port} ({service_name}): libre"
    except Exception as e:
        return False, f"❌ Error verificando puerto {port}: {str(e)}"

def check_ports() -> Tuple[bool, List[str]]:
    """Verifica que los puertos estén libres"""
    print("🔍 Verificando puertos...")
    results = []

    backend_ok, backend_msg = check_port_free(BACKEND_PORT, "Backend")
    frontend_ok, frontend_msg = check_port_free(FRONTEND_PORT, "Frontend")

    results.extend([backend_msg, frontend_msg])

    all_ok = backend_ok and frontend_ok
    return all_ok, results

def test_backend() -> Tuple[bool, str]:
    """Prueba que el backend responda"""
    print("🔍 Probando backend...")
    try:
        response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
        if response.status_code == 200:
            return True, "✅ Backend responde correctamente"
        else:
            return False, f"❌ Backend responde con código {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"❌ Backend no responde: {str(e)}"

def test_frontend() -> Tuple[bool, str]:
    """Prueba que el frontend responda"""
    print("🔍 Probando frontend...")
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            return True, "✅ Frontend responde correctamente"
        else:
            return False, f"❌ Frontend responde con código {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"❌ Frontend no responde: {str(e)}"

def main():
    """Función principal de validación"""
    print("🚀 VALIDACIÓN DEL ENTORNO ARCHIRAPID MVP")
    print("=" * 50)

    all_checks_passed = True
    all_messages = []

    # 1. Verificar dependencias
    deps_ok, deps_messages = check_dependencies()
    all_messages.extend(deps_messages)
    if not deps_ok:
        all_checks_passed = False

    print()

    # 2. Verificar puertos
    ports_ok, ports_messages = check_ports()
    all_messages.extend(ports_messages)
    if not ports_ok:
        all_checks_passed = False

    print()

    # 3. Probar backend
    backend_ok, backend_message = test_backend()
    all_messages.append(backend_message)
    if not backend_ok:
        all_checks_passed = False

    print()

    # 4. Probar frontend
    frontend_ok, frontend_message = test_frontend()
    all_messages.append(frontend_message)
    if not frontend_ok:
        all_checks_passed = False

    print()
    print("=" * 50)
    print("📋 INFORME FINAL")
    print("=" * 50)

    for msg in all_messages:
        print(msg)

    print()

    if all_checks_passed:
        print("🎉 ¡ENTORNO LISTO PARA EJECUTAR MVP COMPLETO!")
        print("✅ Todas las dependencias instaladas correctamente")
        print("✅ Puertos libres para backend y frontend")
        print("✅ Backend y frontend responden correctamente")
        sys.exit(0)
    else:
        print("❌ ENTORNO NO LISTO - CORREGIR ERRORES ANTES DE EJECUTAR")
        print("🔧 Revisa los mensajes de error arriba y soluciona los problemas")
        sys.exit(1)

if __name__ == "__main__":
    main()