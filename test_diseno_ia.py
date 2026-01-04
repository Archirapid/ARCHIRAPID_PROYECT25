#!/usr/bin/env python3
"""
Test para la función generar_diseno_ia
Ejecutar con: python test_diseno_ia.py
"""

from src.models.finca import FincaMVP
from modules.marketplace.ai_engine import generar_diseno_ia

from dotenv import load_dotenv
load_dotenv()

def main():
    # Crear finca de prueba
    finca = FincaMVP(
        id="test123",
        titulo="Finca de prueba",
        direccion="Calle Falsa 123",
        provincia="Madrid",
        precio=100000,
        superficie_parcela=300,
        porcentaje_edificabilidad=0.33,
        superficie_edificable=99,
        lat=40.4,
        lon=-3.7,
        solar_virtual={"ancho": 10, "largo": 10, "orientacion": "S"},
        servicios={"agua": True, "luz": False, "alcantarillado": False},
        estado={"publicada": True}
    )

    print("=== FINCA DE PRUEBA ===")
    print(f"Superficie edificable: {finca.superficie_edificable} m²")
    print(f"Solar virtual: {finca.solar_virtual}")
    print(f"Servicios: {finca.servicios}")
    print()

    try:
        # Generar diseño
        print("Generando diseño con IA...")
        diseno = generar_diseno_ia(finca)

        print("=== RESULTADO DEL DISEÑO ===")
        print(f"Total m²: {diseno.get('total_m2')}")
        print(f"Plantas: {diseno.get('plantas')}")
        print(f"Número de estancias: {len(diseno.get('estancias', []))}")

        # Calcular suma de m² de estancias
        suma_estancias = sum(estancia.get('m2', 0) for estancia in diseno.get('estancias', []))
        print(f"Suma m² de estancias: {suma_estancias}")

        print(f"Extras: {diseno.get('extras')}")

        print()
        print("=== VERIFICACIONES ===")

        # Verificaciones
        total_m2_ok = diseno.get('total_m2', 0) <= finca.superficie_edificable
        suma_estancias_ok = suma_estancias <= finca.superficie_edificable
        plantas_ok = diseno.get('plantas', 0) <= 2

        print(f"Total m² <= superficie edificable: {total_m2_ok} ({diseno.get('total_m2')} <= {finca.superficie_edificable})")
        print(f"Suma estancias <= superficie edificable: {suma_estancias_ok} ({suma_estancias} <= {finca.superficie_edificable})")
        print(f"Plantas <= 2: {plantas_ok} ({diseno.get('plantas')} <= 2)")

        if total_m2_ok and suma_estancias_ok and plantas_ok:
            print("\n✅ TODAS LAS VERIFICACIONES PASARON")
        else:
            print("\n❌ ALGUNAS VERIFICACIONES FALLARON")

        print()
        print("=== DETALLE DE ESTANCIAS ===")
        for i, estancia in enumerate(diseno.get('estancias', [])):
            print(f"{i+1}. {estancia.get('nombre')} - {estancia.get('m2')} m² - Planta {estancia.get('planta')} - Tipo: {estancia.get('tipo')}")

    except Exception as e:
        print(f"❌ Error al generar diseño: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()