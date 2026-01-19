#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de verificación de integridad del proyecto ArchiRapid
Verifica que los archivos críticos estén en sus ubicaciones correctas
"""
import os
import sys
from pathlib import Path

def verificar_ubicacion_critica():
    """Verifica que compute_edificability.py esté en la raíz"""
    raiz = Path.cwd()

    # Verificar que estamos en la raíz del proyecto
    if not (raiz / "compute_edificability.py").exists():
        print("❌ ERROR CRÍTICO: compute_edificability.py no está en la raíz del proyecto!")
        print(f"   Ubicación actual: {raiz}")
        print("   Este archivo DEBE estar en la raíz para que todos los módulos funcionen correctamente.")
        return False

    # Verificar que no esté en subcarpetas (donde no debería estar)
    subcarpetas_con_problemas = [
        raiz / "archirapid_extract" / "compute_edificability.py",
        raiz / "modules" / "compute_edificability.py",
        raiz / "src" / "compute_edificability.py"
    ]

    for ruta_problematica in subcarpetas_con_problemas:
        if ruta_problematica.exists():
            print(f"⚠️  ADVERTENCIA: Se encontró una copia en {ruta_problematica}")
            print("   Considera eliminar copias duplicadas para evitar confusiones.")

    print("✅ compute_edificability.py está correctamente ubicado en la raíz")
    return True

def verificar_archivos_relacionados():
    """Verifica archivos relacionados con la edificabilidad"""
    raiz = Path.cwd()

    archivos_a_verificar = [
        "catastro_output/validation_report.json",
        "modules/marketplace/plot_detail.py",
        "modules/marketplace/ai_engine_groq.py"
    ]

    print("\n🔍 Verificando archivos relacionados:")
    for archivo in archivos_a_verificar:
        ruta = raiz / archivo
        if ruta.exists():
            print(f"✅ {archivo} encontrado")
        else:
            print(f"❌ {archivo} no encontrado")

def main():
    print("🏗️  Verificación de Integridad - ArchiRapid")
    print("=" * 50)

    exito = verificar_ubicacion_critica()
    verificar_archivos_relacionados()

    if exito:
        print("\n🎉 Integridad del proyecto verificada correctamente")
        print("Los m² exactos están accesibles para todos los módulos.")
    else:
        print("\n❌ Problemas de integridad detectados")
        print("Corrige la ubicación de compute_edificability.py antes de continuar.")
        sys.exit(1)

if __name__ == "__main__":
    main()