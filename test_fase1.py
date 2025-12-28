#!/usr/bin/env python3
"""
Test de Fase 1: Fundación del esquema paramétrico
Verifica que todas las operaciones atómicas funcionen correctamente
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_design_ops():
    """Test de operaciones de diseño atómicas"""
    print("🔧 TESTEANDO OPERACIONES DE DISEÑO ATÓMICAS")
    print("-" * 50)

    try:
        from design_ops import (
            ensure_plan_schema, add_room, edit_room, remove_room,
            set_roof, set_foundation, set_pool, set_materials,
            auto_layout, validate_plan
        )

        # Finca de ejemplo
        finca_ejemplo = {
            "superficie_m2": 1000,
            "retranqueos": {"front": 5, "side": 3, "back": 5}
        }

        # Test 1: Esquema inicial
        plan = ensure_plan_schema(None, finca_ejemplo)
        assert plan["site"]["area"] == 1000
        assert plan["program"]["total_m2"] == 0
        print("✅ Esquema inicial correcto")

        # Test 2: Añadir habitación
        plan = add_room(plan, {"type": "bedroom", "area": 15})
        assert len(plan["program"]["rooms"]) == 1
        assert plan["program"]["total_m2"] == 15
        print("✅ Añadir habitación funciona")

        # Test 3: Editar habitación
        room_id = plan["program"]["rooms"][0]["id"]
        plan = edit_room(plan, room_id, {"area": 20})
        assert plan["program"]["total_m2"] == 20
        print("✅ Editar habitación funciona")

        # Test 4: Añadir baño
        plan = add_room(plan, {"type": "bathroom", "area": 8})
        assert len(plan["program"]["rooms"]) == 2
        assert plan["program"]["total_m2"] == 28
        print("✅ Añadir baño funciona")

        # Test 5: Configurar cubierta
        plan = set_roof(plan, {"type": "gable", "pitch_deg": 25})
        assert plan["roof"]["type"] == "gable"
        assert plan["roof"]["pitch_deg"] == 25
        print("✅ Configurar cubierta funciona")

        # Test 6: Configurar cimentación
        plan = set_foundation(plan, {"type": "slab", "depth": 0.6})
        assert plan["structure"]["foundation"]["type"] == "slab"
        assert plan["structure"]["foundation"]["depth"] == 0.6
        print("✅ Configurar cimentación funciona")

        # Test 7: Configurar piscina
        plan = set_pool(plan, {"area": 25, "position": "south"})
        assert plan["site"]["pool"]["exists"] == True
        assert plan["site"]["pool"]["area"] == 25
        print("✅ Configurar piscina funciona")

        # Test 8: Configurar materiales
        plan = set_materials(plan, {"exterior": {"walls": "brick"}})
        assert plan["materials"]["exterior"]["walls"] == "brick"
        print("✅ Configurar materiales funciona")

        # Test 9: Validación
        resultado = validate_plan(plan, finca_ejemplo)
        assert resultado["ok"] == True
        assert resultado["total_m2"] == 28
        print("✅ Validación funciona")

        # Test 10: Auto layout
        plan = auto_layout(plan, finca_ejemplo)
        assert "auto_layout" in [h["action"] for h in plan["history"]]
        print("✅ Auto layout funciona")

        return True

    except Exception as e:
        print(f"❌ Error en test de design_ops: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_access_parametrico():
    """Test de funciones de data access paramétrico"""
    print("\n💾 TESTEANDO DATA ACCESS PARAMÉTRICO")
    print("-" * 50)

    try:
        from modules.marketplace.data_access import (
            list_fincas_adquiridas, save_plan_parametrico,
            get_plan_parametrico, list_planes_parametricos_by_finca,
            migrate_plan_to_parametric
        )

        # Test 1: Fincas adquiridas
        fincas_adq = list_fincas_adquiridas("cliente@ejemplo.com")
        assert len(fincas_adq) >= 1
        print("✅ Fincas adquiridas funciona")

        # Test 2: Migrar plan legacy
        plan_legacy = {
            "habitaciones": [{"nombre": "Dormitorio 1", "m2": 15}],
            "banos": [{"nombre": "Baño 1", "m2": 8}],
            "estancias_principales": [{"nombre": "Salón", "m2": 25}]
        }
        finca = {"superficie_m2": 1000}
        plan_migrado = migrate_plan_to_parametric(plan_legacy, finca)
        assert len(plan_migrado["program"]["rooms"]) == 3
        assert plan_migrado["program"]["total_m2"] == 48
        print("✅ Migración de planes funciona")

        # Test 3: Guardar plan paramétrico
        plan_para_guardar = {
            "program": {"rooms": [{"id": "test", "type": "bedroom", "area": 15}], "total_m2": 15},
            "site": {"area": 1000, "buildable_max": 330}
        }
        proyecto_guardado = save_plan_parametrico(plan_para_guardar, 1, "test")
        assert proyecto_guardado["id"] > 0
        assert proyecto_guardado["esquema_parametrico"] == True
        print("✅ Guardar plan paramétrico funciona")

        # Test 4: Recuperar plan paramétrico
        plan_recuperado = get_plan_parametrico(proyecto_guardado["id"])
        assert plan_recuperado["program"]["total_m2"] == 15
        assert "project_metadata" in plan_recuperado
        print("✅ Recuperar plan paramétrico funciona")

        # Test 5: Listar planes por finca
        planes = list_planes_parametricos_by_finca(1)
        assert len(planes) >= 1
        print("✅ Listar planes paramétricos funciona")

        return True

    except Exception as e:
        print(f"❌ Error en test de data_access: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integracion_completa():
    """Test de integración completa del esquema paramétrico"""
    print("\n🔗 TESTEANDO INTEGRACIÓN COMPLETA")
    print("-" * 50)

    try:
        from design_ops import ensure_plan_schema, add_room, validate_plan
        from modules.marketplace.data_access import save_plan_parametrico, get_plan_parametrico

        # Crear plan completo
        finca = {"superficie_m2": 800, "retranqueos": {"front": 5, "side": 3}}
        plan = ensure_plan_schema(None, finca)

        # Añadir varias habitaciones
        plan = add_room(plan, {"type": "bedroom", "area": 14})
        plan = add_room(plan, {"type": "bedroom", "area": 12})
        plan = add_room(plan, {"type": "bathroom", "area": 7})
        plan = add_room(plan, {"type": "living", "area": 30})
        plan = add_room(plan, {"type": "kitchen", "area": 10})

        # Validar
        validacion = validate_plan(plan, finca)
        assert validacion["ok"] == True
        assert validacion["total_m2"] == 73

        # Guardar
        proyecto = save_plan_parametrico(plan, 1, "integration_test")
        assert proyecto["id"] > 0

        # Recuperar y verificar
        plan_recuperado = get_plan_parametrico(proyecto["id"])
        assert len(plan_recuperado["program"]["rooms"]) == 5
        assert plan_recuperado["program"]["total_m2"] == 73

        print("✅ Integración completa funciona")
        print(f"   📊 Plan creado: {len(plan['program']['rooms'])} habitaciones, {plan['program']['total_m2']} m²")
        print(f"   💾 Proyecto guardado: ID {proyecto['id']}, Versión {proyecto['version']}")

        return True

    except Exception as e:
        print(f"❌ Error en integración: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 TEST COMPLETO DE FASE 1: FUNDACIÓN PARAMÉTRICA")
    print("=" * 60)

    tests = [
        ("Operaciones de Diseño", test_design_ops),
        ("Data Access Paramétrico", test_data_access_parametrico),
        ("Integración Completa", test_integracion_completa)
    ]

    resultados = []
    for nombre, test_func in tests:
        print(f"\n🔬 Ejecutando: {nombre}")
        try:
            exito = test_func()
            resultados.append((nombre, exito))
            status = "✅ PASÓ" if exito else "❌ FALLÓ"
            print(f"Resultado: {status}")
        except Exception as e:
            print(f"❌ ERROR CRÍTICO en {nombre}: {e}")
            resultados.append((nombre, False))

    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINALES DE FASE 1:")

    todos_pasan = True
    for nombre, exito in resultados:
        status = "✅" if exito else "❌"
        print(f"   {status} {nombre}")
        if not exito:
            todos_pasan = False

    print("\n" + "=" * 60)
    if todos_pasan:
        print("🎉 ¡FASE 1 COMPLETADA CON ÉXITO!")
        print("🏗️ Fundación paramétrica sólida establecida")
        print("⚡ Listo para proceder a Fase 2: UI del Estudio")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ FASE 1 CON ERRORES - REVISAR LOGS")
        print("🔧 Corregir antes de continuar")
        sys.exit(1)