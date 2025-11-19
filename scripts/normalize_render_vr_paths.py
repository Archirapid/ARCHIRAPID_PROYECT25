#!/usr/bin/env python3
"""Script para normalizar rutas `render_vr` en la tabla `projects`.

Convierte rutas relativas (por ejemplo: 'uploads/file.zip') a rutas absolutas
basadas en la raíz del proyecto (`BASE`) y actualiza la BD si el archivo existe.
"""
from pathlib import Path
from src import db as src_db
import os

BASE = src_db.BASE_PATH

def normalize():
    rows = src_db.get_all_projects()
    updated = 0
    for r in rows.itertuples(index=False):
        rv = getattr(r, 'render_vr', None)
        if not rv:
            continue
        # already absolute
        if os.path.isabs(rv) and os.path.exists(rv):
            continue
        # try to resolve relative
        candidate = Path(BASE) / rv.replace('\\', '/')
        if candidate.exists():
            src_db.update_project_fields(r.id, {'render_vr': str(candidate)})
            updated += 1
    print(f"Normalized {updated} project render_vr entries")

if __name__ == '__main__':
    normalize()
