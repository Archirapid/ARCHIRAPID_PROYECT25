# vectorize_plan.py
import cv2
import numpy as np
from pathlib import Path
from shapely.geometry import Polygon, mapping
import json
import sys

IN_DIR = Path("catastro_output")
proc_path = IN_DIR / "page_1_processed.png"

# Validate input
if not IN_DIR.exists():
    print(f"❌ ERROR: Directorio no encontrado: {IN_DIR.absolute()}")
    print("   Ejecuta primero 'extract_pdf.py'")
    sys.exit(1)

if not proc_path.exists():
    print(f"❌ ERROR: Imagen procesada no encontrada: {proc_path}")
    print("   Ejecuta primero 'ocr_and_preprocess.py'")
    sys.exit(1)

print(f"🔍 Vectorizando contornos de: {proc_path}")

# Load processed image
img = cv2.imread(str(proc_path), cv2.IMREAD_GRAYSCALE)
if img is None:
    print(f"❌ ERROR: No se pudo cargar la imagen {proc_path}")
    sys.exit(1)

# Find contours
contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print(f"  ✓ Encontrados {len(contours)} contornos")

if not contours:
    print("❌ No se encontraron contornos. Verifica que la imagen esté binarizada correctamente.")
    sys.exit(1)

# Sort contours by area (largest first)
areas = [(cv2.contourArea(cnt), i, cnt) for i, cnt in enumerate(contours)]
areas.sort(reverse=True, key=lambda x: x[0])

# Filter contours with significant area (> 1000 px²)
significant_contours = [(area, idx, cnt) for area, idx, cnt in areas if area > 1000]

if not significant_contours:
    print("⚠️  No se encontraron contornos significativos (área > 1000 px²)")
    significant_contours = areas[:1]  # Use largest anyway

print(f"  ✓ {len(significant_contours)} contornos significativos detectados")

# Process the largest contour (likely the plot boundary)
largest_area, largest_idx, largest_cnt = significant_contours[0]
print(f"  ✓ Contorno principal: área={largest_area:.0f} px², perímetro={cv2.arcLength(largest_cnt, True):.0f} px")

# Approximate polygon to reduce points
epsilon = 0.01 * cv2.arcLength(largest_cnt, True)
approx = cv2.approxPolyDP(largest_cnt, epsilon, True)
pts = approx.reshape(-1, 2).tolist()
print(f"  ✓ Polígono aproximado a {len(pts)} vértices")

# Convert to shapely polygon and simplify
try:
    poly = Polygon(pts)
    if not poly.is_valid:
        print("⚠️  Polígono inválido, intentando reparar...")
        poly = poly.buffer(0)  # Fix invalid polygon
    
    poly_simpl = poly.simplify(2.0, preserve_topology=True)
    print(f"  ✓ Polígono simplificado a {len(list(poly_simpl.exterior.coords))} puntos")
    
    # Create GeoJSON
    geojson = mapping(poly_simpl)
    feature = {
        "type": "Feature",
        "properties": {
            "source": "auto_vectorize",
            "area_px2": float(poly_simpl.area),
            "perimeter_px": float(poly_simpl.length),
            "vertices": len(list(poly_simpl.exterior.coords)) - 1  # -1 because last == first
        },
        "geometry": geojson
    }
    
    out_geojson = IN_DIR / "plot_polygon.geojson"
    with open(out_geojson, "w", encoding="utf-8") as f:
        json.dump(feature, f, indent=2, ensure_ascii=False)
    
    print(f"✅ GeoJSON guardado: {out_geojson}")
    
except Exception as e:
    print(f"❌ Error al crear polígono: {e}")
    sys.exit(1)

# Save visualization: draw contour on original image
try:
    # Load original image for visualization
    orig_img_path = IN_DIR / "page_1.png"
    if orig_img_path.exists():
        vis_img = cv2.imread(str(orig_img_path))
        # Draw the largest contour in green
        cv2.drawContours(vis_img, [largest_cnt], -1, (0, 255, 0), 3)
        # Draw all significant contours in blue
        for area, idx, cnt in significant_contours[1:6]:  # top 5
            cv2.drawContours(vis_img, [cnt], -1, (255, 0, 0), 2)
        
        vis_path = IN_DIR / "contours_visualization.png"
        cv2.imwrite(str(vis_path), vis_img)
        print(f"✅ Visualización guardada: {vis_path}")
except Exception as e:
    print(f"⚠️  No se pudo crear visualización: {e}")

# Save top contours info
contours_info = []
for i, (area, idx, cnt) in enumerate(significant_contours[:5]):
    contours_info.append({
        "rank": i + 1,
        "area_px2": float(area),
        "perimeter_px": float(cv2.arcLength(cnt, True)),
        "vertices": len(cnt)
    })

summary = {
    "total_contours": len(contours),
    "significant_contours": len(significant_contours),
    "main_polygon": {
        "area_px2": float(poly_simpl.area),
        "perimeter_px": float(poly_simpl.length),
        "vertices": len(list(poly_simpl.exterior.coords)) - 1,
        "bounds": list(poly_simpl.bounds)  # (minx, miny, maxx, maxy)
    },
    "top_contours": contours_info
}

summary_path = IN_DIR / "vectorization_summary.json"
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print(f"✅ Resumen de vectorización: {summary_path}")
print(f"✅ Vectorización completada. Polígono principal: {len(list(poly_simpl.exterior.coords))-1} vértices, área={poly_simpl.area:.0f} px²")
