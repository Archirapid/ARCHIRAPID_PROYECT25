# modules/marketplace/marketplace_upload.py
"""
Marketplace de proyectos para arquitectos - ARCHIRAPID MVP
Permite subir proyectos completos (3D, RV, memoria, planos) al catálogo
"""

import streamlit as st
import json
import os
from typing import Dict, List, Optional, Tuple
from .data_access import save_proyecto, get_usuario
from .documentacion import generar_memoria_constructiva, generar_presupuesto_estimado
from src import db
from export_ops import generar_paquete_descarga

# === CONFIGURACIÓN ===
UPLOAD_DIR = "uploads/proyectos_arquitectos"
ALLOWED_EXTENSIONS = {
    '3d': ['obj', 'fbx', 'gltf', 'glb', 'dae'],
    'rv': ['jpg', 'png', 'jpeg', 'mp4', 'webm'],
    'pdf': ['pdf'],
    'cad': ['dxf', 'dwg', 'svg'],
    'json': ['json']
}

os.makedirs(UPLOAD_DIR, exist_ok=True)


def _sync_project_characteristics(project_id: str):
    """Sincroniza `characteristics_json` a columnas de la fila `project_id` en `projects`.
    Se usa para asegurar que nuevas publicaciones rellenen las columnas esperadas.
    """
    try:
        import json as _json
        from src import db as _db
        conn = _db.get_conn()
        cur = conn.cursor()

        # Asegurar columnas opcionales existen (ALTER TABLE seguro)
        try:
            cur.execute("ALTER TABLE projects ADD COLUMN modelo_3d_path TEXT")
            conn.commit()
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE projects ADD COLUMN piscina INTEGER DEFAULT 0")
            conn.commit()
        except Exception:
            pass

        cur.execute("SELECT characteristics_json FROM projects WHERE id=?", (project_id,))
        row = cur.fetchone()
        if not row:
            return
        ch_raw = row[0]
        if not ch_raw:
            return
        try:
            ch = _json.loads(ch_raw)
        except Exception:
            return

        # Normalizar y preparar updates
        habitaciones = ch.get('habitaciones')
        banos = ch.get('baños') if 'baños' in ch else ch.get('banos')
        plantas = ch.get('plantas')
        m2 = ch.get('m2_construidos')
        piscina = 1 if ch.get('piscina') else 0
        garaje = 1 if ch.get('garaje') else 0
        imagenes = ch.get('imagenes')
        modelo_3d = ch.get('modelo_3d_path')

        updates = {}
        if habitaciones is not None:
            try:
                updates['habitaciones'] = int(habitaciones)
            except Exception:
                pass
        if banos is not None:
            try:
                updates['banos'] = int(banos)
            except Exception:
                pass
        if plantas is not None:
            try:
                updates['plantas'] = int(plantas)
            except Exception:
                pass
        if m2 is not None:
            try:
                updates['m2_construidos'] = float(m2)
            except Exception:
                pass
        updates['garaje'] = int(bool(garaje))
        updates['piscina'] = int(bool(piscina))
        if imagenes:
            updates['foto_principal'] = imagenes
        if modelo_3d:
            updates['modelo_3d_path'] = modelo_3d

        if not updates:
            return

        set_clause = ','.join([f"{k}=?" for k in updates.keys()])
        values = tuple(updates.values()) + (project_id,)
        sql = f"UPDATE projects SET {set_clause} WHERE id=?"
        cur.execute(sql, values)
        conn.commit()
    except Exception:
        # no hacer crash en la UI
        return
    finally:
        try:
            conn.close()
        except Exception:
            pass

# === FUNCIONES PRINCIPALES ===
def upload_proyecto_form(arquitecto_id: int) -> Optional[Dict]:
    """
    Formulario para subir proyecto de arquitecto

    Args:
        arquitecto_id: ID del arquitecto que sube el proyecto

    Returns:
        Dict con datos del proyecto creado, o None si cancelado
    """
    st.header("🏗️ Subir Proyecto Arquitectónico")

    with st.form("upload_proyecto_form"):
        # Información básica
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del proyecto", placeholder="Casa Moderna Minimalista")
            descripcion = st.text_area("Descripción", placeholder="Proyecto de vivienda unifamiliar...")

        with col2:
            tipo_proyecto = st.selectbox("Tipo", ["Residencial unifamiliar", "Residencial plurifamiliar", "Comercial", "Industrial"])
            superficie_total = st.number_input("Superficie total (m²)", min_value=50, max_value=5000, value=150)

        # Archivos
        st.subheader("📁 Archivos del proyecto")

        col_files1, col_files2 = st.columns(2)

        with col_files1:
            archivo_3d = st.file_uploader("Modelo 3D", type=ALLOWED_EXTENSIONS['3d'], help="OBJ, FBX, GLTF, etc.")
            archivo_rv = st.file_uploader("Render/Video", type=ALLOWED_EXTENSIONS['rv'], help="JPG, PNG, MP4, etc.")
            archivo_pdf = st.file_uploader("Memoria constructiva (PDF)", type=['pdf'], help="Documento técnico completo")

        with col_files2:
            archivo_cad = st.file_uploader("Planos CAD", type=ALLOWED_EXTENSIONS['cad'], help="DXF, DWG, SVG")
            archivo_json = st.file_uploader("Distribución (JSON)", type=['json'], help="JSON con habitaciones y medidas")

        # Metadatos adicionales
        st.subheader("📊 Metadatos")
        precio_venta = st.number_input("Precio de venta (€)", min_value=1000, step=500)
        etiquetas = st.multiselect("Etiquetas", ["Moderno", "Clásico", "Minimalista", "Ecológico", "Accesible", "Bajo consumo"])

        # Validación y envío
        submitted = st.form_submit_button("🚀 Publicar Proyecto", type="primary")

        if submitted:
            return _procesar_upload(
                arquitecto_id=arquitecto_id,
                nombre=nombre,
                descripcion=descripcion,
                tipo_proyecto=tipo_proyecto,
                superficie_total=superficie_total,
                archivos={
                    '3d': archivo_3d,
                    'rv': archivo_rv,
                    'pdf': archivo_pdf,
                    'cad': archivo_cad,
                    'json': archivo_json
                },
                precio_venta=precio_venta,
                etiquetas=etiquetas
            )

    return None

def _procesar_upload(arquitecto_id: int, nombre: str, descripcion: str, tipo_proyecto: str,
                    superficie_total: float, archivos: Dict, precio_venta: float, etiquetas: List[str]) -> Optional[Dict]:
    """
    Procesa la subida de archivos y crea el proyecto
    """
    try:
        # Validar datos mínimos
        if not nombre or not descripcion:
            st.error("❌ Nombre y descripción son obligatorios")
            return None

        # Crear directorio para el proyecto
        proyecto_dir = os.path.join(UPLOAD_DIR, f"arquitecto_{arquitecto_id}_{int(st.session_state.get('timestamp', 0))}")
        os.makedirs(proyecto_dir, exist_ok=True)

        # Guardar archivos y obtener URLs
        urls_archivos = {}

        for tipo, archivo in archivos.items():
            if archivo is not None:
                filename = _sanitize_filename(archivo.name)
                filepath = os.path.join(proyecto_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(archivo.getbuffer())

                urls_archivos[f'{tipo}_url'] = filepath

        # Procesar JSON de distribución si existe
        json_distribucion = None
        if archivos['json']:
            try:
                json_data = json.loads(archivos['json'].getvalue().decode('utf-8'))
                json_distribucion = json_data
            except:
                st.warning("⚠️ No se pudo procesar el archivo JSON de distribución")

        # Generar documentación si no existe
        memoria_texto = ""
        presupuesto_data = {}

        if not archivos['pdf'] and json_distribucion:
            # Generar memoria básica desde JSON
            memoria_texto = generar_memoria_constructiva(json_distribucion, superficie_total * 3)  # Estimación
            presupuesto_data = generar_presupuesto_estimado(json_distribucion)

        # Crear proyecto
        proyecto_data = {
            'autor_tipo': 'arquitecto',
            'autor_id': arquitecto_id,
            'nombre': nombre,
            'descripcion': descripcion,
            'tipo': tipo_proyecto.lower().replace(' ', '_'),
            'total_m2': superficie_total,
            'precio_venta': precio_venta,
            'etiquetas': etiquetas,
            'json_distribucion': json_distribucion,
            'memoria_texto': memoria_texto,
            'presupuesto_estimado': presupuesto_data,
            'validacion_ok': True,  # Asumimos validado por arquitecto
            'estado_publicacion': 'publicada',
            **urls_archivos
        }

        # Guardar en base de datos
        if save_proyecto(proyecto_data):
            st.success("✅ Proyecto publicado exitosamente en el marketplace!")
            return proyecto_data
        else:
            st.error("❌ Error al guardar el proyecto")
            return None

    except Exception as e:
        st.error(f"❌ Error procesando subida: {str(e)}")
        return None

# === FUNCIONES DE EXPLORACIÓN ===
def explorar_proyectos_arquitectos(filtros: Dict = None) -> List[Dict]:
    """
    Lista proyectos de arquitectos disponibles
    """
    # Import list_proyectos directly to avoid AttributeError from module caching
    try:
        from src.db import list_proyectos
    except Exception:
        try:
            from src import db
            list_proyectos = getattr(db, 'list_proyectos', None)
        except Exception:
            list_proyectos = None

    if not callable(list_proyectos):
        return []

    filtros_arquitectos = {'autor_tipo': 'arquitecto'}
    if filtros:
        filtros_arquitectos.update(filtros)

    try:
        return list_proyectos(filtros_arquitectos)
    except Exception:
        return []

def mostrar_proyecto_arquitecto(proyecto: Dict):
    """
    Muestra detalles de un proyecto de arquitecto
    """
    st.subheader(f"🏗️ {proyecto['nombre']}")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.write(f"**Descripción:** {proyecto.get('descripcion', 'Sin descripción')}")
        st.write(f"**Tipo:** {proyecto.get('tipo', 'No especificado').replace('_', ' ').title()}")
        st.write(f"**Superficie:** {proyecto.get('total_m2', 0)} m²")

        if proyecto.get('etiquetas'):
            st.write(f"**Etiquetas:** {', '.join(proyecto['etiquetas'])}")

        if proyecto.get('presupuesto_estimado'):
            presupuesto = proyecto['presupuesto_estimado']
            st.metric("Presupuesto estimado", f"€{presupuesto.get('total_estimado', 0):,.0f}")

    with col2:
        precio = proyecto.get('precio_venta', proyecto.get('precio', 0))
        st.metric("Precio de venta", f"€{precio:,.0f}")

        # Archivos disponibles
        archivos = []
        if proyecto.get('3d_url'): archivos.append("3D")
        if proyecto.get('rv_url'): archivos.append("RV")
        if proyecto.get('pdf_url'): archivos.append("PDF")
        if proyecto.get('cad_url'): archivos.append("CAD")

        if archivos:
            st.write(f"**Archivos:** {', '.join(archivos)}")

        # Compra del proyecto (paquete ZIP) — pedir email comprador
        st.markdown("---")
        buyer_email = st.text_input("Email comprador (para facturación)", key=f"buy_email_{proyecto.get('nombre','')}")
        if st.button("Comprar Proyecto (Paquete ZIP)", key=f"buy_proj_{proyecto.get('nombre','')}"):
            if not buyer_email or '@' not in buyer_email:
                st.error('Introduce un email válido para completar la compra')
            else:
                # Registrar venta (comisión) y generar paquete
                precio_base = float(precio or 0)
                try:
                    comision = db.registrar_venta_proyecto(proyecto.get('id'), buyer_email, 'Paquete ZIP', precio_base)
                except Exception:
                    comision = 0.0

                try:
                    paquete = generar_paquete_descarga(proyecto.get('nombre', 'proyecto'))
                    st.download_button('Descargar paquete ZIP', data=paquete, file_name=f"{proyecto.get('nombre','proyecto')}.zip", mime='application/zip')
                    st.success(f'Compra registrada. Comisión Archirapid: €{comision:.2f}')
                except Exception as e:
                    st.error(f'Error generando paquete de descarga: {e}')

    # Vista previa de distribución
    if proyecto.get('json_distribucion'):
        with st.expander("📊 Distribución del proyecto"):
            st.json(proyecto['json_distribucion'])

    # Memoria constructiva
    if proyecto.get('memoria_texto'):
        with st.expander("📄 Memoria constructiva"):
            st.code(proyecto['memoria_texto'], language="text")

# === FUNCIONES AUXILIARES ===
def _sanitize_filename(filename: str) -> str:
    """
    Sanitiza nombre de archivo para evitar problemas de seguridad
    """
    import re
    return re.sub(r'[^\w\.-]', '_', filename)


def show_project_upload_form(arquitecto_id: int) -> Optional[Dict]:
    """
    Render a simple project upload form and persist the project in the central DB.

    Fields: title, price, area_m2, description, etiquetas (tags)

    Returns the saved project dict or None.
    """
    st.subheader("Formulario detallado de subida de proyecto")

    with st.form('show_project_upload_form'):
        # Datos básicos
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input('Título del proyecto')
            descripcion = st.text_area('Descripción')
            etiquetas = st.multiselect('Etiquetas', ['Moderno', 'Clásico', 'Minimalista', 'Ecológico', 'Accesible', 'Bajo consumo'])
        with col2:
            tipo_proyecto = st.selectbox('Tipo de proyecto', ['Residencial unifamiliar', 'Residencial plurifamiliar', 'Comercial', 'Industrial', 'Otro'])
            area_m2 = st.number_input('Metros cuadrados construidos (m²)', min_value=1.0, value=100.0, step=1.0)
            precio = st.number_input('Precio (€)', min_value=0.0, value=10000.0, step=500.0)

        st.markdown('---')
        st.subheader('📁 Subida de archivos')
        colf1, colf2 = st.columns(2)
        with colf1:
            memoria_pdf = st.file_uploader('Subir Memoria Descriptiva (.pdf)', type=['pdf'])
            proyecto_cad = st.file_uploader('Subir Proyecto CAD (.dwg)', type=['dwg'])
            modelo_3d = st.file_uploader('Subir Modelo 3D (.obj, .fbx)', type=['obj', 'fbx'])
        with colf2:
            imagenes = st.file_uploader('Subir Imágenes/Renders (.zip, .jpg)', type=['zip', 'jpg', 'jpeg', 'png'], accept_multiple_files=False)
            # Allow legacy 3D types in other uploaders too if needed

        st.markdown('---')
        st.subheader('🏗️ Características arquitectónicas')
        filas1, filas2 = st.columns(2)
        with filas1:
            plantas = st.selectbox('Número de Plantas', options=[1,2,3,4,5,6], index=0)
            habitaciones = st.number_input('Número de Habitaciones', min_value=0, value=3, step=1)
        with filas2:
            banos = st.number_input('Número de Baños', min_value=0, value=2, step=1)
            m2_construidos = st.number_input('Metros Cuadrados Construidos (confirmar)', min_value=0.0, value=float(area_m2), step=1.0)

        st.write('Características adicionales')
        piscina = st.checkbox('Piscina')
        garaje = st.checkbox('Garaje')
        bodega = st.checkbox('Bodega')
        jardin = st.checkbox('Jardín / Terraza')
        suite = st.checkbox('Habitación en Suite')
        vestidor = st.checkbox('Vestidor')

        submitted = st.form_submit_button('Publicar proyecto')

        if not submitted:
            return None

        # Validaciones obligatorias
        if not title:
            st.error('El título es obligatorio')
            return None
        if memoria_pdf is None:
            st.error('La Memoria descriptiva en PDF es obligatoria')
            return None
        if proyecto_cad is None:
            st.error('El proyecto CAD (.dwg) es obligatorio')
            return None
        if modelo_3d is None:
            st.error('El modelo 3D (.obj/.fbx) es obligatorio')
            return None

        # Guardar archivos en disco
        try:
            import time
            from datetime import datetime
            now_ts = int(time.time())
            proyecto_dir = os.path.join(UPLOAD_DIR, f"arquitecto_{arquitecto_id}_{now_ts}")
            os.makedirs(proyecto_dir, exist_ok=True)

            saved_paths = {}
            # Helper local to save a file-like object
            def _save_file(fobj, prefix=None):
                if not fobj:
                    return None
                fname = _sanitize_filename(fobj.name)
                if prefix:
                    fname = f"{prefix}_" + fname
                dest = os.path.join(proyecto_dir, fname)
                with open(dest, 'wb') as _f:
                    _f.write(fobj.getbuffer())
                return dest

            saved_paths['memoria_pdf'] = _save_file(memoria_pdf, 'memoria')
            saved_paths['cad_dwg'] = _save_file(proyecto_cad, 'cad')
            saved_paths['modelo_3d'] = _save_file(modelo_3d, '3d')
            saved_paths['imagenes'] = _save_file(imagenes, 'images') if imagenes else None

            # Construir objeto de características con nombres exactos (compatibilidad Home)
            characteristics = {
                'habitaciones': int(habitaciones),
                'baños': int(banos),
                'plantas': int(plantas),
                'm2_construidos': float(m2_construidos),
                'piscina': bool(piscina),
                'garaje': bool(garaje)
            }

            # Preparar proyecto para DB
            project_id = f"p_{now_ts}_{arquitecto_id}"
            created_at = datetime.utcnow().isoformat()
            try:
                from src import db as _db
            except Exception:
                st.error('Error accediendo a la base de datos')
                return None
            # Construir el JSON principal que leerá la Home: incluir características y rutas relevantes
            # Build flat characteristics JSON with exact keys expected by Home
            data_json = {
                'habitaciones': characteristics.get('habitaciones'),
                'baños': characteristics.get('baños'),
                'banos': characteristics.get('baños') if characteristics.get('baños') is not None else characteristics.get('banos'),
                'plantas': characteristics.get('plantas'),
                'm2_construidos': characteristics.get('m2_construidos'),
                'piscina': characteristics.get('piscina'),
                'garaje': characteristics.get('garaje'),
                'imagenes': saved_paths.get('imagenes'),
                'modelo_3d_path': saved_paths.get('modelo_3d')
            }

            proyecto = {
                'id': project_id,
                'title': title,
                'architect_id': str(arquitecto_id),
                'area_m2': int(m2_construidos),
                'price': float(precio),
                'description': descripcion,
                'created_at': created_at,
                # characteristics_json ahora contiene las claves planas esperadas por la Home
                'characteristics_json': json.dumps(data_json, ensure_ascii=False),
                # Guardar también campos individuales en columnas para que la Home los lea directamente
                'habitaciones': int(characteristics.get('habitaciones')) if characteristics.get('habitaciones') is not None else None,
                # Guardamos 'banos' (sin tilde) que existe en el esquema y mantenemos 'baños' en el JSON
                'banos': int(characteristics.get('baños')) if characteristics.get('baños') is not None else (int(characteristics.get('banos')) if characteristics.get('banos') is not None else None),
                'plantas': int(characteristics.get('plantas')) if characteristics.get('plantas') is not None else None,
                'piscina': int(bool(characteristics.get('piscina'))),
                'garaje': int(bool(characteristics.get('garaje'))),
                # Rutas/fotos: guardar en columnas exactas que busca la Home
                'foto_principal': saved_paths.get('imagenes') or None,
                'imagenes': saved_paths.get('imagenes') or None,
                'imagenes_path': saved_paths.get('imagenes') or None,
                'modelo_3d_path': saved_paths.get('modelo_3d') or None
            }

            # Añadir rutas de archivos al dict para referencia (no son columnas obligatorias)
            proyecto.update({
                'memoria_pdf_path': saved_paths.get('memoria_pdf'),
                'cad_dwg_path': saved_paths.get('cad_dwg'),
                'modelo_3d_path': saved_paths.get('modelo_3d'),
                'imagenes_path': saved_paths.get('imagenes')
            })

                # Insertar en DB: preferir la API centralizada `src.db.insert_project`
                try:
                    _db.insert_project(proyecto)
                    # Sincronizar inmediatamente las columnas desde el JSON para consistencia
                    try:
                        _sync_project_characteristics(project_id)
                    except Exception:
                        pass
                    st.success('Proyecto publicado correctamente')
                    return proyecto
                except Exception:
                    # Fallback a save_proyecto si existe (compatibilidad)
                    try:
                        if save_proyecto(proyecto):
                            # En fallback también intentamos sincronizar
                            try:
                                _sync_project_characteristics(project_id)
                            except Exception:
                                pass
                            st.success('Proyecto publicado correctamente (fallback)')
                            return proyecto
                    except Exception:
                        pass
                    st.error('Error guardando el proyecto en la base de datos')
                    return None

        except Exception as e:
            st.error(f'Error procesando los archivos: {e}')
            return None

def validar_proyecto_minimo(archivos: Dict) -> Tuple[bool, str]:
    """
    Valida que el proyecto tenga archivos mínimos
    """
    tiene_3d_o_json = archivos.get('3d') is not None or archivos.get('json') is not None
    tiene_documentacion = archivos.get('pdf') is not None

    if not tiene_3d_o_json:
        return False, "Se requiere modelo 3D o distribución JSON"

    if not tiene_documentacion:
        return False, "Se requiere memoria constructiva en PDF"

    return True, "Proyecto válido"

def proyectos_por_arquitecto(arquitecto_id: int) -> List[Dict]:
    """
    Lista proyectos de un arquitecto específico (usando src.db.list_proyectos)
    """
    # Import the function directly to avoid AttributeError due to module caching
    try:
        from src.db import list_proyectos
    except Exception:
        # Fallback: import module and try to call the method
        try:
            from src import db
            return db.list_proyectos({'autor_id': arquitecto_id})
        except Exception:
            return []

    try:
        return list_proyectos({'autor_id': arquitecto_id})
    except Exception:
        return []


def main():
    """
    Página principal para Arquitectos (Marketplace) — puerta de acceso.

    Flujo:
    - Si no hay `arquitecto_id` en session_state -> mostrar formulario de login/registro
    - Si hay `arquitecto_id` y no hay `arquitecto_plan` -> mostrar selección de planes
    - Si hay `arquitecto_id` y `arquitecto_plan` -> mostrar "Mis Proyectos" y formulario de subida
    """
    st.title("👷 Marketplace Arquitectos")

    # Simple plan limits
    PLAN_LIMITS = {
        'free': 1,       # Free / Estudiante: 1 proyecto
        'pro': 5         # Pro: 5 proyectos
    }

    # --- Login / Registro ---
    if 'arquitecto_id' not in st.session_state:
        st.info("Inicia sesión o regístrate como arquitecto para gestionar tus proyectos")

        with st.form("auth_form"):
            col1, col2 = st.columns(2)
            with col1:
                input_id = st.text_input("ID Arquitecto (si ya tienes)")
                email = st.text_input("Email")
            with col2:
                nombre = st.text_input("Nombre completo")
                empresa = st.text_input("Empresa / Estudio (opcional)")

            submitted = st.form_submit_button("Entrar / Registrarse")

            if submitted:
                # Preferir ID si se proporciona
                try:
                    if input_id and input_id.strip().isdigit():
                        aid = int(input_id.strip())
                        usuario = get_usuario(aid)
                        st.success(f"Bienvenido {usuario.get('nombre','Arquitecto')}")
                        st.session_state['arquitecto_id'] = aid
                        # keep plan empty until selected
                        st.session_state.setdefault('arquitecto_plan', None)
                        st.experimental_rerun()
                    else:
                        # Registro simulado: generar id basado en timestamp
                        new_id = int(st.session_state.get('timestamp', 0)) or (len(proyectos_por_arquitecto(0)) + 1000)
                        st.session_state['arquitecto_id'] = new_id
                        st.session_state.setdefault('arquitecto_plan', None)
                        st.success(f"Cuenta creada temporal para {nombre or email} (ID {new_id})")
                        st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error autenticando: {e}")
        return

    # --- Usuario logueado ---
    arquitecto_id = st.session_state.get('arquitecto_id')
    arquitecto_plan = st.session_state.get('arquitecto_plan')

    # Si no tiene plan, mostrar selección de planes
    if not arquitecto_plan:
        st.warning("No tienes un plan activo. Selecciona uno para publicar proyectos.")
        plan = st.radio("Elige un plan", ["Free/Estudiante (1 proyecto)", "Pro (5 proyectos)"], index=0)
        if st.button("Suscribirme"):
            chosen = 'free' if 'Free' in plan else 'pro'
            st.session_state['arquitecto_plan'] = chosen
            st.success(f"Plan {plan} activado")
            st.experimental_rerun()
        # Mostrar exploración del mercado aunque no pueda subir
        st.markdown("---")
        st.subheader("Explorar Mercado")
        proyectos = explorar_proyectos_arquitectos()
        for p in proyectos:
            mostrar_proyecto_arquitecto(p)
            st.divider()
        return

    # --- Usuario con plan ---
    limit = PLAN_LIMITS.get(arquitecto_plan, 1)
    proyectos_actuales = proyectos_por_arquitecto(arquitecto_id) or []
    usados = len(proyectos_actuales)
    restantes = max(0, limit - usados)

    st.success(f"Conectado como arquitecto ID {arquitecto_id} — Plan: {arquitecto_plan.upper()} ({usados}/{limit} proyectos)")

    sub_page = st.radio("Acciones", ["Mis Proyectos", "Explorar Mercado", "Subir Proyecto"], horizontal=True, key="arquitectos_main_menu")

    if sub_page == "Mis Proyectos":
        st.subheader("Mis Proyectos")
        if proyectos_actuales:
            for p in proyectos_actuales:
                mostrar_proyecto_arquitecto(p)
                st.divider()
        else:
            st.info("No tienes proyectos aún")

    elif sub_page == "Explorar Mercado":
        st.subheader("Catálogo público")
        proyectos = explorar_proyectos_arquitectos()
        for p in proyectos:
            mostrar_proyecto_arquitecto(p)
            st.divider()

    elif sub_page == "Subir Proyecto":
        st.subheader("Subir nuevo proyecto")
        if restantes <= 0:
            st.error("Has alcanzado el límite de proyectos para tu plan. Actualiza tu plan para publicar más proyectos.")
        else:
            result = show_project_upload_form(arquitecto_id)
            if result:
                st.success("Proyecto subido. Refrescando lista...")
                st.experimental_rerun()