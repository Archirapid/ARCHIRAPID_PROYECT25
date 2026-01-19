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
    ("../compute_edificability.py", "📊 Cálculo de edificabilidad")
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
    print("🚀 ArchiRapid - Pipeline de Extracción Catastral (AI-Enhanced)")
    print("="*60)
    
    # Verificar que existe Catastro.pdf
    pdf_path = Path("Catastro.pdf")
    OUTDIR = Path("catastro_output")
    
    if not pdf_path.exists():
        print(f"❌ ERROR: No se encuentra 'Catastro.pdf'")
        print(f"   Coloca tu PDF catastral en: {pdf_path.absolute()}")
        print(f"\n💡 TIP: Puedes generar un PDF de prueba ejecutando:")
        print(f"   python create_test_pdf.py")
        sys.exit(1)
        
    print(f"✅ PDF encontrado: {pdf_path.absolute()}")
    
    # Ejecutar pipeline con AI Extractor
    start_time = time.time()
    
    try:
        # Import dinámicamente el extractor de IA, que será implementado en el paso 5
        from .ai_extractor import extract_and_save
        
        report = extract_and_save(pdf_path, OUTDIR)
        elapsed = time.time() - start_time
        
    except ImportError:
        print("❌ ERROR: Módulo 'ai_extractor' no disponible o no implementado.")
        print("   Por favor, implementa 'archirapid_extract/ai_extractor.py' antes de ejecutar el pipeline principal.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ PIPELINE FALLÓ durante la ejecución de AI: {e}")
        sys.exit(1)
    
    # Resumen final (adaptado al nuevo output)
    print(f"\n{'='*60}")
    print("✅ PIPELINE COMPLETADO EXITOSAMENTE (AI)")
    print(f"⏱️  Tiempo total: {elapsed:.2f} segundos")
    print(f"\n📂 Resultados guardados en: {OUTDIR.absolute()}")
    print("\n🎯 Archivos principales:")
    print("   - edificability.json → Superficie y edificabilidad calculada (actualizada desde AI report)")
    print("   - ai_report.json → Resultado consolidado del modelo 1.5 Flash")
        
    print("="*60)

if __name__ == "__main__":
    main()
