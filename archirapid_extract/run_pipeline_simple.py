# run_pipeline_simple.py - Pipeline sin emojis (compatible Windows cmd)
# -*- coding: utf-8 -*-
"""
Pipeline de extracción de notas catastrales - ArchiRapid MVP
Versión simple sin emojis para compatibilidad con consola Windows

Ejecuta los 4 scripts en secuencia.
"""

import subprocess
import sys
from pathlib import Path
import time
import os
import io

# Forzar UTF-8 en Windows
if sys.platform == "win32":
    # Configurar consola y streams
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Scripts a ejecutar en orden
SCRIPTS = [
    ("extract_pdf.py", "[1/4] Extraccion de PDF"),
    ("ocr_and_preprocess.py", "[2/4] OCR y preprocesado"),
    ("vectorize_plan.py", "[3/4] Vectorizacion de plano"),
    ("compute_edificability.py", "[4/4] Calculo de edificabilidad")
]

def run_script(script_name, description):
    """Ejecuta un script y retorna True si fue exitoso"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    
    try:
        # Establecer UTF-8 para el subprocess
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=env
        )
        print(result.stdout)
        if result.stderr:
            print("WARNING:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR ejecutando {script_name}:")
        print(e.stdout)
        print(e.stderr)
        return False
    except Exception as e:
        print(f"ERROR inesperado: {e}")
        return False

def main():
    print("ArchiRapid - Pipeline de Extraccion Catastral")
    print("="*60)
    
    # Verificar que existe Catastro.pdf
    pdf_path = Path("Catastro.pdf")
    if not pdf_path.exists():
        print(f"ERROR: No se encuentra 'Catastro.pdf'")
        print(f"Coloca tu PDF catastral en: {pdf_path.absolute()}")
        print(f"\nTIP: Genera un PDF de prueba con: python create_test_pdf.py")
        sys.exit(1)
    
    print(f"OK - PDF encontrado: {pdf_path.absolute()}")
    
    # Ejecutar pipeline
    start_time = time.time()
    failed = []
    
    for script, description in SCRIPTS:
        if not run_script(script, description):
            failed.append(script)
            break
    
    elapsed = time.time() - start_time
    
    # Resumen final
    print(f"\n{'='*60}")
    if not failed:
        print("PIPELINE COMPLETADO EXITOSAMENTE")
        print(f"Tiempo total: {elapsed:.2f} segundos")
        print(f"\nResultados guardados en: catastro_output/")
        print("\nArchivos generados:")
        output_dir = Path("catastro_output")
        if output_dir.exists():
            for file in sorted(output_dir.iterdir()):
                if file.is_file():
                    size_kb = file.stat().st_size / 1024
                    print(f"  - {file.name} ({size_kb:.1f} KB)")
        
        print("\nArchivos principales:")
        print("  - edificability.json -> Superficie y edificabilidad")
        print("  - plot_polygon.geojson -> Poligono del lindero")
        print("  - contours_visualization.png -> Visualizacion de contornos")
        
    else:
        print("PIPELINE FALLO")
        print(f"Scripts fallidos: {', '.join(failed)}")
        sys.exit(1)
    
    print("="*60)

if __name__ == "__main__":
    main()
