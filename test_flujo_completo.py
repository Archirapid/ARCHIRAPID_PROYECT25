#!/usr/bin/env python3
"""
Test script para verificar el flujo completo de ARCHIRAPID
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_data_access():
    """Test de acceso a datos"""
    try:
        from modules.marketplace.data_access import list_fincas_publicadas, list_fincas_by_user, get_finca

        # Test fincas públicas
        fincas_pub = list_fincas_publicadas()
        print(f"✅ Fincas públicas: {len(fincas_pub)} encontradas")

        # Test fincas por usuario
        fincas_user = list_fincas_by_user("cliente_demo@example.com")
        print(f"✅ Fincas de usuario: {len(fincas_user)} encontradas")

        # Test obtener finca específica
        if fincas_pub:
            finca = get_finca(fincas_pub[0]["id"])
            print(f"✅ Finca obtenida: {finca.get('titulo', 'Sin título')}")

        return True
    except Exception as e:
        print(f"❌ Error en data_access: {e}")
        return False

def test_visualization():
    """Test de visualización 3D"""
    try:
        from modules.marketplace.gemelo_digital_vis import create_gemelo_3d

        # Plan de ejemplo
        plan_ejemplo = {
            "habitaciones": [{"nombre": "Dormitorio 1", "m2": 15}],
            "banos": [{"nombre": "Baño 1", "m2": 8}],
            "total_m2": 23
        }

        fig = create_gemelo_3d(plan_ejemplo)
        print("✅ Visualización 3D generada correctamente")
        return True
    except Exception as e:
        print(f"❌ Error en visualización: {e}")
        return False

def test_ai_engine():
    """Test del motor de IA"""
    try:
        from modules.marketplace.ai_engine import get_ai_response

        response = get_ai_response("Hola, necesito ayuda con un diseño")
        print(f"✅ Respuesta IA: {response[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Error en IA: {e}")
        return False

def test_validation():
    """Test de validación"""
    try:
        from modules.marketplace.validacion import validar_plan_local

        plan_test = {"total_m2": 100}
        resultado = validar_plan_local(plan_test, 300)
        print(f"✅ Validación completada: {resultado}")
        return True
    except Exception as e:
        print(f"❌ Error en validación: {e}")
        return False

def main():
    print("🧪 Iniciando pruebas del flujo ARCHIRAPID...")
    print("=" * 50)

    tests = [
        ("Acceso a datos", test_data_access),
        ("Visualización 3D", test_visualization),
        ("Motor de IA", test_ai_engine),
        ("Validación", test_validation)
    ]

    passed = 0
    total = len(tests)

    for name, test_func in tests:
        print(f"\n🔍 Probando {name}...")
        if test_func():
            passed += 1

    print("\n" + "=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El flujo está listo.")
        return 0
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores.")
        return 1

if __name__ == "__main__":
    sys.exit(main())