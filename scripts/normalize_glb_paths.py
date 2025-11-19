#!/usr/bin/env python3
"""Normaliza rutas `modelo_3d_glb` en la tabla `projects`.

Este script convierte rutas relativas (por ejemplo: 'uploads/...') a rutas absolutas
basadas en la raíz del proyecto (`BASE`) y actualiza la BD si el archivo existe.

Solo actualiza `modelo_3d_glb` y es idempotente y seguro: no cambia si la ruta
ya es absoluta o no existe el archivo (no rompe nada).
"""
from pathlib import Path
from src import db as src_db
import os

BASE = src_db.BASE_PATH

def normalize():
    rows = src_db.get_all_projects()
    updated = 0
    changed = []
    for r in rows.itertuples(index=False):
        glb = getattr(r, 'modelo_3d_glb', None)
        if not glb:
            continue
        # already absolute and exists -> nothing to do
        if os.path.isabs(glb):
            if os.path.exists(glb):
                continue
        # Try to resolve relative path against base
        candidate = Path(BASE) / glb.replace('\\', '/')
        if candidate.exists():
            src_db.update_project_fields(r.id, {'modelo_3d_glb': str(candidate)})
            updated += 1
            changed.append({'id': r.id, 'title': getattr(r,'title', None), 'new_path': str(candidate)})

    print(f"Normalized {updated} project modelos 3D (.glb)")
    if changed:
        for c in changed:
            print(c)

if __name__ == '__main__':
    normalize()
