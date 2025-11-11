#!/usr/bin/env python3
"""Script para verificar propiedades de las imágenes generadas."""

from PIL import Image
import os

output_dir = "catastro_output"

images = [
    "page_1.png",
    "page_1_processed.png",
    "contours_visualization.png"
]

print("=" * 60)
print("VERIFICACIÓN DE IMÁGENES GENERADAS")
print("=" * 60)

for img_name in images:
    img_path = os.path.join(output_dir, img_name)
    if os.path.exists(img_path):
        img = Image.open(img_path)
        file_size_kb = os.path.getsize(img_path) / 1024
        
        print(f"\n{img_name}:")
        print(f"  Dimensiones: {img.size[0]} x {img.size[1]} px")
        print(f"  Modo color: {img.mode}")
        print(f"  Tamaño: {file_size_kb:.1f} KB")
    else:
        print(f"\n{img_name}: NO EXISTE")

print("\n" + "=" * 60)
