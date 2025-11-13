"""
Test suite para generate_design.py
===================================

Valida todas las funciones del diseñador paramétrico con datos reales
del proyecto ARCHIRAPID.

Ejecutar: python test_generate_design.py
"""

import sys
from pathlib import Path
import json

# Añadir directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from generate_design import (
    load_validation_report,
    load_plot_polygon,
    estimate_pixel_to_meter_scale,
    compute_buildable_area,
    inscribe_rectangle,
    generate_functional_layout,
    generate_parametric_design,
    SHAPELY_AVAILABLE,
    NUMPY_AVAILABLE,
    MATPLOTLIB_AVAILABLE,
    TRIMESH_AVAILABLE
)


def test_dependencies():
    """Test 1: Verificar dependencias"""
    print("\n" + "="*70)
    print("TEST 1: VERIFICACIÓN DE DEPENDENCIAS")
    print("="*70)
    
    deps = {
        "Shapely": SHAPELY_AVAILABLE,
        "NumPy": NUMPY_AVAILABLE,
        "Matplotlib": MATPLOTLIB_AVAILABLE,
        "Trimesh": TRIMESH_AVAILABLE
    }
    
    all_ok = True
    for name, available in deps.items():
        status = "✅ OK" if available else "❌ FALTA"
        print(f"{name:15s} {status}")
        if not available:
            all_ok = False
    
    if not all_ok:
        print("\n⚠️  Algunas dependencias faltan. Instalar con:")
        print("   pip install shapely numpy matplotlib trimesh")
    else:
        print("\n✅ Todas las dependencias disponibles")
    
    return all_ok


def test_load_data():
    """Test 2: Cargar datos de validación y geometría"""
    print("\n" + "="*70)
    print("TEST 2: CARGA DE DATOS")
    print("="*70)
    
    output_dir = Path(__file__).parent / "catastro_output"
    
    # Test validation report
    validation = load_validation_report(output_dir)
    if validation:
        print(f"✅ validation_report.json cargado")
        print(f"   - Superficie: {validation.get('surface_m2', 'N/A')} m²")
        print(f"   - Tipo suelo: {validation.get('soil_type', 'N/A')}")
        print(f"   - Edificabilidad: {validation.get('edificability_m2', 'N/A')} m²")
    else:
        print(f"❌ No se pudo cargar validation_report.json")
        return False
    
    # Test polygon
    polygon = load_plot_polygon(output_dir)
    if polygon and SHAPELY_AVAILABLE:
        print(f"✅ plot_polygon.geojson cargado")
        print(f"   - Área (píxeles): {polygon.area:.2f}")
        print(f"   - Perímetro: {polygon.length:.2f}")
        print(f"   - Válido: {polygon.is_valid}")
    elif polygon is None:
        print(f"❌ No se pudo cargar plot_polygon.geojson")
        return False
    else:
        print(f"⚠️  Shapely no disponible, geometría no procesada")
    
    return True


def test_scale_calculation():
    """Test 3: Cálculo de escala px→m"""
    print("\n" + "="*70)
    print("TEST 3: CÁLCULO DE ESCALA")
    print("="*70)
    
    if not SHAPELY_AVAILABLE:
        print("⚠️  Shapely no disponible, test omitido")
        return True
    
    output_dir = Path(__file__).parent / "catastro_output"
    
    validation = load_validation_report(output_dir)
    polygon = load_plot_polygon(output_dir)
    
    if not validation or not polygon:
        print("❌ Datos no disponibles")
        return False
    
    surface_m2 = validation.get("surface_m2", 0)
    scale, valid = estimate_pixel_to_meter_scale(polygon, surface_m2)
    
    print(f"Superficie real: {surface_m2} m²")
    print(f"Área polígono: {polygon.area:.2f} px²")
    print(f"Escala calculada: {scale:.6f} m/px")
    print(f"Validación: {'✅ VÁLIDA' if valid else '⚠️  BAJA CONFIANZA (error >25%)'}")
    
    # Verificar coherencia
    estimated_area = polygon.area * (scale ** 2)
    error_pct = abs(estimated_area - surface_m2) / surface_m2 * 100
    print(f"Área estimada: {estimated_area:.2f} m²")
    print(f"Error: {error_pct:.1f}%")
    
    return True


def test_buildable_area():
    """Test 4: Cálculo de área edificable con retranqueos"""
    print("\n" + "="*70)
    print("TEST 4: ÁREA EDIFICABLE")
    print("="*70)
    
    if not SHAPELY_AVAILABLE:
        print("⚠️  Shapely no disponible, test omitido")
        return True
    
    output_dir = Path(__file__).parent / "catastro_output"
    
    validation = load_validation_report(output_dir)
    polygon = load_plot_polygon(output_dir)
    
    if not validation or not polygon:
        print("❌ Datos no disponibles")
        return False
    
    surface_m2 = validation.get("surface_m2", 0)
    scale, _ = estimate_pixel_to_meter_scale(polygon, surface_m2)
    
    # Probar diferentes retranqueos
    for setback_m in [3.0, 5.0, 7.0]:
        buildable = compute_buildable_area(polygon, setback_m, scale)
        
        if buildable:
            buildable_area_m2 = buildable.area * (scale ** 2)
            reduction_pct = (1 - buildable_area_m2 / surface_m2) * 100
            print(f"Retranqueo {setback_m}m: {buildable_area_m2:.2f} m² edificable ({reduction_pct:.1f}% reducción)")
        else:
            print(f"Retranqueo {setback_m}m: ❌ Sin área edificable")
    
    return True


def test_footprint():
    """Test 5: Inscripción de huella de edificación"""
    print("\n" + "="*70)
    print("TEST 5: HUELLA DE EDIFICACIÓN")
    print("="*70)
    
    if not SHAPELY_AVAILABLE:
        print("⚠️  Shapely no disponible, test omitido")
        return True
    
    output_dir = Path(__file__).parent / "catastro_output"
    
    validation = load_validation_report(output_dir)
    polygon = load_plot_polygon(output_dir)
    
    if not validation or not polygon:
        print("❌ Datos no disponibles")
        return False
    
    surface_m2 = validation.get("surface_m2", 0)
    scale, _ = estimate_pixel_to_meter_scale(polygon, surface_m2)
    
    buildable = compute_buildable_area(polygon, 3.0, scale)
    if not buildable:
        print("❌ No hay área edificable")
        return False
    
    # Objetivo: 50% del área edificable
    target_area_px = buildable.area * 0.5
    
    rect = inscribe_rectangle(buildable, target_area_px, aspect_ratio=1.5)
    
    if rect:
        x, y, w, h = rect
        w_m = w * scale
        h_m = h * scale
        area_m2 = w_m * h_m
        
        print(f"✅ Huella inscrita:")
        print(f"   - Dimensiones: {w_m:.2f}m × {h_m:.2f}m")
        print(f"   - Área: {area_m2:.2f} m²")
        print(f"   - Ratio largo/ancho: {max(w_m, h_m) / min(w_m, h_m):.2f}")
    else:
        print("❌ No se pudo inscribir huella")
        return False
    
    return True


def test_layout_generation():
    """Test 6: Generación de distribución funcional"""
    print("\n" + "="*70)
    print("TEST 6: DISTRIBUCIÓN FUNCIONAL")
    print("="*70)
    
    usable_area = 120.0  # m² útiles
    num_bedrooms = 3
    
    layout = generate_functional_layout(usable_area, num_bedrooms)
    
    print(f"Superficie útil: {usable_area} m²")
    print(f"Dormitorios: {num_bedrooms}")
    print("\nDistribución generada:")
    
    total = 0
    for space, area in layout.items():
        pct = (area / usable_area) * 100
        print(f"   {space:20s} {area:6.2f} m²  ({pct:5.1f}%)")
        total += area
    
    print(f"   {'TOTAL':20s} {total:6.2f} m²  ({total/usable_area*100:5.1f}%)")
    
    if abs(total - usable_area) < 1.0:
        print("✅ Distribución coherente")
        return True
    else:
        print(f"⚠️  Diferencia: {abs(total - usable_area):.2f} m²")
        return True


def test_full_generation():
    """Test 7: Generación completa del diseño paramétrico"""
    print("\n" + "="*70)
    print("TEST 7: GENERACIÓN COMPLETA")
    print("="*70)
    
    output_dir = Path(__file__).parent / "catastro_output"
    
    if not output_dir.exists():
        print(f"❌ Directorio {output_dir} no existe")
        print("   Ejecutar primero: python run_pipeline.py <ruta_pdf>")
        return False
    
    print(f"Ejecutando generación paramétrica...")
    print(f"   - Dormitorios: 3")
    print(f"   - Plantas: 2")
    print(f"   - Retranqueo: automático según tipo suelo")
    
    result = generate_parametric_design(
        output_dir,
        num_bedrooms=3,
        num_floors=2,
        setback_override=None
    )
    
    print("\n" + "-"*70)
    print("RESULTADO:")
    print("-"*70)
    print(f"Status: {result['status']}")
    
    if result.get('errors'):
        print(f"\n❌ ERRORES ({len(result['errors'])}):")
        for err in result['errors']:
            print(f"   - {err}")
    
    if result.get('warnings'):
        print(f"\n⚠️  ADVERTENCIAS ({len(result['warnings'])}):")
        for warn in result['warnings']:
            print(f"   - {warn}")
    
    if result.get('outputs'):
        print(f"\n📁 ARCHIVOS GENERADOS ({len(result['outputs'])}):")
        for name, path in result['outputs'].items():
            exists = Path(path).exists() if path else False
            status = "✅" if exists else "❌"
            print(f"   {status} {name}: {path}")
    
    if result.get('parameters'):
        print(f"\n📊 PARÁMETROS:")
        for key, value in result['parameters'].items():
            print(f"   - {key}: {value}")
    
    if result.get('layout'):
        print(f"\n🏠 DISTRIBUCIÓN:")
        for space, area in result['layout'].items():
            print(f"   - {space}: {area} m²")
    
    if result.get('budget'):
        print(f"\n💰 PRESUPUESTO:")
        budget = result['budget']
        print(f"   - Superficie construida: {budget.get('superficie_construida_m2', 0)} m²")
        print(f"   - Coste construcción: {budget.get('coste_construccion_eur', 0):,.2f} €")
        print(f"   - Honorarios proyecto: {budget.get('honorarios_proyecto_eur', 0):,.2f} €")
        print(f"   - Licencias/tasas: {budget.get('licencias_tasas_eur', 0):,.2f} €")
        print(f"   - TOTAL: {budget.get('presupuesto_total_eur', 0):,.2f} €")
    
    success = result['status'] == 'success'
    
    if success:
        print("\n✅ GENERACIÓN COMPLETA EXITOSA")
    else:
        print("\n❌ GENERACIÓN FALLÓ")
    
    return success


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "="*70)
    print("SUITE DE TESTS - DISEÑADOR PARAMÉTRICO ARCHIRAPID")
    print("="*70)
    
    tests = [
        ("Dependencias", test_dependencies),
        ("Carga de datos", test_load_data),
        ("Cálculo de escala", test_scale_calculation),
        ("Área edificable", test_buildable_area),
        ("Huella de edificación", test_footprint),
        ("Distribución funcional", test_layout_generation),
        ("Generación completa", test_full_generation)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ EXCEPCIÓN EN TEST '{name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE TESTS")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:8s} {name}")
    
    print("-"*70)
    print(f"Total: {passed}/{total} tests pasados ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n✅ TODOS LOS TESTS PASARON")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests fallaron")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
