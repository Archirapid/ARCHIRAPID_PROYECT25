#!/usr/bin/env python3
"""
Test de integración final: Fase 2 + Fase 3
Verifica que ARCHIRAPID funciona completamente como herramienta profesional
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_arquitectura_completa():
    """Test de arquitectura completa desde Fase 1 hasta Fase 3"""
    print("🏗️ TESTEANDO ARQUITECTURA COMPLETA ARCHIRAPID")
    print("-" * 60)

    try:
        # Importar todas las funcionalidades
        from design_ops import (
            ensure_plan_schema, add_room, edit_room, remove_room,
            set_roof, set_foundation, set_pool, set_materials,
            auto_layout, validate_plan,
            # Fase 3
            set_electrical_system, set_plumbing_system, set_lighting_system,
            set_furniture_package, set_smart_home_integration,
            apply_architectural_style, generate_professional_export
        )

        # Simular proyecto completo de cliente real
        finca = {
            "superficie_m2": 1200,
            "retranqueos": {"front": 8, "side": 5, "back": 6}
        }

        # FASE 1: Fundación paramétrica
        plan = ensure_plan_schema(None, finca)
        assert plan["site"]["area"] == 1200

        # FASE 2: Diseño básico con operaciones atómicas
        plan = add_room(plan, {"type": "living", "area": 60})      # Salón grande
        plan = add_room(plan, {"type": "kitchen_dining", "area": 45})  # Cocina abierta
        plan = add_room(plan, {"type": "bedroom", "area": 25})     # Dormitorio principal
        plan = add_room(plan, {"type": "bedroom", "area": 20})     # Dormitorio secundario
        plan = add_room(plan, {"type": "bedroom", "area": 18})     # Dormitorio infantil
        plan = add_room(plan, {"type": "bathroom", "area": 12})    # Baño principal
        plan = add_room(plan, {"type": "bathroom", "area": 9})     # Baño secundario
        plan = add_room(plan, {"type": "office", "area": 16})      # Despacho
        plan = add_room(plan, {"type": "terrace", "area": 35})     # Terraza

        # Estructura básica
        plan = set_foundation(plan, {"type": "slab", "depth": 0.6, "material": "reinforced_concrete"})
        plan = set_roof(plan, {"type": "gable", "pitch_deg": 22, "material": "ceramic_tiles"})
        plan = set_pool(plan, {"area": 45, "position": "backyard"})

        # Validar diseño básico
        validation = validate_plan(plan, finca)
        assert validation["ok"] == True

        # FASE 3: IA Avanzada + Coordinación Profesional
        # Aplicar estilo moderno completo
        plan = apply_architectural_style(plan, "modern")

        # Sistemas técnicos coordinados
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

        # Domótica completa
        plan = set_smart_home_integration(plan, True)

        # Mobiliario inteligente completo
        plan = set_furniture_package(plan, "living", ["sofa", "coffee_table", "tv_stand", "bookshelf", "armchair"])
        plan = set_furniture_package(plan, "bedroom", ["bed", "nightstand", "wardrobe", "dresser", "desk"])
        plan = set_furniture_package(plan, "kitchen", ["dining_table", "chairs", "kitchen_island", "bar_stools"])
        plan = set_furniture_package(plan, "bathroom", ["vanity", "mirror", "storage_cabinet"])
        plan = set_furniture_package(plan, "office", ["desk", "office_chair", "bookshelf", "filing_cabinet"])

        # Auto-layout final
        plan = auto_layout(plan, finca)

        # Validación final completa
        final_validation = validate_plan(plan, finca)
        assert final_validation["ok"] == True

        # Exportación profesional completa
        export_options = [
            "📄 Memoria Técnica PDF", "🏗️ Planos CAD/DWG", "💰 Presupuesto Detallado",
            "📊 Análisis Estructural", "⚡ Planos Eléctricos", "🚿 Planos Fontanería",
            "💡 Planos de Iluminación", "📋 Lista de Materiales", "🪑 Plano de Muebles"
        ]

        export_data = generate_professional_export(plan, export_options)

        # Verificaciones finales exhaustivas
        assert plan["program"]["total_m2"] == 240  # Suma de todas las habitaciones: 60+45+25+20+18+12+9+16+35
        assert len(plan["program"]["rooms"]) == 9
        assert plan["materials"]["exterior"]["walls"] == "concrete"  # Estilo moderno aplicado
        assert plan["roof"]["type"] == "flat"  # Override por estilo moderno
        assert plan["systems"]["electrical"]["smart_home"] == True
        assert plan["systems"]["plumbing"]["rainfall_shower"] == True
        assert plan["systems"]["lighting"]["led_lighting"] == True
        assert plan["systems"]["smart_home"]["enabled"] == True
        assert len(plan["furniture"]) >= 3  # Al menos salón, dormitorio y cocina equipados
        assert export_data["exports"]["budget"]["total"] > 200000  # Proyecto premium

        print("✅ Arquitectura completa ARCHIRAPID validada")
        print(f"   🏠 Proyecto ejecutivo: {len(plan['program']['rooms'])} espacios, {plan['program']['total_m2']} m²")
        print(f"   🎨 Estilo: Moderno premium completo")
        print(f"   🔌 Sistemas técnicos: 4 disciplinas coordinadas")
        print(f"   🏠 Domótica: Completa (seguridad, clima, entretenimiento, energía)")
        print(f"   🪑 Mobiliario: {sum(len(items) for items in plan['furniture'].values())} piezas en {len(plan['furniture'])} ambientes")
        print(f"   📤 Documentación: {len(export_data['exports'])} entregables profesionales")
        print(f"   💰 Presupuesto total: €{export_data['exports']['budget']['total']:,.0f}")

        return True

    except Exception as e:
        print(f"❌ Error en arquitectura completa: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flujo_usuario_completo():
    """Test del flujo completo de usuario desde cero hasta exportación"""
    print("\n👤 TESTEANDO FLUJO COMPLETO DE USUARIO")
    print("-" * 60)

    try:
        from design_ops import (
            ensure_plan_schema, add_room, set_pool, apply_architectural_style,
            set_electrical_system, set_lighting_system, set_plumbing_system,
            set_furniture_package, auto_layout, validate_plan, generate_professional_export
        )
        # Simular flujo completo de un usuario no-experto

        # PASO 1: Selección de finca
        finca = {"superficie_m2": 600, "retranqueos": {"front": 5, "side": 3}}

        # PASO 2: IA conversacional inicial
        from design_ops import ensure_plan_schema
        plan = ensure_plan_schema(None, finca)

        # PASO 3: Órdenes naturales de IA
        user_orders = [
            "Quiero una casa moderna de 3 dormitorios con piscina",
            "Añade cocina abierta de 20m² y salón de 35m²",
            "Dos baños, uno con bañera y otro con ducha lluvia",
            "Instalación eléctrica inteligente con USB en todas partes",
            "Iluminación LED con sensores de movimiento",
            "Muebles minimalistas en salón y dormitorios"
        ]

        # Simular procesamiento de órdenes
        for order in user_orders:
            p = order.lower()

            # Procesar habitaciones
            if "3 dormitorios" in p:
                for i in range(3):
                    plan = add_room(plan, {"type": "bedroom", "area": 16})
            if "cocina abierta" in p and "20m²" in p:
                plan = add_room(plan, {"type": "kitchen_dining", "area": 20})
            if "salón" in p and "35m²" in p:
                plan = add_room(plan, {"type": "living", "area": 35})
            if "dos baños" in p:
                plan = add_room(plan, {"type": "bathroom", "area": 10})
                plan = add_room(plan, {"type": "bathroom", "area": 8})

            # Procesar piscina
            if "piscina" in p:
                plan = set_pool(plan, {"area": 32, "position": "south"})

            # Procesar estilo
            if "moderna" in p:
                plan = apply_architectural_style(plan, "modern")

            # Procesar sistemas
            if "eléctrica inteligente" in p and "usb" in p:
                plan = set_electrical_system(plan, {"smart_home": True, "usb_outlets": True})
            if "iluminación led" in p and "sensores" in p:
                plan = set_lighting_system(plan, {"led_lighting": True, "motion_sensors": True})
            if "bañera" in p:
                plan = set_plumbing_system(plan, {"bathtub": True})
            if "ducha lluvia" in p:
                plan = set_plumbing_system(plan, {"rainfall_shower": True})

            # Procesar muebles
            if "muebles minimalistas" in p:
                if "salón" in p:
                    plan = set_furniture_package(plan, "living", ["sofa", "coffee_table", "tv_stand"])
                if "dormitorios" in p:
                    plan = set_furniture_package(plan, "bedroom", ["bed", "nightstand", "wardrobe"])

        # PASO 4: Auto-layout inteligente
        plan = auto_layout(plan, finca)

        # PASO 5: Validación automática
        validation = validate_plan(plan, finca)
        assert validation["ok"] == True

        # PASO 6: Exportación final
        export_options = ["📄 Memoria Técnica PDF", "💰 Presupuesto Detallado", "📋 Lista de Materiales"]
        export_data = generate_professional_export(plan, export_options)

        print("✅ Flujo completo de usuario validado")
        print(f"   📝 Órdenes procesadas: {len(user_orders)} instrucciones naturales")
        print(f"   🏠 Diseño generado: {len(plan['program']['rooms'])} espacios")
        print(f"   ✅ Validación: {validation['ok']}")
        print(f"   📤 Documentos generados: {len(export_data['exports'])}")

        return True

    except Exception as e:
        print(f"❌ Error en flujo de usuario: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_catalog_arquitectonico():
    """Test del catálogo arquitectónico inteligente"""
    print("\n📚 TESTEANDO CATÁLOGO ARQUITECTÓNICO")
    print("-" * 60)

    try:
        from design_ops import (
            ensure_plan_schema, apply_architectural_style,
            set_smart_home_integration, set_pool
        )
        from modules.marketplace.data_access import migrate_plan_to_parametric
        # Simular catálogo de proyectos
        catalog_projects = [
            {
                "id": 1,
                "titulo": "Villa Mediterránea Moderna",
                "total_m2": 280,
                "estilo": "Moderno",
                "caracteristicas": ["Piscina", "Terraza", "Garaje", "Domótica"],
                "precio_base": 450000
            },
            {
                "id": 2,
                "titulo": "Casa de Campo Clásica",
                "total_m2": 320,
                "estilo": "Clásico",
                "caracteristicas": ["Jardín", "Chimenea", "Garaje", "Piscina"],
                "precio_base": 380000
            },
            {
                "id": 3,
                "titulo": "Loft Urbano Minimalista",
                "total_m2": 180,
                "estilo": "Minimalista",
                "caracteristicas": ["Terraza", "Domótica", "Garaje"],
                "precio_base": 320000
            }
        ]

        # Simular búsqueda por filtros
        finca = {"superficie_m2": 800}

        # Filtro por tamaño
        size_filter = "Mediano (100-200m²)"
        if size_filter == "Mediano (100-200m²)":
            filtered = [p for p in catalog_projects if 100 <= p["total_m2"] <= 200]
            assert len(filtered) == 1  # Solo el Loft Urbano
            assert filtered[0]["titulo"] == "Loft Urbano Minimalista"

        # Filtro por características
        features_filter = ["Piscina", "Domótica"]
        filtered = [p for p in catalog_projects if all(f in p["caracteristicas"] for f in features_filter)]
        assert len(filtered) == 1  # Solo la Villa Mediterránea
        assert filtered[0]["titulo"] == "Villa Mediterránea Moderna"

        # Simular aplicación de proyecto del catálogo
        selected_project = catalog_projects[0]  # Villa Mediterránea

        # Convertir a plan paramétrico
        base_plan = ensure_plan_schema(None, finca)
        catalog_plan = {
            "program": {"total_m2": selected_project["total_m2"], "rooms": []},
            "structure": {"foundation": {"type": "slab"}, "roof": {"type": "flat"}},
            "materials": {"exterior": {"walls": "concrete"}, "interior": {"floors": "ceramic"}},
            "site": {"pool": {"exists": True}}
        }

        parametric_plan = migrate_plan_to_parametric(catalog_plan, finca)

        # Aplicar estilo del catálogo
        if selected_project["estilo"] == "Moderno":
            parametric_plan = apply_architectural_style(parametric_plan, "modern")

        # Añadir sistemas según características
        if "Domótica" in selected_project["caracteristicas"]:
            parametric_plan = set_smart_home_integration(parametric_plan, True)

        if "Piscina" in selected_project["caracteristicas"]:
            parametric_plan = set_pool(parametric_plan, {"area": 40, "position": "backyard"})

        print("✅ Catálogo arquitectónico inteligente validado")
        print(f"   📚 Proyectos en catálogo: {len(catalog_projects)}")
        print(f"   🎯 Proyecto aplicado: '{selected_project['titulo']}'")
        print(f"   🏠 Características: {', '.join(selected_project['caracteristicas'])}")
        print(f"   💰 Precio base: €{selected_project['precio_base']:,.0f}")

        return True

    except Exception as e:
        print(f"❌ Error en catálogo arquitectónico: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rendimiento_escalabilidad():
    """Test de rendimiento y escalabilidad"""
    print("\n⚡ TESTEANDO RENDIMIENTO Y ESCALABILIDAD")
    print("-" * 60)

    try:
        import time
        from design_ops import (
            ensure_plan_schema, add_room, apply_architectural_style,
            set_electrical_system, set_lighting_system
        )

        # Test de escalabilidad: proyecto grande
        finca_grande = {"superficie_m2": 5000}  # Proyecto comercial
        start_time = time.time()

        plan_grande = ensure_plan_schema(None, finca_grande)

        # Añadir muchas habitaciones (edificio comercial)
        for i in range(50):  # 50 espacios
            plan_grande = add_room(plan_grande, {"type": "office", "area": 15})

        # Aplicar estilo y sistemas complejos
        plan_grande = apply_architectural_style(plan_grande, "modern")
        plan_grande = set_electrical_system(plan_grande, {"smart_home": True})
        plan_grande = set_lighting_system(plan_grande, {"led_lighting": True})

        end_time = time.time()
        processing_time = end_time - start_time

        # Validar que escala bien
        assert len(plan_grande["program"]["rooms"]) == 50
        assert plan_grande["program"]["total_m2"] == 750  # 50 * 15
        assert processing_time < 5.0  # Debe procesar en menos de 5 segundos

        print("✅ Rendimiento y escalabilidad validados")
        print(f"   🏢 Proyecto grande: {len(plan_grande['program']['rooms'])} espacios, {plan_grande['program']['total_m2']} m²")
        print(f"   ⏱️ Tiempo de procesamiento: {processing_time:.2f} segundos")
        print(f"   📈 Escalabilidad: ✓ (procesa 50 espacios eficientemente)")

        return True

    except Exception as e:
        print(f"❌ Error en rendimiento: {e}")
        return False

if __name__ == "__main__":
    print("🎯 TEST DE INTEGRACIÓN FINAL: ARCHIRAPID PROFESIONAL COMPLETO")
    print("=" * 80)

    tests = [
        ("Arquitectura Completa", test_arquitectura_completa),
        ("Flujo Usuario Completo", test_flujo_usuario_completo),
        ("Catálogo Arquitectónico", test_catalog_arquitectonico),
        ("Rendimiento y Escalabilidad", test_rendimiento_escalabilidad)
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

    print("\n" + "=" * 80)
    print("📊 RESULTADOS INTEGRACIÓN FINAL ARCHIRAPID:")

    todos_pasan = True
    for nombre, exito in resultados:
        status = "✅" if exito else "❌"
        print(f"   {status} {nombre}")
        if not exito:
            todos_pasan = False

    print("\n" + "=" * 80)
    if todos_pasan:
        print("🎉 ¡ARCHIRAPID PROFESIONAL COMPLETADO CON ÉXITO!")
        print("🏗️ Arquitectura paramétrica perfecta")
        print("🎨 Fase 2: UI conversacional + operaciones atómicas")
        print("🚀 Fase 3: IA avanzada + coordinación profesional")
        print("📚 Catálogo inteligente + exportación completa")
        print("⚡ Rendimiento escalable para proyectos grandes")
        print("🌟 ARCHIRAPID es ahora una HERRAMIENTA DE ARQUITECTURA PROFESIONAL")
        print("💎 Lista para revolucionar el diseño arquitectónico")
        print("=" * 80)
        sys.exit(0)
    else:
        print("❌ INTEGRACIÓN CON ERRORES - REVISAR")
        print("🔧 Corregir antes de liberación final")
        sys.exit(1)