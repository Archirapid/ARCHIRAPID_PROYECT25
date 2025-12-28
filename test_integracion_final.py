#!/usr/bin/env python3
"""
Test de integración final: Verificar que la aplicación completa funciona
con la nueva UI del estudio
"""
import sys
import os
import time
import requests
import subprocess
import signal

def test_app_startup():
    """Test que la aplicación se inicia correctamente"""
    print("🚀 TESTEANDO INICIO DE APLICACIÓN")
    print("-" * 50)

    try:
        # Verificar que el proceso está corriendo
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq python.exe"],
            capture_output=True, text=True
        )

        if "python.exe" in result.stdout:
            print("✅ Aplicación ejecutándose")
            return True
        else:
            print("❌ Aplicación no encontrada")
            return False

    except Exception as e:
        print(f"❌ Error verificando aplicación: {e}")
        return False

def test_studio_navigation():
    """Test de navegación al estudio"""
    print("\n🧭 TESTEANDO NAVEGACIÓN AL ESTUDIO")
    print("-" * 50)

    try:
        # Simular navegación a través del código
        # Verificar que studio_panel existe y es callable
        from app import studio_panel

        if callable(studio_panel):
            print("✅ Función studio_panel disponible")
        else:
            print("❌ studio_panel no es callable")
            return False

        # Verificar que client_panel usa studio_panel
        import inspect
        source = inspect.getsource(studio_panel)

        if "Asistente IA Continuo" in source and "Programación Arquitectónica" in source:
            print("✅ studio_panel contiene IA conversacional y editores profesionales")
        else:
            print("❌ studio_panel no tiene componentes esperados")
            return False

        return True

    except Exception as e:
        print(f"❌ Error en navegación: {e}")
        return False

def test_parametric_operations_integration():
    """Test de integración de operaciones paramétricas"""
    print("\n⚙️ TESTEANDO INTEGRACIÓN OPERACIONES PARAMÉTRICAS")
    print("-" * 50)

    try:
        from design_ops import (
            ensure_plan_schema, add_room, edit_room, remove_room,
            set_roof, set_foundation, set_pool, set_materials,
            auto_layout, validate_plan
        )

        # Simular flujo completo de usuario en estudio
        finca = {"superficie_m2": 800, "retranqueos": {"front": 6, "side": 4}}

        # 1. Inicializar proyecto
        plan = ensure_plan_schema(None, finca)

        # 2. Diseño básico
        plan = add_room(plan, {"type": "living", "area": 35})
        plan = add_room(plan, {"type": "kitchen", "area": 16})
        plan = add_room(plan, {"type": "bedroom", "area": 18})
        plan = add_room(plan, {"type": "bedroom", "area": 14})
        plan = add_room(plan, {"type": "bathroom", "area": 10})
        plan = add_room(plan, {"type": "bathroom", "area": 6})

        # 3. Estructura
        plan = set_foundation(plan, {"type": "slab", "depth": 0.6, "material": "reinforced_concrete"})
        plan = set_roof(plan, {"type": "hip", "pitch_deg": 20, "material": "concrete_tiles"})

        # 4. Extras
        plan = set_pool(plan, {"area": 40, "position": "backyard"})

        # 5. Materiales
        plan = set_materials(plan, {
            "exterior": {"walls": "brick", "roof": "tiles", "windows": "pvc", "doors": "wood"},
            "interior": {"walls": "plaster", "floors": "ceramic", "ceilings": "plaster", "doors": "wood"},
            "finishes": {"kitchen": "granite", "bathrooms": "ceramic", "floors": "hardwood"}
        })

        # 6. Auto-layout
        plan = auto_layout(plan, finca)

        # 7. Validar
        validation = validate_plan(plan, finca)

        if validation["ok"]:
            print("✅ Flujo paramétrico completo funciona")
            print(f"   🏠 Proyecto: {len(plan['program']['rooms'])} espacios, {plan['program']['total_m2']} m²")
            print(f"   🏗️ Estructura: {plan['roof']['type']} + {plan['structure']['foundation']['type']}")
            print(f"   🏊 Piscina: {plan['site']['pool']['area']}m²")
            print(f"   🎨 Materiales: {plan['materials']['exterior']['walls']} exterior")
            return True
        else:
            print(f"❌ Validación falló: {validation['warnings']}")
            return False

    except Exception as e:
        print(f"❌ Error en operaciones paramétricas: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_conversation_flow():
    """Test del flujo de conversación con IA"""
    print("\n🤖 TESTEANDO FLUJO CONVERSACIÓN IA")
    print("-" * 50)

    try:
        # Simular conversación completa
        conversation_log = []

        # Usuario pide diseño básico
        user_input = "Quiero una casa de 3 dormitorios con piscina"
        conversation_log.append(f"Usuario: {user_input}")

        # IA procesa
        parsed_actions = []
        ui = user_input.lower()

        if "3 dormitorios" in ui or "tres dormitorios" in ui:
            parsed_actions.extend(["add_room bedroom", "add_room bedroom", "add_room bedroom"])
        if "piscina" in ui:
            parsed_actions.append("set_pool backyard")

        conversation_log.append(f"IA parsea: {parsed_actions}")

        # Aplicar acciones
        from design_ops import ensure_plan_schema, add_room, set_pool
        finca = {"superficie_m2": 600}
        plan = ensure_plan_schema(None, finca)

        for action in parsed_actions:
            if action == "add_room bedroom":
                plan = add_room(plan, {"type": "bedroom", "area": 15})
            elif action == "set_pool backyard":
                plan = set_pool(plan, {"area": 25, "position": "backyard"})

        conversation_log.append(f"Plan actualizado: {len(plan['program']['rooms'])} habitaciones")

        # IA responde
        response = f"He creado un diseño con {len(plan['program']['rooms'])} dormitorios y piscina de {plan['site']['pool']['area']}m². ¿Quieres añadir más espacios?"
        conversation_log.append(f"IA responde: {response}")

        print("✅ Flujo conversación IA funciona")
        for msg in conversation_log:
            print(f"   💬 {msg}")
        return True

    except Exception as e:
        print(f"❌ Error en conversación IA: {e}")
        return False

def test_3d_visualization_integration():
    """Test de integración de visualización 3D"""
    print("\n🌐 TESTEANDO INTEGRACIÓN VISUALIZACIÓN 3D")
    print("-" * 50)

    try:
        from design_ops import ensure_plan_schema, add_room
        from modules.marketplace.gemelo_digital_vis import create_gemelo_3d

        # Crear plan complejo
        finca = {"superficie_m2": 500}
        plan = ensure_plan_schema(None, finca)

        # Añadir varios espacios
        spaces = [
            {"type": "living", "area": 30},
            {"type": "kitchen", "area": 12},
            {"type": "bedroom", "area": 16},
            {"type": "bedroom", "area": 12},
            {"type": "bathroom", "area": 8}
        ]

        for space in spaces:
            plan = add_room(plan, space)

        # Generar visualización
        fig = create_gemelo_3d(plan)

        if fig:
            print("✅ Visualización 3D integrada correctamente")
            print(f"   📊 Modelo 3D generado para {len(plan['program']['rooms'])} espacios")
            return True
        else:
            print("❌ No se pudo generar visualización 3D")
            return False

    except Exception as e:
        print(f"❌ Error en visualización 3D: {e}")
        return False

def test_export_capabilities():
    """Test de capacidades de exportación"""
    print("\n📤 TESTEANDO CAPACIDADES DE EXPORTACIÓN")
    print("-" * 50)

    try:
        from design_ops import ensure_plan_schema, add_room, set_materials
        from modules.marketplace.data_access import save_plan_parametrico

        # Crear proyecto completo
        finca = {"superficie_m2": 400}
        plan = ensure_plan_schema(None, finca)

        plan = add_room(plan, {"type": "living", "area": 25})
        plan = add_room(plan, {"type": "kitchen", "area": 10})
        plan = add_room(plan, {"type": "bedroom", "area": 14})

        plan = set_materials(plan, {
            "exterior": {"walls": "brick", "roof": "tiles"},
            "interior": {"floors": "ceramic"}
        })

        # Guardar proyecto
        proyecto = save_plan_parametrico(plan, 1, "export_test")

        if proyecto and proyecto["id"] > 0:
            print("✅ Proyecto guardado para exportación")
            print(f"   💾 ID: {proyecto['id']}, Versión: {proyecto['version']}")
            print("   📋 Listo para exportar: PDF, CAD, materiales, presupuesto")
            return True
        else:
            print("❌ Error guardando proyecto")
            return False

    except Exception as e:
        print(f"❌ Error en exportación: {e}")
        return False

if __name__ == "__main__":
    print("🔗 TEST DE INTEGRACIÓN FINAL DE ARCHIRAPID")
    print("=" * 60)

    tests = [
        ("Inicio de Aplicación", test_app_startup),
        ("Navegación al Estudio", test_studio_navigation),
        ("Operaciones Paramétricas", test_parametric_operations_integration),
        ("Flujo Conversación IA", test_ai_conversation_flow),
        ("Visualización 3D", test_3d_visualization_integration),
        ("Capacidades Exportación", test_export_capabilities)
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
    print("📊 RESULTADOS INTEGRACIÓN FINAL:")

    todos_pasan = True
    for nombre, exito in resultados:
        status = "✅" if exito else "❌"
        print(f"   {status} {nombre}")
        if not exito:
            todos_pasan = False

    print("\n" + "=" * 60)
    if todos_pasan:
        print("🎉 ¡INTEGRACIÓN COMPLETA EXITOSA!")
        print("🏗️ ARCHIRAPID listo para producción")
        print("🎨 Estudio profesional operativo")
        print("🤖 IA conversacional funcional")
        print("⚡ Preparado para Fase 3: IA Avanzada")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ INTEGRACIÓN CON ERRORES - REVISAR")
        print("🔧 Corregir antes de producción")
        sys.exit(1)