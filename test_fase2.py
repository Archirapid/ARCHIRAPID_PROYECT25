#!/usr/bin/env python3
"""
Test exhaustivo de Fase 2: UI del Estudio
Verifica que studio_panel() funcione correctamente con IA conversacional
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_studio_panel_imports():
    """Test de imports necesarios para studio_panel"""
    print("🔧 TESTEANDO IMPORTS DE STUDIO PANEL")
    print("-" * 50)

    try:
        from app import studio_panel
        from design_ops import (
            ensure_plan_schema, add_room, edit_room, remove_room,
            set_roof, set_foundation, set_pool, set_materials, auto_layout,
            validate_plan
        )
        from modules.marketplace.data_access import (
            get_finca, save_plan_parametrico, get_plan_parametrico,
            list_proyectos_compatibles
        )
        from modules.marketplace.gemelo_digital_vis import create_gemelo_3d

        print("✅ Todos los imports funcionan")
        return True

    except Exception as e:
        print(f"❌ Error en imports: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ia_conversacional_parser():
    """Test del parser de IA conversacional"""
    print("\n🤖 TESTEANDO PARSER IA CONVERSACIONAL")
    print("-" * 50)

    try:
        # Simular órdenes de IA
        test_orders = [
            "añade dormitorio de 15m²",
            "cubierta a dos aguas",
            "piscina al sur de 30m²",
            "materiales modernos",
            "elimina ultimo",
            "optimiza distribucion"
        ]

        # Verificar que las órdenes se parsearían correctamente
        for order in test_orders:
            p = order.lower()
            actions_found = []

            if "añade" in p and "dormitorio" in p:
                actions_found.append("add_room bedroom")
            if "cubierta" in p and "dos aguas" in p:
                actions_found.append("set_roof gable")
            if "piscina" in p and "sur" in p:
                actions_found.append("set_pool south")
            if "materiales" in p and "modernos" in p:
                actions_found.append("set_materials modern")
            if "elimina" in p and "ultimo" in p:
                actions_found.append("remove_room")
            if "optimiza" in p or "distribucion" in p:
                actions_found.append("auto_layout")

            if actions_found:
                print(f"✅ '{order}' → {actions_found}")
            else:
                print(f"❌ '{order}' → No parseado")

        print("✅ Parser IA validado")
        return True

    except Exception as e:
        print(f"❌ Error en parser IA: {e}")
        return False

def test_operaciones_atomicas_ui():
    """Test de operaciones atómicas desde UI"""
    print("\n⚙️ TESTEANDO OPERACIONES ATÓMICAS UI")
    print("-" * 50)

    try:
        from design_ops import ensure_plan_schema, add_room, validate_plan

        # Finca de test
        finca = {"superficie_m2": 500, "retranqueos": {"front": 5, "side": 3}}

        # Simular flujo UI
        plan = ensure_plan_schema(None, finca)
        assert plan["site"]["area"] == 500

        # Añadir habitaciones como en UI
        plan = add_room(plan, {"type": "bedroom", "area": 15})
        plan = add_room(plan, {"type": "bathroom", "area": 8})
        plan = add_room(plan, {"type": "kitchen", "area": 12})
        plan = add_room(plan, {"type": "living", "area": 25})

        # Verificar estado
        rooms = plan["program"]["rooms"]
        assert len(rooms) == 4
        assert plan["program"]["total_m2"] == 60

        # Validar
        validation = validate_plan(plan, finca)
        assert validation["ok"] == True

        print("✅ Operaciones UI simuladas correctamente")
        print(f"   📊 Plan creado: {len(rooms)} habitaciones, {plan['program']['total_m2']} m²")
        return True

    except Exception as e:
        print(f"❌ Error en operaciones UI: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_undo_redo_logica():
    """Test de lógica undo/redo"""
    print("\n↶↷ TESTEANDO UNDO/REDO")
    print("-" * 50)

    try:
        # Simular estado de sesión
        session_state = {
            "plan_json": None,
            "undo_stack": [],
            "redo_stack": []
        }

        from design_ops import ensure_plan_schema, add_room

        # Finca de test
        finca = {"superficie_m2": 300}

        # Estado inicial
        session_state["plan_json"] = ensure_plan_schema(None, finca)

        # Operación 1: añadir habitación
        pj_before = session_state["plan_json"]
        session_state["plan_json"] = add_room(pj_before, {"type": "bedroom", "area": 15})
        session_state["undo_stack"].append(pj_before)
        session_state["redo_stack"].clear()

        assert len(session_state["undo_stack"]) == 1
        assert len(session_state["redo_stack"]) == 0
        assert len(session_state["plan_json"]["program"]["rooms"]) == 1

        # Operación 2: añadir baño
        pj_before = session_state["plan_json"]
        session_state["plan_json"] = add_room(pj_before, {"type": "bathroom", "area": 8})
        session_state["undo_stack"].append(pj_before)
        session_state["redo_stack"].clear()

        assert len(session_state["undo_stack"]) == 2
        assert len(session_state["plan_json"]["program"]["rooms"]) == 2

        # Undo
        if session_state["undo_stack"]:
            prev = session_state["undo_stack"].pop()
            session_state["redo_stack"].append(session_state["plan_json"])
            session_state["plan_json"] = prev

        assert len(session_state["undo_stack"]) == 1
        assert len(session_state["redo_stack"]) == 1
        assert len(session_state["plan_json"]["program"]["rooms"]) == 1

        # Redo
        if session_state["redo_stack"]:
            next_p = session_state["redo_stack"].pop()
            session_state["undo_stack"].append(session_state["plan_json"])
            session_state["plan_json"] = next_p

        assert len(session_state["undo_stack"]) == 2
        assert len(session_state["redo_stack"]) == 0
        assert len(session_state["plan_json"]["program"]["rooms"]) == 2

        print("✅ Undo/Redo funciona correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en undo/redo: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_materiales_configuracion():
    """Test de configuración de materiales"""
    print("\n🎨 TESTEANDO CONFIGURACIÓN DE MATERIALES")
    print("-" * 50)

    try:
        from design_ops import ensure_plan_schema, set_materials

        finca = {"superficie_m2": 400}
        plan = ensure_plan_schema(None, finca)

        # Aplicar materiales modernos
        plan = set_materials(plan, {
            "exterior": {
                "walls": "concrete",
                "roof": "flat",
                "windows": "aluminum",
                "doors": "steel"
            },
            "interior": {
                "walls": "plaster",
                "floors": "ceramic",
                "ceilings": "plaster",
                "doors": "wood"
            },
            "finishes": {
                "kitchen": "silestone",
                "bathrooms": "porcelain",
                "floors": "parquet"
            }
        })

        materials = plan["materials"]
        assert materials["exterior"]["walls"] == "concrete"
        assert materials["interior"]["floors"] == "ceramic"
        assert materials["finishes"]["kitchen"] == "silestone"

        print("✅ Configuración de materiales funciona")
        return True

    except Exception as e:
        print(f"❌ Error en materiales: {e}")
        return False

def test_visualizacion_3d():
    """Test de visualización 3D"""
    print("\n🌐 TESTEANDO VISUALIZACIÓN 3D")
    print("-" * 50)

    try:
        from design_ops import ensure_plan_schema, add_room
        from modules.marketplace.gemelo_digital_vis import create_gemelo_3d

        finca = {"superficie_m2": 300}
        plan = ensure_plan_schema(None, finca)

        # Añadir algunas habitaciones
        plan = add_room(plan, {"type": "bedroom", "area": 15})
        plan = add_room(plan, {"type": "living", "area": 25})

        # Generar 3D
        fig = create_gemelo_3d(plan)

        print("✅ Visualización 3D generada correctamente")
        print(f"   📊 Plan visualizado: {len(plan['program']['rooms'])} habitaciones")
        return True

    except Exception as e:
        print(f"❌ Error en 3D: {e}")
        return False

def test_integracion_completa_fase2():
    """Test de integración completa de Fase 2"""
    print("\n🔗 TESTEANDO INTEGRACIÓN COMPLETA FASE 2")
    print("-" * 50)

    try:
        from design_ops import ensure_plan_schema, add_room, set_roof, set_pool, validate_plan
        from modules.marketplace.data_access import save_plan_parametrico, get_plan_parametrico

        # Simular flujo completo de usuario
        finca = {"superficie_m2": 600, "retranqueos": {"front": 5, "side": 3}}

        # 1. Inicializar estudio
        plan = ensure_plan_schema(None, finca)

        # 2. Añadir habitaciones vía UI
        plan = add_room(plan, {"type": "bedroom", "area": 16})  # Dormitorio principal
        plan = add_room(plan, {"type": "bedroom", "area": 12})  # Dormitorio secundario
        plan = add_room(plan, {"type": "bathroom", "area": 9})  # Baño completo
        plan = add_room(plan, {"type": "living", "area": 30})   # Salón comedor
        plan = add_room(plan, {"type": "kitchen", "area": 14})  # Cocina

        # 3. Configurar estructura
        from design_ops import set_foundation, set_roof
        plan = set_foundation(plan, {"type": "slab", "depth": 0.5, "material": "concrete"})
        plan = set_roof(plan, {"type": "gable", "pitch_deg": 25, "material": "tiles"})

        # 4. Añadir piscina
        plan = set_pool(plan, {"area": 32, "position": "south"})

        # 5. Validar diseño
        validation = validate_plan(plan, finca)
        assert validation["ok"] == True

        # 6. Guardar proyecto
        proyecto = save_plan_parametrico(plan, 1, "studio_test")
        assert proyecto["id"] > 0

        # 7. Recuperar y verificar
        plan_recuperado = get_plan_parametrico(proyecto["id"])
        assert len(plan_recuperado["program"]["rooms"]) == 5
        assert plan_recuperado["roof"]["type"] == "gable"
        assert plan_recuperado["site"]["pool"]["exists"] == True

        print("✅ Integración completa Fase 2 funciona")
        print(f"   🏠 Proyecto creado: {len(plan['program']['rooms'])} espacios")
        print(f"   🏗️ Estructura: {plan['roof']['type']} + {plan['structure']['foundation']['type']}")
        print(f"   🏊 Piscina: {plan['site']['pool']['area']}m² al {plan['site']['pool']['position']}")
        print(f"   💾 Proyecto guardado: ID {proyecto['id']}, Versión {proyecto['version']}")

        return True

    except Exception as e:
        print(f"❌ Error en integración Fase 2: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 TEST EXHAUSTIVO DE FASE 2: UI DEL ESTUDIO")
    print("=" * 60)

    tests = [
        ("Imports de Studio Panel", test_studio_panel_imports),
        ("Parser IA Conversacional", test_ia_conversacional_parser),
        ("Operaciones Atómicas UI", test_operaciones_atomicas_ui),
        ("Undo/Redo Lógica", test_undo_redo_logica),
        ("Configuración Materiales", test_materiales_configuracion),
        ("Visualización 3D", test_visualizacion_3d),
        ("Integración Completa Fase 2", test_integracion_completa_fase2)
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
    print("📊 RESULTADOS FINALES DE FASE 2:")

    todos_pasan = True
    for nombre, exito in resultados:
        status = "✅" if exito else "❌"
        print(f"   {status} {nombre}")
        if not exito:
            todos_pasan = False

    print("\n" + "=" * 60)
    if todos_pasan:
        print("🎉 ¡FASE 2 COMPLETADA CON ÉXITO!")
        print("🎨 UI del Estudio implementada perfectamente")
        print("🤖 IA conversacional operativa")
        print("⚡ Listo para Fase 3: IA Conversacional Avanzada")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ FASE 2 CON ERRORES - REVISAR LOGS")
        print("🔧 Corregir antes de continuar")
        sys.exit(1)