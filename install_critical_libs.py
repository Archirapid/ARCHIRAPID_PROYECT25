#!/usr/bin/env python3
"""
SCRIPT DE INSTALACIÓN RÁPIDA - LIBRERÍAS CRÍTICAS PARA ARCHIRAPID MVP
Ejecuta este script para instalar/actualizar todas las librerías necesarias
"""

import subprocess
import sys

def run_command(cmd, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🔧 {description}")
    print(f"Comando: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ Éxito")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        print(f"Salida de error: {e.stderr}")
        return False

def main():
    print("🚀 INSTALACIÓN DE LIBRERÍAS CRÍTICAS PARA ARCHIRAPID MVP")
    print("=" * 60)

    # Lista de librerías críticas con versiones específicas
    librerias_criticas = [
        ("PyMuPDF==1.23.25", "PyMuPDF para procesamiento PDF sin dependencias externas"),
        ("Pillow==10.2.0", "Pillow para procesamiento de imágenes"),
        ("google-generativeai==0.8.6", "Google Generative AI para Gemini Vision"),
        ("python-dotenv==1.0.0", "Python-dotenv para variables de entorno")
    ]

    success_count = 0

    for libreria, descripcion in librerias_criticas:
        if run_command(f"pip install --upgrade {libreria}", f"Instalando {descripcion}"):
            success_count += 1

    print(f"\n📊 RESULTADO: {success_count}/{len(librerias_criticas)} librerías instaladas correctamente")

    if success_count == len(librerias_criticas):
        print("\n🎉 ¡Todas las librerías críticas están instaladas!")
        print("\nPara verificar la instalación, ejecuta:")
        print("python -c \"import fitz, PIL, google.generativeai; print('✅ Todas las librerías funcionan')\"")

        print("\nPara probar el motor de extracción:")
        print("python test_motor_optimizado.py")
    else:
        print(f"\n⚠️  {len(librerias_criticas) - success_count} librerías fallaron. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == "__main__":
    main()