# modules/marketplace/client_panel.py
import streamlit as st
try:
    from modules.marketplace.utils import db_conn
except ImportError:
    # Fallback si falla el import
    import sys
    sys.path.append(r"C:/ARCHIRAPID_PROYECT25")
    from src import db as db_module
    def db_conn():
        return db_module.get_conn()
import json
import os
from modules.marketplace.compatibilidad import get_proyectos_compatibles

def main():
    st.title("👤 Panel de Cliente - ARCHIRAPID")

    # Auto-login si viene de query params con owner_email
    if "auto_owner_email" in st.session_state and not st.session_state.get("client_logged_in", False):
        auto_email = st.session_state["auto_owner_email"]
        # Verificar si el email tiene transacciones O es propietario con fincas
        conn = db_conn()
        cursor = conn.cursor()

        # Buscar SOLO transacciones de COMPRA (este panel es exclusivo para compradores)
        cursor.execute("SELECT * FROM reservations WHERE buyer_email=? AND kind='purchase'", (auto_email,))
        transactions = cursor.fetchall()

        # NO auto-login para propietarios - ellos tienen panel separado
        owner_plots = []

        conn.close()

        # Auto-login SOLO si tiene transacciones de COMPRA verificadas
        if transactions:
            st.session_state["client_logged_in"] = True
            st.session_state["client_email"] = auto_email
            st.session_state["user_role"] = "buyer"
            st.session_state["has_transactions"] = len(transactions) > 0
            st.session_state["has_properties"] = False

            st.info(f"🔄 Auto-acceso concedido como comprador para {auto_email}")

            # Limpiar el estado de auto-login
            del st.session_state["auto_owner_email"]

    # Verificar si viene de vista previa de proyecto
    selected_project = st.query_params.get("selected_project")
    if selected_project and not st.session_state.get("client_logged_in", False):
        st.info("🔍 Proyecto seleccionado detectado. Por favor inicia sesión para continuar.")
    
    # Login simple por email
    if "client_logged_in" not in st.session_state:
        st.session_state["client_logged_in"] = False
    
    if not st.session_state["client_logged_in"]:
        st.subheader("🔐 Acceso al Panel de Cliente")
        st.info("Introduce el email que usaste al realizar tu compra/reserva")
        
        email = st.text_input("Email de cliente", placeholder="tu@email.com")
        
        if st.button("Acceder", type="primary"):
            if email:
                # Verificar si el email tiene transacciones, propiedades O está registrado como cliente
                conn = db_conn()
                cursor = conn.cursor()
                
                # Verificar si el email tiene transacciones de COMPRA (solo clientes que han comprado)
                cursor.execute("SELECT * FROM reservations WHERE buyer_email=? AND kind='purchase'", (email,))
                transactions = cursor.fetchall()
                
                # NO permitir acceso a propietarios aquí - ellos tienen su propio panel
                owner_plots = []  # No buscar propiedades de propietario
                
                # NO verificar registro como cliente genérico - solo compras reales
                is_registered_client = False
                
                conn.close()
                
                # Permitir acceso SOLO si tiene transacciones de COMPRA verificadas
                if transactions:
                    st.session_state["client_logged_in"] = True
                    st.session_state["client_email"] = email
                    st.session_state["user_role"] = "buyer"
                    st.session_state["has_transactions"] = len(transactions) > 0
                    st.session_state["has_properties"] = False  # No es propietario en este panel
                    
                    st.success(f"✅ Acceso concedido como cliente para {email}")
                    st.rerun()
                else:
                    st.error("❌ Acceso denegado. Este panel es exclusivo para clientes que han realizado compras.")
                    st.info("Si eres propietario, accede desde la página principal. Si has comprado un proyecto, verifica tu email.")
            else:
                st.error("Por favor introduce tu email")
        
        st.markdown("---")
        st.info("💡 **Nota:** Si acabas de realizar una compra, usa el email que proporcionaste en el formulario de datos personales.")
        st.info("Por favor inicia sesión para acceder al panel.")
        # st.stop()  # Comentado para permitir que la página se cargue
    
    if st.session_state["client_logged_in"]:
        # Panel de cliente logueado
        client_email = st.session_state.get("client_email")
        user_role = st.session_state.get("user_role", "buyer")
        has_transactions = st.session_state.get("has_transactions", False)
        has_properties = st.session_state.get("has_properties", False)
        
        # Botón de cerrar sesión en sidebar
        with st.sidebar:
            if st.button("🚪 Cerrar Sesión", width='stretch', key="logout_button"):
                st.session_state["client_logged_in"] = False
                for key in ["client_email", "user_role", "has_transactions", "has_properties", "selected_project_for_panel"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        # Mostrar rol del usuario
        role_emoji = "🛒" if user_role == "buyer" else "🏠"
        role_text = "Comprador" if user_role == "buyer" else "Propietario"
        st.success(f"{role_emoji} **Bienvenido/a {role_text}** - {client_email}")
        
        # � QUIRÚRGICO: Manejar proyecto seleccionado desde query params para usuarios logueados
        selected_project = st.query_params.get("selected_project")
        if selected_project and not st.session_state.get("selected_project_for_panel"):
            st.session_state["selected_project_for_panel"] = selected_project
            # Limpiar query param para evitar conflictos futuros
            if "selected_project" in st.query_params:
                del st.query_params["selected_project"]
        
        # �🔍 MODO 3: Usuario interesado en un proyecto (sin transacciones)
        selected_project_for_panel = st.session_state.get("selected_project_for_panel")
        if user_role == "buyer" and not has_transactions and selected_project_for_panel:
            show_selected_project_panel(client_email, selected_project_for_panel)
            return
        
        # Contenido diferente según el rol
        if user_role == "buyer":
            show_buyer_panel(client_email)
        elif user_role == "owner":
            show_owner_panel_v2(client_email)
        else:
            st.error("Error: No se pudo determinar el tipo de panel apropiado")
            st.stop()

def show_selected_project_panel(client_email, project_id):
    from modules.marketplace.project_detail import get_project_by_id
    from modules.marketplace import ai_engine_groq as ai
    
    project = get_project_by_id(project_id)
    
    st.title(f"📂 Proyecto: {project['nombre']}")
    
    # 1. BOTÓN DE DOSSIER (Texto corto para evitar cortes)
    if st.button("📋 GENERAR DOSSIER PREVENTA"):
        texto = project.get('ocr_text', "No hay datos en la DB")
        with st.spinner("Analizando..."):
            resumen = ai.generate_text(f"Resume en 150 palabras materiales y estilo de: {texto[:2000]}")
            st.info(resumen)

    # 2. BOTÓN DE PLANO (La clave de lo que buscas)
    if st.button("📐 GENERAR PLANO TÉCNICO"):
        texto = project.get('ocr_text', "")
        if not texto:
            st.error("Error: No hay memoria técnica guardada en la base de datos para este proyecto.")
        else:
            with st.spinner("Dibujando plano..."):
                plano = ai.generate_ascii_plan_only(texto)
                st.code(plano, language="text")

    st.divider()
    # ... (Aquí siguen tus botones de 'Comprar Proyecto', 'Descargar CAD', etc.) ...

def show_client_interests(client_email):
    """Mostrar proyectos de interés del cliente"""
    st.subheader("⭐ Mis Proyectos de Interés")
    
    conn = db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ci.project_id, ci.created_at, p.title, p.m2_construidos, p.price, p.foto_principal
        FROM client_interests ci
        JOIN projects p ON ci.project_id = p.id
        WHERE ci.email = ?
        ORDER BY ci.created_at DESC
    """, (client_email,))
    
    interests = cursor.fetchall()
    conn.close()
    
    if not interests:
        st.info("No tienes proyectos guardados como de interés. Explora el marketplace para encontrar proyectos que te gusten.")
        return
    
    # Mostrar proyectos de interés
    for interest in interests:
        project_id, saved_at, title, m2, price, foto = interest
        
        with st.expander(f"🏗️ {title}", expanded=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if foto:
                    try:
                        st.image(foto, width=200)
                    except:
                        st.image("assets/fincas/image1.jpg", width=200)
                else:
                    st.image("assets/fincas/image1.jpg", width=200)
            
            with col2:
                st.markdown(f"**🏗️ Proyecto:** {title}")
                st.markdown(f"**📏 Superficie:** {m2} m²" if m2 else "**📏 Superficie:** N/D")
                st.markdown(f"**💰 Precio:** €{price:,.0f}" if price else "**💰 Precio:** N/D")
                st.markdown(f"**📅 Guardado:** {saved_at}")
                
                if st.button("Ver Detalles", key=f"view_interest_{project_id}"):
                    st.query_params["selected_project"] = project_id
                    st.rerun()

def show_client_transactions(client_email):
    """Mostrar transacciones del cliente (fincas compradas)"""
    st.subheader("📋 Mis Transacciones")
    
    # Obtener transacciones del cliente
    conn = db_conn()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT r.id, r.plot_id, r.buyer_name, r.amount, r.kind, r.created_at, 
           p.title, p.m2, p.price, p.photo_paths
    FROM reservations r
    JOIN plots p ON r.plot_id = p.id
    WHERE r.buyer_email = ?
    ORDER BY r.created_at DESC
""", (client_email,))

    transactions = cursor.fetchall()
    conn.close()

    if not transactions:
        st.info("No se encontraron transacciones para este cliente.")
        return

    # Mostrar tabla general
    st.dataframe(transactions)

    # Mostrar resumen de transacciones
    for trans in transactions:
        trans_id, plot_id, buyer_name, amount, kind, created_at, plot_title, m2, price, photo_paths = trans

        with st.expander(f"🏠 {plot_title} - {kind.upper()}", expanded=True):
            col1, col2 = st.columns([1, 2])

            # 📸 Columna izquierda: imagen
            with col1:
                if photo_paths:
                    try:
                        paths = json.loads(photo_paths)
                        if paths and isinstance(paths, list):
                            image_paths = [f"uploads/{path}" for path in paths]
                            st.image(image_paths, caption=["Foto " + str(i+1) for i in range(len(image_paths))], use_container_width=True)
                    except Exception as e:
                        st.warning(f"No se pudo cargar la imagen: {e}")

            # 📋 Columna derecha: detalles
            with col2:
                st.markdown(f"**📋 ID Transacción:** `{trans_id}`")
                st.markdown(f"**🏠 Finca:** {plot_title}")
                st.markdown(f"**📏 Superficie:** {m2} m²")
                st.markdown(f"**💰 Precio Total:** €{price}")
                st.markdown(f"**💵 Cantidad Pagada:** €{amount}")
                st.markdown(f"**📅 Fecha:** {created_at}")
                st.markdown(f"**✅ Tipo:** {kind.upper()}")

        # 🔍 PROYECTOS COMPATIBLES
        st.markdown("### 📐 Proyectos Compatibles")

        proyectos = get_proyectos_compatibles(plot_id)

        if not proyectos:
            st.info("No hay proyectos compatibles para esta finca.")
        else:
            for p in proyectos:
                st.markdown(f"**🏗️ {p.get('nombre', 'Proyecto sin nombre')}** — {p.get('total_m2', '?')} m²")

                img = p.get("imagen_principal")
                if img:
                    st.image(f"assets/projects/{img}", use_container_width=True)

                st.markdown("---")

        show_common_actions(context=f"buyer_{trans_id}")  # Acciones comunes para compradores

def show_buyer_panel(client_email):
    """Panel principal para compradores"""
    st.header("🛒 Panel de Comprador")
    
    # Tabs para diferentes secciones
    tab1, tab2, tab3 = st.tabs(["🔍 Buscar Proyectos", "📋 Mis Intereses", "� Mis Compras de Proyectos"])
    
    with tab1:
        # Búsqueda avanzada de proyectos
        show_advanced_project_search(client_email)
    
    with tab2:
        # Mostrar proyectos guardados/interesantes
        show_client_interests(client_email)
    
    with tab3:
        # Mostrar compras de proyectos realizadas
        show_client_project_purchases(client_email)


def show_owner_panel_v2(client_email):
    """Panel para propietarios con fincas"""
    st.subheader("🏠 Mis Propiedades Publicadas")
    
    # Obtener fincas del propietario
    conn = db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, cadastral_ref, surface_m2, buildable_m2, is_urban, vector_geojson, registry_note_path, price, lat, lon, status, created_at, photo_paths, owner_name, owner_email, owner_phone, sanitation_type, plot_type, propietario_direccion FROM plots WHERE owner_email = ? ORDER BY created_at DESC", (client_email,))
    
    properties = cursor.fetchall()
    conn.close()
    
    if not properties:
        st.warning("No tienes propiedades publicadas")
        return
    
    # Mostrar propiedades
    for prop in properties:
        prop_id = prop[0]
        title = prop[1]
        surface_m2 = prop[3]
        price = prop[8]
        status = prop[11]
        created_at = prop[12]
        photo_paths = prop[13]
        owner_name = prop[14]
        owner_phone = prop[16]
        
        status_emoji = "✅" if status == "published" else "⏳" if status == "pending" else "❌"
        
        with st.expander(f"{status_emoji} {title} - {surface_m2} m²", expanded=True):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Mostrar imagen de la finca
                if photo_paths:
                    try:
                        paths = json.loads(photo_paths)
                        if paths and isinstance(paths, list):
                            img_path = f"uploads/{paths[0]}"
                            if os.path.exists(img_path):
                                st.image(img_path, width=200)
                    except:
                        st.image("assets/fincas/image1.jpg", width=200)
                else:
                    st.image("assets/fincas/image1.jpg", width=200)
            
            with col2:
                st.markdown(f"**🏠 Propiedad:** {title}")
                st.markdown(f"**📏 Superficie:** {surface_m2} m²")
                st.markdown(f"**💰 Precio:** €{price}")
                st.markdown(f"**📊 Estado:** {status.capitalize()}")
                st.markdown(f"**📅 Publicada:** {created_at}")
                st.markdown(f"**📞 Contacto:** {owner_phone}")
                
                # Estadísticas de la propiedad
                st.markdown("---")
                st.markdown("**📈 Estadísticas:**")
                
                # Contar propuestas para esta finca
                conn = db_conn()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM proposals WHERE plot_id = ?", (prop_id,))
                proposals_count = cursor.fetchone()[0]
                conn.close()
                
                col_stats1, col_stats2 = st.columns(2)
                with col_stats1:
                    st.metric("📨 Propuestas Recibidas", proposals_count)
                with col_stats2:
                    st.metric("👁️ Visitas Estimadas", "N/A")  # TODO: implementar contador de visitas
    
    # Opciones específicas para propietarios
    st.markdown("---")
    st.subheader("🎯 Gestión de Propiedades")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 VER PROPUESTAS")
        st.write("Revisa las propuestas de arquitectos para tus fincas")
        if st.button("📨 Ver Todas las Propuestas", key="view_proposals_owner", use_container_width=True, type="primary"):
            st.success("📨 Mostrando todas las propuestas...")
            st.info("Aquí podrás gestionar todas las propuestas recibidas para tus propiedades")
    
    with col2:
        st.markdown("#### ➕ PUBLICAR MÁS FINCAS")
        st.write("Añade más propiedades a tu portafolio")
        if st.button("🏠 Subir Nueva Finca", key="upload_new_property", use_container_width=True, type="primary"):
            st.success("🏠 Redirigiendo a subida de fincas...")
            st.info("Accede desde el menú lateral 'Propietarios (Subir Fincas)'")
    
    show_common_actions(context="owner")  # Acciones comunes para todos

def show_buyer_actions():
    """Acciones comunes para compradores"""
    st.markdown("---")
    
    # Opciones de acción para compradores
    st.subheader("🎯 ¿Qué deseas hacer?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏡 DISEÑAR VIVIENDA")
        st.write("Crea tu casa ideal con nuestros arquitectos")
        if st.button("🚀 Ir al Diseñador", key="go_designer_panel_1", use_container_width=True, type="primary"):
            st.success("🎨 Redirigiendo al Diseñador de Vivienda...")
            st.info("En esta sección podrás diseñar tu vivienda personalizada")
    
    with col2:
        st.markdown("#### 📐 VER PROYECTOS")
        st.write("Explora proyectos compatibles con tu finca")
        if st.button("📋 Ver Proyectos", key="go_projects_panel", use_container_width=True, type="primary"):
            st.success("📐 Mostrando proyectos disponibles...")
            st.info("Aquí verás todos los proyectos arquitectónicos compatibles")
    
    st.markdown("---")
    
    # Opciones adicionales
    st.subheader("🔧 Opciones Adicionales")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("🗺️ Volver al Marketplace", key="back_to_marketplace", use_container_width=True):
            st.success("🏠 Volviendo al marketplace...")
            st.info("Puedes seguir explorando más fincas y proyectos")
    
    with col_b:
        if st.button("📧 Contactar Soporte", key="contact_support_panel", use_container_width=True):
            st.info("📧 Contacto con soporte:")
            st.write("**Email:** soporte@archirapid.com")
            st.write("**Teléfono:** +34 900 123 456")
    
    with col_c:
        if st.button("📄 Descargar Documentación", key="download_docs", use_container_width=True):
            st.info("📄 Descarga disponible próximamente")
            st.write("Pronto podrás descargar todos los documentos de tu transacción")

# Añadir import necesario
import os
def show_common_actions(context="common"):
    """Acciones comunes para compradores y propietarios"""
    st.markdown("---")
    
    # Opciones de acción
    st.subheader("🎯 ¿Qué deseas hacer?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏡 DISEÑAR VIVIENDA")
        st.write("Crea tu casa ideal con nuestros arquitectos")
        if st.button("🚀 Ir al Diseñador", key=f"go_designer_panel_2_{context}", use_container_width=True, type="primary"):
            st.success("🎨 Redirigiendo al Diseñador de Vivienda...")
            st.info("En esta sección podrás diseñar tu vivienda personalizada")
    
    with col2:
        st.markdown("#### 📐 VER PROYECTOS")
        st.write("Explora proyectos compatibles con tu finca")
        if st.button("📋 Ver Proyectos", key=f"go_projects_panel_{context}", use_container_width=True, type="primary"):
            st.success("📐 Mostrando proyectos disponibles...")
            st.info("Aquí verás todos los proyectos arquitectónicos compatibles")
    
    st.markdown("---")
    
    # Opciones adicionales
    st.subheader("🔧 Opciones Adicionales")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("🗺️ Volver al Marketplace", key=f"back_to_marketplace_{context}", use_container_width=True):
            st.success("🏠 Volviendo al marketplace...")
            st.info("Puedes seguir explorando más fincas y proyectos")
    
    with col_b:
        if st.button("📧 Contactar Soporte", key=f"contact_support_panel_{context}", use_container_width=True):
            st.info("📧 Contacto con soporte:")
            st.write("**Email:** soporte@archirapid.com")
            st.write("**Teléfono:** +34 900 123 456")
    
    with col_c:
        if st.button("📄 Descargar Documentación", key=f"download_docs_{context}", use_container_width=True):
            st.info("📄 Descarga disponible próximamente")
            st.write("Pronto podrás descargar todos los documentos de tu transacción")

def show_advanced_project_search(client_email):
    """Búsqueda avanzada de proyectos por criterios"""
    st.subheader("🔍 Buscar Proyectos Arquitectónicos")
    st.write("Encuentra proyectos compatibles con tus necesidades específicas")
    
    # Formulario de búsqueda
    with st.form("advanced_search_form"):
        st.markdown("### 🎯 Especifica tus criterios")
        
        col1, col2 = st.columns(2)
        
        with col1:
            presupuesto_max = st.number_input(
                "💰 Presupuesto máximo (€)", 
                min_value=0, 
                value=0, 
                step=10000,
                help="Precio máximo que estás dispuesto a pagar por el proyecto completo"
            )
            
            area_deseada = st.number_input(
                "📐 Área de construcción deseada (m²)", 
                min_value=0, 
                value=0, 
                step=10,
                help="Superficie aproximada que quieres construir (±20% tolerancia)"
            )
        
        with col2:
            parcela_disponible = st.number_input(
                "🏞️ Parcela disponible (m²)", 
                min_value=0, 
                value=0, 
                step=50,
                help="Tamaño de terreno que tienes disponible"
            )
            
            # Checkbox para buscar solo proyectos que quepan
            solo_compatibles = st.checkbox(
                "Solo proyectos que quepan en mi parcela", 
                value=True,
                help="Filtrar proyectos cuya parcela mínima sea ≤ a tu terreno disponible"
            )
        
        # Botón de búsqueda
        submitted = st.form_submit_button("🔍 Buscar Proyectos", type="primary", use_container_width=True)
    
    # Procesar búsqueda
    if submitted:
        # Preparar parámetros
        search_params = {
            'client_budget': presupuesto_max if presupuesto_max > 0 else None,
            'client_desired_area': area_deseada if area_deseada > 0 else None,
            'client_parcel_size': parcela_disponible if parcela_disponible > 0 and solo_compatibles else None,
            'client_email': client_email
        }
        
        # Mostrar criterios de búsqueda
        st.markdown("### 📋 Criterios de búsqueda aplicados:")
        criterios = []
        if search_params['client_budget']:
            criterios.append(f"💰 Presupuesto ≤ €{search_params['client_budget']:,}")
        if search_params['client_desired_area']:
            criterios.append(f"📐 Área ≈ {search_params['client_desired_area']} m² (±20%)")
        if search_params['client_parcel_size']:
            criterios.append(f"🏞️ Parcela ≥ {search_params['client_parcel_size']} m²")
        
        if criterios:
            for criterio in criterios:
                st.write(f"• {criterio}")
        else:
            st.info("No se aplicaron filtros específicos - mostrando todos los proyectos disponibles")
        
        # Buscar proyectos
        with st.spinner("Buscando proyectos compatibles..."):
            proyectos = get_proyectos_compatibles(**search_params)
        
        # Mostrar resultados
        st.markdown(f"### 🏗️ Resultados: {len(proyectos)} proyectos encontrados")
        
        if not proyectos:
            st.warning("No se encontraron proyectos que cumplan con tus criterios. Prueba ampliando los límites.")
            return
        
        # Mostrar proyectos en grid
        cols = st.columns(2)
        for idx, proyecto in enumerate(proyectos):
            with cols[idx % 2]:
                # Tarjeta de proyecto
                with st.container():
                    # Imagen
                    foto = proyecto.get('foto_principal')
                    if foto:
                        try:
                            st.image(foto, width=250, caption=proyecto['title'])
                        except:
                            st.image("assets/fincas/image1.jpg", width=250, caption=proyecto['title'])
                    else:
                        st.image("assets/fincas/image1.jpg", width=250, caption=proyecto['title'])
                    
                    # Información básica
                    st.markdown(f"**🏗️ {proyecto['title']}**")
                    st.write(f"📐 **Área:** {proyecto.get('m2_construidos', proyecto.get('area_m2', 'N/D'))} m²")
                    st.write(f"💰 **Precio:** €{proyecto.get('price', 0):,.0f}" if proyecto.get('price') else "💰 **Precio:** Consultar")
                    
                    # Arquitecto
                    if proyecto.get('architect_name'):
                        st.write(f"👨‍💼 **Arquitecto:** {proyecto['architect_name']}")
                    
                    # Compatibilidad
                    if search_params['client_parcel_size'] and proyecto.get('m2_parcela_minima'):
                        if proyecto['m2_parcela_minima'] <= search_params['client_parcel_size']:
                            st.success("✅ Compatible con tu parcela")
                        else:
                            st.warning(f"⚠️ Necesita parcela ≥ {proyecto['m2_parcela_minima']} m²")
                    
                    # Botón de detalles
                    if st.button("Ver Detalles", key=f"search_detail_{proyecto['id']}", use_container_width=True):
                        st.query_params["selected_project"] = proyecto['id']
                        st.rerun()
                    
                    st.markdown("---")

def show_project_interest_panel(project_id):
    from modules.marketplace.project_detail import get_project_by_id
    from modules.marketplace import ai_engine_groq as ai
    import json

    # 1. Recuperamos el proyecto con los nuevos campos (ocr_text)
    project = get_project_by_id(project_id)
    
    if not project:
        st.error("Proyecto no encontrado")
        return

    st.title(f"🏗️ {project['nombre']}")
    
    # --- BLOQUE DE IA CORREGIDO ---
    st.divider()
    st.subheader("🤖 Análisis de Inteligencia Artificial")
    
    # Recuperamos el texto que guardamos en la base de datos
    ocr_content = project.get('ocr_text', "")
    
    if not ocr_content:
        st.warning("⚠️ Este proyecto no tiene memoria técnica procesada. Súbelo de nuevo para activar el análisis.")
    else:
        # BOTÓN 1: El Dossier Preventa (Resumen corto para que no se corte)
        if st.button("📋 GENERAR DOSSIER PREVENTA", type="primary"):
            with st.spinner("Redactando dossier ejecutivo..."):
                # Forzamos a la IA a ser breve: máximo 150 palabras
                resumen = ai.generate_text(
                    f"Basado en este texto: {ocr_content[:2000]}, haz un resumen ejecutivo de calidades y estilo de máximo 150 palabras. NO TE INVENTES NOMBRES, usa el título: {project['nombre']}", 
                    max_tokens=300
                )
                st.info(resumen)

        # BOTÓN 2: El Plano Técnico (Llamada exclusiva al dibujo)
        if st.button("📐 GENERAR PLANO TÉCNICO (ASCII)"):
            with st.spinner("Delineando espacios..."):
                # Llamamos a la función dedicada que creamos antes
                plano_ascii = ai.generate_ascii_plan_only(ocr_content)
                st.markdown("#### Distribución de Planta Sugerida")
                st.code(plano_ascii, language="text")
                st.caption("Nota: Este plano es una representación esquemática basada en la memoria descriptiva.")


def show_client_project_purchases(client_email):
    """Mostrar compras de proyectos realizadas por el cliente"""
    st.subheader("🛒 Mis Compras de Proyectos")

    # Obtener compras del cliente
    conn = db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT vp.*, p.title as project_title, p.architect_name
        FROM ventas_proyectos vp
        LEFT JOIN projects p ON vp.proyecto_id = p.id
        WHERE vp.cliente_email = ?
        ORDER BY vp.fecha_compra DESC
    """, (client_email,))

    purchases = cursor.fetchall()
    conn.close()

    if not purchases:
        st.info("Aún no has realizado ninguna compra de proyectos.")
        st.markdown("💡 **¿Quieres comprar un proyecto?**")
        st.markdown("• Ve a la pestaña '🔍 Buscar Proyectos' para explorar opciones")
        st.markdown("• O navega por el marketplace principal")
        return

    # Mostrar estadísticas
    total_compras = len(purchases)
    total_gastado = sum(purchase[6] for purchase in purchases if purchase[6])  # total_pagado

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Compras", total_compras)
    with col2:
        st.metric("Total Gastado", f"€{total_gastado:,.0f}")
    with col3:
        st.metric("Promedio por Compra", f"€{total_gastado/total_compras:,.0f}" if total_compras > 0 else "€0")

    st.markdown("---")

    # Mostrar compras agrupadas por proyecto
    st.subheader("📋 Detalle de Compras")

    # Agrupar por proyecto
    projects_grouped = {}
    for purchase in purchases:
        project_id = purchase[1]  # proyecto_id
        if project_id not in projects_grouped:
            projects_grouped[project_id] = {
                'title': purchase[9] or f"Proyecto {project_id}",  # project_title
                'architect': purchase[10] or "No especificado",  # architect_name
                'purchases': []
            }
        projects_grouped[project_id]['purchases'].append(purchase)

    # Mostrar cada proyecto con sus compras
    for project_id, project_data in projects_grouped.items():
        with st.expander(f"🏗️ {project_data['title']} - Arquitecto: {project_data['architect']}", expanded=True):

            # Calcular total por proyecto
            project_total = sum(p[6] for p in project_data['purchases'] if p[6])

            st.markdown(f"**💰 Total invertido en este proyecto:** €{project_total:,.0f}")

            # Mostrar cada compra
            for purchase in project_data['purchases']:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                with col1:
                    producto = purchase[4]  # productos_comprados
                    st.markdown(f"**📄 {producto}**")

                with col2:
                    precio = purchase[5]  # total_pagado
                    st.markdown(f"**€{precio:,.0f}**")

                with col3:
                    metodo = purchase[6]  # metodo_pago
                    st.markdown(f"**{metodo}**")

                with col4:
                    fecha = purchase[7]  # fecha_compra
                    if fecha:
                        # Formatear fecha si es necesario
                        st.markdown(f"**{fecha[:10]}**")
                    else:
                        st.markdown("**Fecha N/D**")

                st.markdown("---")

    # Mostrar servicios contratados con proveedores
    st.markdown("### 🏗️ Servicios Profesionales Contratados")

    conn = db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sa.id, sa.servicio_tipo, sa.proveedor_id, sa.precio_servicio, sa.estado,
               sa.fecha_asignacion, sa.fecha_completado, sa.notas,
               sp.name as proveedor_name, sp.company, sp.phone, sp.specialty,
               vp.productos_comprados, p.title as project_title
        FROM service_assignments sa
        JOIN service_providers sp ON sa.proveedor_id = sp.id
        JOIN ventas_proyectos vp ON sa.venta_id = vp.id
        LEFT JOIN projects p ON sa.proyecto_id = p.id
        WHERE sa.cliente_email = ?
        ORDER BY sa.fecha_asignacion DESC
    """, (client_email,))

    services = cursor.fetchall()
    conn.close()

    if services:
        for service in services:
            (assignment_id, servicio_tipo, proveedor_id, precio_servicio, estado,
             fecha_asignacion, fecha_completado, notas,
             proveedor_name, company, phone, specialty,
             productos_comprados, project_title) = service

            estado_emoji = {
                "pendiente": "⏳",
                "en_progreso": "🔄",
                "completado": "✅",
                "cancelado": "❌"
            }.get(estado, "❓")

            servicio_nombre = {
                "direccion_obra": "Dirección de Obra",
                "visado": "Visado del Proyecto",
                "bim": "Gemelos Digitales (BIM)",
                "sostenibilidad": "Consultoría Sostenibilidad",
                "ssl": "Coordinación SSL"
            }.get(servicio_tipo, servicio_tipo.replace('_', ' ').title())

            with st.expander(f"{estado_emoji} {servicio_nombre} - {proveedor_name}", expanded=True):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**🏢 Proveedor:** {proveedor_name}")
                    if company:
                        st.write(f"**Empresa:** {company}")
                    st.write(f"**Especialidad:** {specialty.replace('_', ' ').title()}")
                    st.write(f"**Teléfono:** {phone}")
                    st.write(f"**Proyecto:** {project_title or f'ID: {productos_comprados}'}")

                with col2:
                    st.write(f"**💰 Precio:** €{precio_servicio:,.0f}")
                    st.write(f"**📊 Estado:** {estado.title()}")
                    st.write(f"**📅 Asignado:** {fecha_asignacion[:10]}")
                    if fecha_completado:
                        st.write(f"**✅ Completado:** {fecha_completado[:10]}")

                if notas:
                    st.write("**📝 Notas del proveedor:**")
                    for nota in notas.split('\n'):
                        if nota.strip():
                            st.write(f"• {nota.strip()}")

                # Información de contacto
                st.markdown("---")
                st.info(f"📞 **Contacto:** {phone} | Para consultas sobre el progreso del servicio")
    else:
        st.info("No tienes servicios profesionales contratados.")

    st.markdown("### 📥 Descargas Disponibles")
    st.info("Las descargas de tus proyectos estarán disponibles próximamente en esta sección.")
