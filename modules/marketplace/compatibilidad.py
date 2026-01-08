from modules.marketplace.utils import db_conn
from modules.marketplace.data_access import list_proyectos

def get_proyectos_compatibles(
    plot_id: int,
    client_budget: float = None,
    client_email: str = None
) -> list:
    """
    Devuelve proyectos compatibles con una finca específica.
    
    Filtros aplicados:
    1.  Superficie proyecto <= superficie_edificable de la finca
    2. Precio proyecto <= presupuesto del cliente (si se proporciona)
    3. Tipo compatible (residencial)
    4. Proyecto activo (is_active = 1)
    5. NO mostrar proyectos ya comprados por este cliente
    
    Args: 
        plot_id:  ID de la finca
        client_budget: Presupuesto máximo del cliente (opcional)
        client_email:  Email del cliente para excluir comprados (opcional)
    
    Returns:
        Lista de proyectos compatibles con datos completos
    """
    from modules.marketplace.utils import db_conn
    import json
    
    conn = db_conn()
    cursor = conn.cursor()
    
    # 1. Obtener datos de la finca
    cursor. execute("""
        SELECT id, title, m2, superficie_edificable
        FROM plots
        WHERE id = ?
    """, (plot_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return []
    
    finca_m2 = row[2]
    superficie_edificable = row[3]
    
    # Si no tiene superficie_edificable, calcular 33% por defecto
    if not superficie_edificable:
        superficie_edificable = finca_m2 * 0.33 if finca_m2 else 0
    
    # 2. Construir query para proyectos
    query = """
        SELECT 
            p.id,
            p.title,
            p. description,
            p.m2_construidos,
            p.price,
            p.estimated_cost,
            p.price_memoria,
            p.price_cad,
            p. property_type,
            p. foto_principal,
            p.galeria_fotos,
            p.memoria_pdf,
            p.planos_pdf,
            p.planos_dwg,
            p.modelo_3d_glb,
            p.vr_tour,
            p. energy_rating,
            p.architect_id,
            p.architect_name
        FROM projects p
        WHERE 1=1
    """
    
    params = []
    
    # Filtrar por superficie edificable
    # Usar m2_construidos O area_m2 (el que tenga valor)
    query += """
        AND (
            (p.m2_construidos IS NOT NULL AND p.m2_construidos > 0 AND p.m2_construidos <= ?)
            OR (p.m2_construidos IS NULL AND p.area_m2 IS NOT NULL AND p.area_m2 > 0 AND p.area_m2 <= ?)
        )
    """
    params.extend([superficie_edificable, superficie_edificable])
    
    # Filtrar por tipo (residencial)
    query += " AND (p.property_type LIKE '%residencial%' OR p.property_type IS NULL)"
    
    # Filtrar por activo
    query += " AND (p.is_active = 1 OR p.is_active IS NULL)"
    
    # Filtrar por presupuesto del cliente
    if client_budget:
        query += " AND (p.price <= ?  OR p.price IS NULL)"
        params.append(client_budget)
    
    # Excluir proyectos ya comprados
    if client_email:
        query += """
            AND p.id NOT IN (
                SELECT proyecto_id 
                FROM ventas_proyectos 
                WHERE cliente_email = ? 
            )
        """
        params.append(client_email)
    
    query += " ORDER BY p.price ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # 3. Formatear resultados
    compatibles = []
    for row in rows:
        # Parsear galeria_fotos si es JSON
        galeria = []
        if row[10]:  # galeria_fotos
            try: 
                galeria = json.loads(row[10]) if isinstance(row[10], str) else row[10]
            except: 
                galeria = [row[10]] if row[10] else []
        
        proyecto = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "m2_construidos": row[3],
            "price":  row[4],
            "estimated_cost": row[5],
            "price_memoria": row[6] or 1800,
            "price_cad": row[7] or 2500,
            "property_type": row[8] or "residencial",
            "foto_principal": row[9],
            "galeria_fotos": galeria,
            "memoria_pdf": row[11],
            "planos_pdf":  row[12],
            "planos_dwg": row[13],
            "modelo_3d_glb": row[14],
            "vr_tour":  row[15],
            "energy_rating": row[16],
            "architect_id": row[17],
            "architect_name": row[18],
            # Datos calculados
            "fits_plot": True,
            "superficie_disponible": superficie_edificable,
            "precio_total": (row[6] or 1800) + (row[7] or 2500)
        }
        compatibles. append(proyecto)
    
    return compatibles