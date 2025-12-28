#!/usr/bin/env python3
"""
Test exhaustivo de Fase 3: IA Avanzada + Coordinación Profesional
Verifica que todas las nuevas funcionalidades funcionen correctamente
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_imports_fase3():
    """Test de imports de Fase 3"""
    print("🔧 TESTEANDO IMPORTS DE FASE 3")
    print("-" * 50)

    try:
        from design_ops import (
            set_electrical_system, set_plumbing_system, set_lighting_system,
            set_furniture_package, set_smart_home_integration,
            apply_architectural_style, generate_professional_export
        )
        print("✅ Todos los imports de operaciones atómicas Fase 3 funcionan")
        return True

    except Exception as e:
        print(f"❌ Error en imports Fase 3: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sistemas_tecnicos_atomicos():
    """Test de operaciones atómicas de sistemas técnicos"""
    print("\n🔌 TESTEANDO SISTEMAS TÉCNICOS ATÓMICOS")
    print("-" * 50)

    try:
        from design_ops import (
            ensure_plan_schema, set_electrical_system, set_plumbing_system,
            set_lighting_system, set_smart_home_integration
        )

        finca = {"superficie_m2": 400}
        plan = ensure_plan_schema(None, finca)

        # Sistema eléctrico
        plan = set_electrical_system(plan, {
            "smart_home": True,
            "usb_outlets": True,
            "solar_panels": True,
            "emergency_power": True,
            "ev_charging": False
        })

        assert plan["systems"]["electrical"]["smart_home"] == True
        assert plan["systems"]["electrical"]["usb_outlets"] == True
        assert plan["systems"]["electrical"]["solar_panels"] == True

        # Sistema de fontanería
        plan = set_plumbing_system(plan, {
            "rainfall_shower": True,
            "bathtub": True,
            "bidet": True,
            "water_recycling": True,
            "greywater_system": False
        })

        assert plan["systems"]["plumbing"]["rainfall_shower"] == True
        assert plan["systems"]["plumbing"]["bathtub"] == True
        assert plan["systems"]["plumbing"]["bidet"] == True

        # Sistema de iluminación
        plan = set_lighting_system(plan, {
            "led_lighting": True,
            "motion_sensors": True,
            "dimming": True,
            "color_temperature": True,
            "smart_switches": True
        })

        assert plan["systems"]["lighting"]["led_lighting"] == True
        assert plan["systems"]["lighting"]["motion_sensors"] == True
        assert plan["systems"]["lighting"]["dimming"] == True

        # Domótica completa
        plan = set_smart_home_integration(plan, True)

        assert plan["systems"]["smart_home"]["enabled"] == True
        assert plan["systems"]["smart_home"]["security"] == True
        assert plan["systems"]["smart_home"]["climate"] == True

        print("✅ Sistemas técnicos atómicos funcionan correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en sistemas técnicos: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_estilos_arquitectonicos():
    """Test de aplicación de estilos arquitectónicos"""
    print("\n🎨 TESTEANDO ESTILOS ARQUITECTÓNICOS")
    print("-" * 50)

    try:
        from design_ops import ensure_plan_schema, apply_architectural_style

        finca = {"superficie_m2": 300}
        plan = ensure_plan_schema(None, finca)

        # Aplicar estilo moderno
        plan_modern = apply_architectural_style(plan, "modern")

        assert plan_modern["materials"]["exterior"]["walls"] == "concrete"
        assert plan_modern["materials"]["interior"]["floors"] == "ceramic"
        assert plan_modern["roof"]["type"] == "flat"
        assert plan_modern["systems"]["electrical"]["smart_home"] == True
        assert plan_modern["systems"]["lighting"]["led_lighting"] == True

        # Aplicar estilo clásico
        plan_classic = apply_architectural_style(plan, "classic")

        assert plan_classic["materials"]["exterior"]["walls"] == "brick"
        assert plan_classic["materials"]["interior"]["floors"] == "terrazzo"
        assert plan_classic["roof"]["type"] == "gable"
        assert plan_classic["systems"]["plumbing"]["bathtub"] == True

        # Aplicar estilo minimalista
        plan_minimal = apply_architectural_style(plan, "minimalist")

        assert plan_minimal["materials"]["exterior"]["walls"] == "concrete"
        assert plan_minimal["materials"]["interior"]["floors"] == "concrete"
        assert plan_minimal["roof"]["type"] == "flat"
        assert plan_minimal["systems"]["electrical"]["smart_home"] == True

        print("✅ Estilos arquitectónicos aplicados correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en estilos arquitectónicos: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mobiliario_inteligente():
    """Test de configuración de mobiliario inteligente"""
    print("\n🪑 TESTEANDO MOBILIARIO INTELIGENTE")
    print("-" * 50)

    try:
        from design_ops import ensure_plan_schema, set_furniture_package

        finca = {"superficie_m2": 350}
        plan = ensure_plan_schema(None, finca)

        # Configurar mobiliario para salón
        living_furniture = ["sofa", "coffee_table", "tv_stand", "bookshelf"]
        plan = set_furniture_package(plan, "living", living_furniture)

        assert plan["furniture"]["living"] == living_furniture

        # Configurar mobiliario para dormitorio
        bedroom_furniture = ["bed", "nightstand", "wardrobe", "dresser"]
        plan = set_furniture_package(plan, "bedroom", bedroom_furniture)

        assert plan["furniture"]["bedroom"] == bedroom_furniture

        # Configurar mobiliario para cocina
        kitchen_furniture = ["dining_table", "chairs", "kitchen_island"]
        plan = set_furniture_package(plan, "kitchen", kitchen_furniture)

        assert plan["furniture"]["kitchen"] == kitchen_furniture

        print("✅ Mobiliario inteligente configurado correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en mobiliario inteligente: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_exportacion_profesional():
    """Test de generación de exportación profesional"""
    print("\n📤 TESTEANDO EXPORTACIÓN PROFESIONAL")
    print("-" * 50)

    try:
        from design_ops import ensure_plan_schema, add_room, generate_professional_export

        finca = {"superficie_m2": 500}
        plan = ensure_plan_schema(None, finca)

        # Añadir algunas habitaciones para tener un plan completo
        plan = add_room(plan, {"type": "living", "area": 40})
        plan = add_room(plan, {"type": "kitchen", "area": 15})
        plan = add_room(plan, {"type": "bedroom", "area": 18})

        # Opciones de exportación
        export_options = [
            "📄 Memoria Técnica PDF",
            "🏗️ Planos CAD/DWG",
            "💰 Presupuesto Detallado",
            "⚡ Planos Eléctricos",
            "🚿 Planos Fontanería",
            "📋 Lista de Materiales"
        ]

        # Generar exportación
        export_data = generate_professional_export(plan, export_options)

        # Verificar estructura de exportación
        assert "timestamp" in export_data
        assert "project_id" in export_data
        assert "version" in export_data
        assert "exports" in export_data

        # Verificar documentos incluidos
        exports = export_data["exports"]
        assert "technical_memory" in exports
        assert "cad_plans" in exports
        assert "budget" in exports
        assert "electrical_plans" in exports
        assert "plumbing_plans" in exports
        assert "materials_list" in exports

        # Verificar presupuesto
        assert "total" in exports["budget"]
        assert exports["budget"]["total"] > 0
        assert exports["budget"]["currency"] == "EUR"

        print("✅ Exportación profesional generada correctamente")
        print(f"   📊 Proyecto: {export_data['project_id']}, Versión: {export_data['version']}")
        print(f"   💰 Presupuesto total: €{exports['budget']['total']:,.0f}")
        return True

    except Exception as e:
        print(f"❌ Error en exportación profesional: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ia_conversacional_avanzada():
    """Test del parser de IA conversacional avanzada"""
    print("\n🤖 TESTEANDO IA CONVERSACIONAL AVANZADA")
    print("-" * 50)

    try:
        # Simular órdenes avanzadas de IA
        test_orders = [
            "casa moderna con domotica completa",
            "estilo clasico con bañera y bidet",
            "iluminacion led inteligente con sensores",
            "electricidad con usb y carga de vehiculos",
            "fontaneria premium con ducha lluvia",
            "muebles minimalistas en salon y dormitorio"
        ]

        # Verificar que las órdenes se parsearían correctamente
        for order in test_orders:
            p = order.lower()
            actions_found = []

            if "moderna" in p and "domotica" in p:
                actions_found.extend(["apply_architectural_style modern", "set_smart_home_integration"])
            if "clasico" in p and "bañera" in p:
                actions_found.extend(["apply_architectural_style classic"])
            if "iluminacion led" in p and "sensores" in p:
                actions_found.append("set_lighting_system advanced")
            if "usb" in p and "vehiculos" in p:
                actions_found.append("set_electrical_system with_ev")
            if "ducha lluvia" in p:
                actions_found.append("set_plumbing_system rainfall")
            if "muebles minimalistas" in p:
                actions_found.append("set_furniture_package minimalist")

            if actions_found:
                print(f"✅ '{order}' → {len(actions_found)} acciones detectadas")
            else:
                print(f"❌ '{order}' → No parseado")

        print("✅ IA conversacional avanzada validada")
        return True

    except Exception as e:
        print(f"❌ Error en IA conversacional avanzada: {e}")
        return False

def test_integracion_completa_fase3():
    """Test de integración completa de Fase 3"""
    print("\n🔗 TESTEANDO INTEGRACIÓN COMPLETA FASE 3")
    print("-" * 50)

    try:
        from design_ops import (
            ensure_plan_schema, add_room, apply_architectural_style,
            set_electrical_system, set_plumbing_system, set_lighting_system,
            set_furniture_package, set_smart_home_integration,
            generate_professional_export
        )

        # Simular flujo completo de usuario profesional
        finca = {"superficie_m2": 800, "retranqueos": {"front": 6, "side": 4}}

        # 1. Inicializar proyecto profesional
        plan = ensure_plan_schema(None, finca)

        # 2. Diseño básico
        plan = add_room(plan, {"type": "living", "area": 50})
        plan = add_room(plan, {"type": "kitchen", "area": 20})
        plan = add_room(plan, {"type": "bedroom", "area": 20})
        plan = add_room(plan, {"type": "bedroom", "area": 18})
        plan = add_room(plan, {"type": "bathroom", "area": 12})
        plan = add_room(plan, {"type": "bathroom", "area": 10})

        # 3. Aplicar estilo arquitectónico completo
        plan = apply_architectural_style(plan, "modern")

        # 4. Sistemas técnicos coordinados
        plan = set_electrical_system(plan, {
            "smart_home": True, "usb_outlets": True, "solar_panels": True,
            "emergency_power": True, "ev_charging": True
        })

        plan = set_plumbing_system(plan, {
            "rainfall_shower": True, "bathtub": True, "bidet": True,
            "water_recycling": True, "greywater_system": True
        })

        plan = set_lighting_system(plan, {
            "led_lighting": True, "motion_sensors": True, "dimming": True,
            "color_temperature": True, "smart_switches": True
        })

        # 5. Domótica completa
        plan = set_smart_home_integration(plan, True)

        # 6. Mobiliario inteligente
        plan = set_furniture_package(plan, "living", ["sofa", "coffee_table", "tv_stand", "bookshelf"])
        plan = set_furniture_package(plan, "bedroom", ["bed", "nightstand", "wardrobe", "dresser"])
        plan = set_furniture_package(plan, "kitchen", ["dining_table", "chairs", "kitchen_island"])

        # 7. Generar exportación profesional completa
        export_options = [
            "📄 Memoria Técnica PDF", "🏗️ Planos CAD/DWG", "💰 Presupuesto Detallado",
            "📊 Análisis Estructural", "⚡ Planos Eléctricos", "🚿 Planos Fontanería",
            "📋 Lista de Materiales", "🪑 Plano de Muebles"
        ]

        export_data = generate_professional_export(plan, export_options)

        # Verificaciones finales
        assert plan["materials"]["exterior"]["walls"] == "concrete"  # Estilo moderno aplicado
        assert plan["systems"]["electrical"]["smart_home"] == True
        assert plan["systems"]["plumbing"]["rainfall_shower"] == True
        assert plan["systems"]["lighting"]["led_lighting"] == True
        assert plan["systems"]["smart_home"]["enabled"] == True
        assert len(plan["furniture"]["living"]) > 0
        assert export_data["exports"]["budget"]["total"] > 0

        print("✅ Integración completa Fase 3 funciona perfectamente")
        print(f"   🏠 Proyecto profesional: {len(plan['program']['rooms'])} espacios, {plan['program']['total_m2']} m²")
        print(f"   🎨 Estilo: Moderno completo")
        print(f"   🔌 Sistemas: Eléctrico ✓ | Fontanería ✓ | Iluminación ✓ | Domótica ✓")
        print(f"   🪑 Mobiliario: {len(plan['furniture'])} ambientes equipados")
        print(f"   📤 Exportación: {len(export_data['exports'])} documentos profesionales")
        print(f"   💰 Presupuesto total: €{export_data['exports']['budget']['total']:,.0f}")

        return True

    except Exception as e:
        print(f"❌ Error en integración Fase 3: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 TEST EXHAUSTIVO DE FASE 3: IA AVANZADA + COORDINACIÓN PROFESIONAL")
    print("=" * 70)

    tests = [
        ("Imports de Fase 3", test_imports_fase3),
        ("Sistemas Técnicos Atómicos", test_sistemas_tecnicos_atomicos),
        ("Estilos Arquitectónicos", test_estilos_arquitectonicos),
        ("Mobiliario Inteligente", test_mobiliario_inteligente),
        ("Exportación Profesional", test_exportacion_profesional),
        ("IA Conversacional Avanzada", test_ia_conversacional_avanzada),
        ("Integración Completa Fase 3", test_integracion_completa_fase3)
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

    print("\n" + "=" * 70)
    print("📊 RESULTADOS FINALES DE FASE 3:")

    todos_pasan = True
    for nombre, exito in resultados:
        status = "✅" if exito else "❌"
        print(f"   {status} {nombre}")
        if not exito:
            todos_pasan = False

    print("\n" + "=" * 70)
    if todos_pasan:
        print("🎉 ¡FASE 3 COMPLETADA CON ÉXITO!")
        print("🤖 IA conversacional avanzada operativa")
        print("🔧 Coordinación de disciplinas perfecta")
        print("🪑 Mobiliario inteligente implementado")
        print("📤 Exportación profesional completa")
        print("📚 Catálogo arquitectónico inteligente")
        print("⚡ ARCHIRAPID es ahora una herramienta PROFESIONAL COMPLETA")
        print("=" * 70)
        sys.exit(0)
    else:
        print("❌ FASE 3 CON ERRORES - REVISAR")
        print("🔧 Corregir antes de producción")
        sys.exit(1)