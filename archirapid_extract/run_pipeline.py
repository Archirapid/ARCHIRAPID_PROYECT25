# run_pipeline.py - Ejecuta el pipeline completo de extracción catastral
"""
Pipeline de extracción de notas catastrales - ArchiRapid MVP

Ejecuta los 4 scripts en secuencia:
1. extract_pdf.py - Extrae texto e imágenes del PDF
2. ocr_and_preprocess.py - OCR y preprocesado
3. vectorize_plan.py - Vectorización de linderos
4. compute_edificability.py - Cálculo de edificabilidad

Uso:
    python run_pipeline.py
    
Requisitos:
    - Archivo 'Catastro.pdf' en esta carpeta
    - Dependencias instaladas (pip install -r requirements.txt)
"""

import subprocess
import sys
from pathlib import Path
import time

# Scripts a ejecutar en orden
SCRIPTS = [
    ("extract_pdf.py", "📄 Extracción de PDF"),
    ("ocr_and_preprocess.py", "🖼️  OCR y preprocesado"),
    ("vectorize_plan.py", "🔍 Vectorización de plano"),
    ("compute_edificability.py", "📊 Cálculo de edificabilidad")
]

def run_script(script_name, description):
    """Ejecuta un script y retorna True si fue exitoso"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print(result.stdout)
        if result.stderr:
            print("⚠️  Warnings:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando {script_name}:")
        print(e.stdout)
        print(e.stderr)
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    print("🚀 ArchiRapid - Pipeline de Extracción Catastral")
    print("="*60)
    
    # Verificar que existe Catastro.pdf
    pdf_path = Path("Catastro.pdf")
    if not pdf_path.exists():
        print(f"❌ ERROR: No se encuentra 'Catastro.pdf'")
        print(f"   Coloca tu PDF catastral en: {pdf_path.absolute()}")
        print(f"\n💡 TIP: Puedes generar un PDF de prueba ejecutando:")
        print(f"   python create_test_pdf.py")
        sys.exit(1)
    
    print(f"✅ PDF encontrado: {pdf_path.absolute()}")
    
    # Ejecutar pipeline
    start_time = time.time()
    failed = []
    
    for script, description in SCRIPTS:
        if not run_script(script, description):
            failed.append(script)
            break  # Detener si algún script falla
    
    elapsed = time.time() - start_time
    
    # Resumen final
    print(f"\n{'='*60}")
    if not failed:
        print("✅ PIPELINE COMPLETADO EXITOSAMENTE")
        print(f"⏱️  Tiempo total: {elapsed:.2f} segundos")
        print(f"\n📂 Resultados guardados en: catastro_output/")
        print("\n📊 Archivos generados:")
        output_dir = Path("catastro_output")
        if output_dir.exists():
            for file in sorted(output_dir.iterdir()):
                if file.is_file():
                    size_kb = file.stat().st_size / 1024
                    print(f"   - {file.name} ({size_kb:.1f} KB)")
        
        print("\n🎯 Archivos principales:")
        print("   - edificability.json → Superficie y edificabilidad calculada")
        print("   - plot_polygon.geojson → Polígono del lindero")
        print("   - contours_visualization.png → Visualización de contornos")
        
    else:
        print("❌ PIPELINE FALLÓ")
        print(f"   Scripts fallidos: {', '.join(failed)}")
        print(f"   Revisa los mensajes de error arriba.")
        sys.exit(1)
    
    print("="*60)

if __name__ == "__main__":
    main()
