# modules/marketplace/project_detail.py
"""
Página de detalles de proyecto arquitectónico
Vista previa básica para usuarios no registrados
"""

import streamlit as st
import json
from modules.marketplace.plot_detail import get_project_images
from src import db
from .marketplace import get_project_display_image

def normalize_gallery(galeria_fotos):
    import json
    if not galeria_fotos:
        return []
    if isinstance(galeria_fotos, list):
        return [f for f in galeria_fotos if f]
    if isinstance(galeria_fotos, str):
        try:
            data = json.loads(galeria_fotos)
            if isinstance(data, list):
                return [f for f in data if f]
        except:
            return []
    return []

def get_project_by_id(project_id: str) -> dict:
    """Obtiene un proyecto por ID incluyendo ocr_text para análisis IA"""
    conn = db.get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, architect_id, title, description, area_m2, price, 
               foto_principal, galeria_fotos, memoria_pdf, planos_pdf, 
               planos_dwg, modelo_3d_glb, vr_tour, ocr_text, created_at
        FROM projects
        WHERE id = ?
    """, (project_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    # Parsear galeria_fotos si es JSON
    import json
    galeria_fotos = []
    if row[7]:  # galeria_fotos
        try:
            if isinstance(row[7], str):
                galeria_fotos = json.loads(row[7])
            elif isinstance(row[7], list):
                galeria_fotos = row[7]
        except:
            galeria_fotos = []

    # Convertir row a dict y asegurar que ocr_text esté incluido
    project_dict = {
        'id': row[0],
        'architect_id': row[1],
        'title': row[2],
        'description': row[3],
        'area_m2': row[4],
        'price': row[5],
        'files': {
            'fotos': galeria_fotos,
            'memoria': row[8],
            'planos': row[9],
            'modelo_3d': row[11],
            'vr_tour': row[12],
            'ocr_text': row[13]
        },
        'created_at': row[14],
        # Mapeos para compatibilidad
        'm2_construidos': row[4],  # area_m2
        'architect_name': 'Arquitecto Demo',  # Placeholder
        'foto_principal': row[6] if row[6] else (galeria_fotos[0] if galeria_fotos else None),
        'galeria_fotos': galeria_fotos,
        'memoria_pdf': row[8],
        'planos_pdf': row[9],
        'modelo_3d_glb': row[11],
        'vr_tour': row[12],
        'property_type': 'Residencial',
        'estimated_cost': row[5] * 0.8 if row[5] else 0,
        'price_memoria': 1800,
        'price_cad': 2500,
        'energy_rating': 'A',
        'characteristics_json': '{}',
        'habitaciones': 3,
        'banos': 2,
        'garaje': True,
        'plantas': 2,
        'm2_parcela_minima': row[4] / 0.33 if row[4] else 0,
        'm2_parcela_maxima': row[4] / 0.2 if row[4] else 0,
        'certificacion_energetica': 'A',
        'tipo_proyecto': 'Residencial',
        'ocr_text': row[13],  # From database column
        'nombre': row[2]  # Alias para compatibilidad
    }

    return project_dict

def show_project_detail_page(project_id: str):
    """Muestra la página de vista previa de un proyecto arquitectónico"""

    # Limpiar sidebar para vista dedicada
    st.sidebar.empty()

    # Obtener datos del proyecto
    conn = db.get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, architect_id, title, description, area_m2, price, 
               foto_principal, galeria_fotos, memoria_pdf, planos_pdf, 
               planos_dwg, modelo_3d_glb, vr_tour, ocr_text, created_at
        FROM projects
        WHERE id = ?
    """, (project_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        st.error("❌ Proyecto no encontrado")
        return

    # Parsear galeria_fotos si es JSON
    import json
    galeria_fotos = []
    if row[7]:  # galeria_fotos
        try:
            if isinstance(row[7], str):
                galeria_fotos = json.loads(row[7])
            elif isinstance(row[7], list):
                galeria_fotos = row[7]
        except:
            galeria_fotos = []

    # Extraer datos del proyecto
    project_data = {
        'id': row[0],
        'architect_id': row[1],
        'title': row[2],
        'description': row[3],
        'area_m2': row[4],
        'price': row[5],
        'files': {
            'fotos': galeria_fotos,
            'memoria': row[8],
            'planos': row[9],
            'modelo_3d': row[11],
            'vr_tour': row[12],
            'ocr_text': row[13]
        },
        'created_at': row[14],
        # Mapeos para compatibilidad
        'm2_construidos': row[4],  # area_m2
        'architect_name': 'Arquitecto Demo',  # Placeholder
        'foto_principal': row[6] if row[6] else (galeria_fotos[0] if galeria_fotos else None),
        'galeria_fotos': galeria_fotos,
        'memoria_pdf': row[8],
        'planos_pdf': row[9],
        'modelo_3d_glb': row[11],
        'vr_tour': row[12],
        'property_type': 'Residencial',
        'estimated_cost': row[5] * 0.8 if row[5] else 0,
        'price_memoria': 1800,
        'price_cad': 2500,
        'energy_rating': 'A',
        'characteristics': {},
        'habitaciones': 3,
        'banos': 2,
        'garaje': True,
        'plantas': 2,
        'm2_parcela_minima': row[4] / 0.33 if row[4] else 0,
        'm2_parcela_maxima': row[4] / 0.2 if row[4] else 0,
        'certificacion_energetica': 'A',
        'tipo_proyecto': 'Residencial'
    }

    gallery = normalize_gallery(project_data["galeria_fotos"])

    # Definir variables de login temprano para evitar errores
    client_logged_in = st.session_state.get("client_logged_in", False)
    client_email = st.session_state.get("client_email", "")

    # Calcular superficie mínima requerida
    m2_proyecto = project_data['m2_construidos'] or project_data['area_m2'] or 0
    if project_data['m2_parcela_minima']:
        superficie_minima = project_data['m2_parcela_minima']
    else:
        superficie_minima = m2_proyecto / 0.33 if m2_proyecto > 0 else 0

    # Título
    st.title(f"🏗️ {project_data['title']}")

    # Galería de fotos
    st.header("📸 Galería del Proyecto")

    # Obtener imágenes válidas
    project_images = get_project_display_image(project_id, 'gallery')

    if project_images:
        # Mostrar imágenes en grid
        cols = st.columns(min(len(project_images), 3))
        for idx, img_path in enumerate(project_images):
            with cols[idx % 3]:
                try:
                    st.image(img_path, width='stretch', caption=f"Imagen {idx + 1}")
                except Exception as e:
                    st.warning(f"No se pudo cargar la imagen {idx + 1}")
    else:
        st.info("No hay imágenes disponibles para este proyecto")

    # Información básica del proyecto
    st.header("📋 Información del Proyecto")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏠 Características Técnicas")
        st.write(f"**Superficie construida:** {m2_proyecto:.0f} m²")
        st.write(f"**Superficie mínima de terreno:** {superficie_minima:.0f} m²")
        if project_data['m2_parcela_maxima']:
            st.write(f"**Superficie máxima de terreno:** {project_data['m2_parcela_maxima']:.0f} m²")
        st.write(f"**Tipo:** {project_data['property_type'] or project_data['tipo_proyecto'] or 'Residencial'}")

        # Características específicas
        if project_data['habitaciones']:
            st.write(f"**Habitaciones:** {project_data['habitaciones']}")
        if project_data['banos']:
            st.write(f"**Baños:** {project_data['banos']}")
        if project_data['plantas']:
            st.write(f"**Plantas:** {project_data['plantas']}")
        if project_data['garaje']:
            st.write(f"**Garaje:** {'Sí' if project_data['garaje'] else 'No'}")

        # Certificación energética
        if project_data['certificacion_energetica'] or project_data['energy_rating']:
            rating = project_data['certificacion_energetica'] or project_data['energy_rating']
            st.write(f"**Certificación energética:** {rating}")

    with col2:
        st.subheader("💰 Información Económica")
        if project_data['estimated_cost']:
            st.write(f"**Coste de ejecución aproximado:** €{project_data['estimated_cost']:,.0f}")
        st.write("**Precio descarga proyecto completo:**")
        st.write(f"• PDF (Memoria completa): €{project_data['price_memoria']}")
        st.write(f"• CAD (Planos editables): €{project_data['price_cad']}")

    # Descripción
    if project_data['description']:
        st.header("📝 Descripción")
        st.write(project_data['description'])

    # Arquitecto
    if project_data['architect_name']:
        st.write(f"**Arquitecto:** {project_data['architect_name']}")

    # VISUALIZACIONES DEL PROYECTO - CINCO PESTAÑAS CLONADAS (SIN COMPRA)
    st.header("🏗️ Visualizaciones del Proyecto")

    # PESTAÑAS PARA ORGANIZAR EL CONTENIDO
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 DOSSIER", "🔍 ANÁLISIS IA", "📄 MEMORIA", "📐 PLANOS", "🏗️ 3D/VR"
    ])

    with tab1:
        st.header("📋 DOSSIER PREVENTA")
        if st.button("📋 Generar Dossier Completo", type="primary"):
            texto = project_data.get('ocr_text', "No hay datos en la DB")
            with st.spinner("Analizando proyecto..."):
                from modules.marketplace import ai_engine_groq as ai
                resumen = ai.generate_text(f"Genera un dossier de preventa profesional para este proyecto arquitectónico resumiendo en 200 palabras: materiales, estilo, características técnicas y valor añadido: {texto[:2500]}")
                st.success("📋 DOSSIER GENERADO")
                st.write(resumen)

    with tab2:
        st.header("🔍 ANÁLISIS CON IA")
        if st.button("🤖 Analizar Proyecto con Gemini", type="primary"):
            st.info("Para ver análisis detallados, ficha técnica completa, archivos 3D y realidad virtual, regístrate como cliente.")

    with tab3:
        st.header("📄 MEMORIA TÉCNICA")
        if st.button("📄 Generar Memoria Detallada", type="secondary"):
            st.info("Para ver análisis detallados, ficha técnica completa, archivos 3D y realidad virtual, regístrate como cliente.")

    with tab4:
        st.header("📐 PLANOS TÉCNICOS")
        if st.button("📐 Generar Plano Arquitectónico", type="secondary"):
            st.info("Para ver análisis detallados, ficha técnica completa, archivos 3D y realidad virtual, regístrate como cliente.")

    with tab5:
        st.header("🏗️ VISUALIZACIÓN 3D / VR")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🏗️ Generar Modelo 3D", type="secondary", use_container_width=True):
                st.info("Para ver análisis detallados, ficha técnica completa, archivos 3D y realidad virtual, regístrate como cliente.")
        with col2:
            if st.button("🥽 Visor VR Inmersivo", type="secondary", use_container_width=True):
                st.info("Para ver análisis detallados, ficha técnica completa, archivos 3D y realidad virtual, regístrate como cliente.")

    # 🔍 BUSCAR PROYECTOS SIMILARES (solo para usuarios logueados)
    if client_logged_in:
        st.header("🔍 Buscar Proyectos Similares")
        st.write("Encuentra otros proyectos que se ajusten a tus necesidades específicas")
        
        # Formulario de búsqueda
        with st.form("similar_projects_form"):
            st.markdown("### 🎯 Especifica tus criterios")
            
            col1, col2 = st.columns(2)
            
            with col1:
                presupuesto_max = st.number_input(
                    "💰 Presupuesto máximo (€)", 
                    min_value=0, 
                    value=int(project_data.get('price') or 0), 
                    step=10000,
                    help="Precio máximo que estás dispuesto a pagar"
                )
                
                area_deseada = st.number_input(
                    "📐 Área de construcción deseada (m²)", 
                    min_value=0, 
                    value=int(project_data.get('m2_construidos') or 0), 
                    step=10,
                    help="Superficie aproximada que quieres construir"
                )
            
            with col2:
                parcela_disponible = st.number_input(
                    "🏞️ Parcela disponible (m²)", 
                    min_value=0, 
                    value=int(project_data.get('m2_parcela_minima') or 0), 
                    step=50,
                    help="Tamaño de terreno que tienes disponible"
                )
                
                # Checkbox para buscar solo proyectos que quepan
                solo_compatibles = st.checkbox(
                    "Solo proyectos compatibles con mi parcela", 
                    value=True,
                    help="Filtrar proyectos cuya parcela mínima sea ≤ a tu terreno disponible"
                )
            
            # Botón de búsqueda
            submitted = st.form_submit_button("🔍 Buscar Proyectos Similares", type="primary", width='stretch')
        
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
            with st.spinner("Buscando proyectos similares..."):
                from modules.marketplace.compatibilidad import get_proyectos_compatibles
                proyectos = get_proyectos_compatibles(**search_params)
            
            # Filtrar para excluir el proyecto actual
            proyectos = [p for p in proyectos if str(p['id']) != str(project_id)]
            
            # Mostrar resultados
            st.markdown(f"### 🏗️ Proyectos similares encontrados: {len(proyectos)}")
            
            if not proyectos:
                st.warning("No se encontraron proyectos que cumplan con tus criterios. Prueba ampliando los límites.")
            else:
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
                            if st.button("Ver Detalles", key=f"similar_detail_{proyecto['id']}", width='stretch'):
                                st.query_params["selected_project"] = proyecto['id']
                                st.rerun()
                            
                            st.markdown("---")

    else:
        st.header("🔍 ¿Interesado en este proyecto?")
        st.info("Para ver planos detallados, ficha técnica completa, archivos 3D y realidad virtual, regístrate como cliente.")
        
        # 🔍 BUSCAR PROYECTOS COMPATIBLES (antes del registro)
        show_advanced_project_search(client_email=None)
        
        # Usuario no logueado - mostrar formulario de registro rápido
        st.subheader("📝 Regístrate para acceder")

        with st.form("registro_rapido"):
            col1, col2 = st.columns(2)

            with col1:
                nombre = st.text_input("Nombre", placeholder="Tu nombre")
                apellidos = st.text_input("Apellidos", placeholder="Tus apellidos")
                telefono = st.text_input("Teléfono", placeholder="+34 600 000 000")

            with col2:
                email = st.text_input("Email", placeholder="tu@email.com")
                confirmar_email = st.text_input("Confirmar Email", placeholder="tu@email.com")
                password = st.text_input("Contraseña", type="password", placeholder="Mínimo 6 caracteres")
                confirmar_password = st.text_input("Confirmar Contraseña", type="password", placeholder="Repite tu contraseña")
                direccion = st.text_input("Dirección", placeholder="Calle, Ciudad, Provincia")

            submitted = st.form_submit_button("🚀 Registrarme y Acceder", type="primary", width='stretch')

            if submitted:
                # Validaciones básicas
                if not nombre or not apellidos or not email or not password:
                    st.error("Por favor completa nombre, apellidos, email y contraseña")
                elif email != confirmar_email:
                    st.error("Los emails no coinciden")
                elif password != confirmar_password:
                    st.error("Las contraseñas no coinciden")
                elif len(password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                elif "@" not in email:
                    st.error("Por favor introduce un email válido")
                else:
                    # Registrar usuario en base de datos
                    try:
                        from werkzeug.security import generate_password_hash
                        conn = db.get_conn()
                        cursor = conn.cursor()

                        # Verificar si el email ya existe en users
                        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                        existing_user = cursor.fetchone()

                        if existing_user:
                            st.success("✅ Ya estabas registrado. Accediendo al portal...")
                        else:
                            # Insertar nuevo usuario con contraseña
                            full_name = f"{nombre} {apellidos}".strip()
                            hashed_password = generate_password_hash(password)
                            cursor.execute("""
                                INSERT INTO users (email, full_name, role, is_professional, password_hash, created_at)
                                VALUES (?, ?, 'client', 0, ?, datetime('now'))
                            """, (email, full_name, hashed_password))

                            # También insertar en clients para compatibilidad V2
                            cursor.execute("""
                                INSERT OR IGNORE INTO clients (name, email, phone, address, created_at)
                                VALUES (?, ?, ?, ?, datetime('now'))
                            """, (full_name, email, telefono, direccion))

                            st.success("✅ Registro completado. Accediendo al portal...")

                        conn.commit()

                        # Guardar interés en el proyecto
                        try:
                            cursor.execute("""
                                INSERT OR IGNORE INTO client_interests (email, project_id, created_at)
                                VALUES (?, ?, datetime('now'))
                            """, (email, project_id))
                            conn.commit()
                        except Exception as e:
                            st.warning(f"No se pudo guardar el interés: {e}")

                        conn.close()

                        # Auto-login con credenciales
                        st.session_state["client_logged_in"] = True
                        st.session_state["client_email"] = email
                        st.session_state["logged_in"] = True
                        st.session_state["user_email"] = email
                        st.session_state["user_name"] = full_name
                        st.session_state["role"] = "client"
                        st.session_state["user_role"] = "buyer"
                        st.session_state["has_transactions"] = False
                        st.session_state["has_properties"] = False
                        st.session_state["just_registered"] = True
                        st.session_state["registration_success"] = True

                        st.rerun()

                    except Exception as e:
                        st.error(f"Error en el registro: {e}")

        st.markdown("---")
        st.info("💡 **¿Ya tienes cuenta?** Si has realizado compras anteriores, usa tu email para acceder directamente.")

        # ═══════════════════════════════════════════════════════════════
        # MOSTRAR OPCIONES DESPUÉS DE REGISTRO EXITOSO (FUERA DEL FORMULARIO)
        # ═══════════════════════════════════════════════════════════════
        if st.session_state.get("registration_success"):
            # Limpiar el flag para no mostrarlo en futuras visitas
            del st.session_state["registration_success"]
            
            st.success("🎉 **¡Registro completado exitosamente!**")
            st.balloons()
            
            # Mensaje informativo claro
            st.info("✅ **Ahora tienes acceso completo a este proyecto y a todo el portal de cliente.**")
            
            # Opciones claras para el usuario
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👤 Ir a Mi Panel de Cliente", type="primary", width='stretch'):
                    st.query_params.update({
                        "page": "👤 Panel de Cliente",
                        "selected_project": project_id
                    })
                    st.rerun()
            
            with col2:
                if st.button("🔍 Seguir Explorando Proyectos", width='stretch'):
                    st.query_params.clear()
                    st.query_params["page"] = "Home"
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### 🎯 ¿Qué puedes hacer ahora?")
            st.markdown("• **Ver todos los detalles** del proyecto (planos, 3D, VR)")
            st.markdown("• **Comprar proyectos** completos (PDF + CAD)")  
            st.markdown("• **Acceder a tu panel** para gestionar todas tus compras")
            st.markdown("• **Buscar más proyectos** compatibles con tus necesidades")
            
            st.markdown("---")

    if client_logged_in and client_email:
        # Si acabamos de registrarnos, ya hemos mostrado las opciones arriba
        just_registered = st.session_state.get("just_registered", False)
        if not just_registered:
            st.success(f"✅ **Bienvenido de vuelta, {client_email}**")
            st.info("Ya puedes acceder al portal completo del cliente con todos los detalles del proyecto.")
            
            # Usuario ya logueado - ir al panel
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("👁️ Acceder al Portal de Cliente", width='stretch', type="primary"):
                    # Guardar datos del proyecto y cliente en session_state
                    st.session_state["selected_project_id"] = project_id
                    st.session_state["selected_project_for_panel"] = project_id
                    st.session_state["client_logged_in"] = True
                    st.session_state["buyer_email"] = client_email
                    
                    # Navegar usando query params (mismo método que el botón "Acceso Clientes" en HOME)
                    st.query_params.update({
                        "page": "👤 Panel de Cliente",
                        "selected_project": project_id
                    })
                    st.rerun()
        # Si acabamos de registrarnos, limpiar el flag pero continuar mostrando la página
        else:
            del st.session_state["just_registered"]

    # Botón volver
    if st.button("← Volver al Inicio"):
        st.query_params.clear()
        st.rerun()

    # Detener la ejecución para evitar mostrar contenido adicional
    st.stop()


def show_advanced_project_search(client_email=None):
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
        submitted = st.form_submit_button("🔍 Buscar Proyectos", type="primary", width='stretch')
    
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
            from modules.marketplace.compatibilidad import get_proyectos_compatibles
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
                    if st.button("Ver Detalles", key=f"search_detail_{proyecto['id']}", width='stretch'):
                        st.query_params["selected_project"] = proyecto['id']
                        st.rerun()
                    
                    st.markdown("---")


def get_project_by_id(project_id: str) -> dict:
    """Obtiene los datos básicos de un proyecto por su ID (Incluyendo OCR)"""
    try:
        conn = db.get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, title, description, m2_construidos, area_m2, price, estimated_cost,
                   price_memoria, price_cad, property_type, foto_principal, galeria_fotos,
                   memoria_pdf, planos_pdf, planos_dwg, modelo_3d_glb, vr_tour, energy_rating,
                   architect_name, characteristics_json, habitaciones, banos, garaje, plantas,
                   m2_parcela_minima, m2_parcela_maxima, certificacion_energetica, tipo_proyecto,
                   ocr_text  -- ⬅️ COLUMNA VITAL AÑADIDA
            FROM projects
            WHERE id = ?
        """, (project_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        # Retornar datos incluyendo el OCR para la IA
        return {
            'id': row[0],
            'nombre': row[1],
            'descripcion': row[2],
            'total_m2': row[3] or row[4],  # Usar m2_construidos o area_m2
            'coste_estimado': row[6] or 0,  # estimated_cost
            'imagen_principal': row[10],  # foto_principal
            'tipo_propiedad': row[9],  # property_type
            'precio': row[5] or 0,  # price
            'ocr_text': row[28], # ⬅️ ASIGNAMOS EL TEXTO REAL
        }
    except Exception as e:
        print(f"Error obteniendo proyecto {project_id}: {e}")
        return None