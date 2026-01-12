from src import db

# Obtener proyectos destacados (o todos si limit es alto)
projects = db.get_featured_projects(limit=20)  # Aumentar límite para encontrar los dos

for p in projects:
    title = p.get('title', '').lower()
    if 'prueba test proyecto a' in title or 'test casa 3b' in title:
        print(f"Proyecto: {p['title']}")
        print(f"ID: {p.get('id')}")
        print(f"Files completo: {p.get('files', {})}")
        fotos = p.get('files', {}).get('fotos', [])
        print(f"Galería fotos (tipo: {type(fotos)}): {fotos}")
        print(f"Longitud de galeria_fotos: {len(fotos) if isinstance(fotos, list) else 'No es lista'}")
        print("---")