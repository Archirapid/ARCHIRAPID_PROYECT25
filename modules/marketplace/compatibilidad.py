from modules.marketplace.utils import db_conn
from modules.marketplace.data_access import list_proyectos

def get_proyectos_compatibles(
    plot_id: int = None,
    client_budget: float = None,
    client_desired_area: float = None,
    client_parcel_size: float = None,
    client_email: str = None
) -> list:
    """
    Devuelve proyectos compatibles con criterios específicos.
    
    Si plot_id se proporciona: compatibilidad con finca específica
    Si no: búsqueda general por criterios
    
    Filtros aplicados:
    1. Superficie proyecto <= superficie_edificable de la finca (si plot_id)
    2. Precio proyecto <= presupuesto del cliente (opcional)
    3. Área construida ≈ área deseada (±20% tolerancia) (opcional)
    4. Parcela disponible >= parcela mínima requerida (opcional)
    5. Tipo compatible (residencial)
    6. Proyecto activo (is_active = 1)
    7. NO mostrar proyectos ya comprados por este cliente
    
    Args: 
        plot_id: ID de la finca (opcional)
        client_budget: Presupuesto máximo del cliente (opcional)
        client_desired_area: Área de construcción deseada (opcional)
        client_parcel_size: Tamaño de parcela disponible (opcional)
        client_email: Email del cliente para excluir comprados (opcional)
    
    Returns:
        Lista de proyectos compatibles con datos completos
    """
    from modules.marketplace.utils import db_conn
    import json
    
    conn = db_conn()
    cursor = conn.cursor()
    
    superficie_edificable = None
    
    # Si hay plot_id, obtener datos de la finca
    if plot_id:
        cursor.execute("""
            SELECT id, title, m2, superficie_edificable
            FROM plots
            WHERE id = ?
        """, (plot_id,))
        row = cursor.fetchone()
        
        if row:
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
            p.description,
            p.m2_construidos,
            p.area_m2,
            p.price,
            p.estimated_cost,
            p.price_memoria,
            p.price_cad,
            p.property_type,
            p.foto_principal,
            p.galeria_fotos,
            p.memoria_pdf,
            p.planos_pdf,
            p.planos_dwg,
            p.modelo_3d_glb,
            p.vr_tour,
            p.energy_rating,
            p.architect_id,
            p.architect_name,
            p.m2_parcela_minima,
            p.m2_parcela_maxima
        FROM projects p
        WHERE 1=1
    """
    
    params = []
    
    # Filtrar por superficie edificable (solo si hay plot_id)
    if superficie_edificable:
        query += """
            AND (
                (p.m2_construidos IS NOT NULL AND p.m2_construidos > 0 AND p.m2_construidos <= ?)
                OR (p.m2_construidos IS NULL AND p.area_m2 IS NOT NULL AND p.area_m2 > 0 AND p.area_m2 <= ?)
            )
        """
        params.extend([superficie_edificable, superficie_edificable])
    
    # Filtrar por presupuesto del cliente
    if client_budget:
        query += " AND (p.price <= ? OR p.price IS NULL)"
        params.append(client_budget)
    
    # Filtrar por área deseada (±20% tolerancia)
    if client_desired_area:
        min_area = client_desired_area * 0.8
        max_area = client_desired_area * 1.2
        query += """
            AND (
                (p.m2_construidos IS NOT NULL AND p.m2_construidos >= ? AND p.m2_construidos <= ?)
                OR (p.m2_construidos IS NULL AND p.area_m2 IS NOT NULL AND p.area_m2 >= ? AND p.area_m2 <= ?)
            )
        """
        params.extend([min_area, max_area, min_area, max_area])
    
    # Filtrar por parcela disponible
    if client_parcel_size:
        query += " AND (p.m2_parcela_minima IS NULL OR p.m2_parcela_minima <= ?)"
        params.append(client_parcel_size)
    
    # Filtrar por tipo (residencial)
    query += " AND (p.property_type LIKE '%residencial%' OR p.property_type IS NULL)"
    
    # Filtrar por activo
    query += " AND (p.is_active = 1 OR p.is_active IS NULL)"
    
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
        if row[11]:  # galeria_fotos
            try: 
                galeria = json.loads(row[11]) if isinstance(row[11], str) else row[11]
            except: 
                galeria = [row[11]] if row[11] else []
        
        proyecto = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "m2_construidos": row[3],
            "area_m2": row[4],
            "price": row[5],
            "estimated_cost": row[6],
            "price_memoria": row[7] or 1800,
            "price_cad": row[8] or 2500,
            "property_type": row[9] or "residencial",
            "foto_principal": row[10],
            "galeria_fotos": galeria,
            "memoria_pdf": row[12],
            "planos_pdf": row[13],
            "planos_dwg": row[14],
            "modelo_3d_glb": row[15],
            "vr_tour": row[16],
            "energy_rating": row[17],
            "architect_id": row[18],
            "architect_name": row[19],
            "m2_parcela_minima": row[20],
            "m2_parcela_maxima": row[21],
            # Datos calculados
            "fits_plot": superficie_edificable is not None and (
                (row[3] and row[3] <= superficie_edificable) or
                (not row[3] and row[4] and row[4] <= superficie_edificable)
            ),
            "superficie_disponible": superficie_edificable,
            "precio_total": (row[7] or 1800) + (row[8] or 2500)
        }
        compatibles.append(proyecto)
    
    return compatibles
    
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
        if row[11]:  # galeria_fotos
            try: 
                galeria = json.loads(row[11]) if isinstance(row[11], str) else row[11]
            except: 
                galeria = [row[11]] if row[11] else []
        
        proyecto = {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "m2_construidos": row[3],
            "area_m2": row[4],
            "price": row[5],
            "estimated_cost": row[6],
            "price_memoria": row[7] or 1800,
            "price_cad": row[8] or 2500,
            "property_type": row[9] or "residencial",
            "foto_principal": row[10],
            "galeria_fotos": galeria,
            "memoria_pdf": row[12],
            "planos_pdf": row[13],
            "planos_dwg": row[14],
            "modelo_3d_glb": row[15],
            "vr_tour": row[16],
            "energy_rating": row[17],
            "architect_id": row[18],
            "architect_name": row[19],
            "m2_parcela_minima": row[20],
            "m2_parcela_maxima": row[21],
            # Datos calculados
            "fits_plot": superficie_edificable is not None and (
                (row[3] and row[3] <= superficie_edificable) or
                (not row[3] and row[4] and row[4] <= superficie_edificable)
            ),
            "superficie_disponible": superficie_edificable,
            "precio_total": (row[7] or 1800) + (row[8] or 2500)
        }
        compatibles.append(proyecto)
    
    return compatibles