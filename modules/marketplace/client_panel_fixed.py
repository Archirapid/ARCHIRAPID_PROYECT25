# modules/marketplace/client_panel.py
import streamlit as st
from modules.marketplace.utils import db_conn
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

        # Buscar transacciones (compras/reservas)
        cursor.execute("SELECT * FROM reservations WHERE buyer_email=?", (auto_email,))
        transactions = cursor.fetchall()

        # Si no tiene transacciones, buscar si es propietario con fincas publicadas
        if not transactions:
            cursor.execute("SELECT * FROM plots WHERE owner_email=?", (auto_email,))
            owner_plots = cursor.fetchall()
        else:
            owner_plots = []

        conn.close()

        # Auto-login si tiene transacciones O fincas como propietario
        if transactions or owner_plots:
            st.session_state["client_logged_in"] = True
            st.session_state["client_email"] = auto_email
            st.session_state["user_role"] = "buyer" if transactions else "owner"
            st.session_state["has_transactions"] = len(transactions) > 0
            st.session_state["has_properties"] = len(owner_plots) > 0

            role_text = "comprador" if transactions else "propietario"
            st.info(f"🔄 Auto-acceso concedido como {role_text} para {auto_email}")

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
                
                # Buscar transacciones (compras/reservas)
                cursor.execute("SELECT * FROM reservations WHERE buyer_email=?", (email,))
                transactions = cursor.fetchall()
                
                # Si no tiene transacciones, buscar si es propietario con fincas publicadas
                if not transactions:
                    cursor.execute("SELECT * FROM plots WHERE owner_email=?", (email,))
                    owner_plots = cursor.fetchall()
                else:
                    owner_plots = []
                
                # Si no tiene transacciones ni propiedades, verificar si está registrado como cliente
                is_registered_client = False
                if not transactions and not owner_plots:
                    cursor.execute("SELECT id, name FROM clients WHERE email = ?", (email,))
                    client_record = cursor.fetchone()
                    is_registered_client = client_record is not None
                
                conn.close()
                
                # Permitir acceso si tiene transacciones, fincas como propietario O está registrado como cliente
                if transactions or owner_plots or is_registered_client:
                    st.session_state["client_logged_in"] = True
                    st.session_state["client_email"] = email
                    
                    # Determinar el rol basado en la prioridad: transacciones > propiedades > cliente registrado
                    if transactions:
                        user_role = "buyer"
                        role_text = "comprador"
                    elif owner_plots:
                        user_role = "owner" 
                        role_text = "propietario"
                    else:
                        # Cliente registrado sin transacciones ni propiedades
                        user_role = "buyer"  # Por defecto buyer para poder comprar proyectos
                        role_text = "cliente registrado"
                    
                    st.session_state["user_role"] = user_role
                    st.session_state["has_transactions"] = len(transactions) > 0
                    st.session_state["has_properties"] = len(owner_plots) > 0
                    
                    st.success(f"✅ Acceso concedido como {role_text} para {email}")
                    st.rerun()
                else:
                    st.error("No se encontraron transacciones, propiedades ni registro para este email")
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
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state["client_logged_in"] = False
                for key in ["client_email", "user_role", "has_transactions", "has_properties", "selected_project_for_panel"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        # Mostrar rol del usuario
        role_emoji = "🛒" if user_role == "buyer" else "🏠"
        role_text = "Comprador" if user_role == "buyer" else "Propietario"
        st.success(f"{role_emoji} **Bienvenido/a {role_text}** - {client_email}")
        
        # 🔍 MODO 3: Usuario interesado en un proyecto (sin transacciones)
        selected_project_for_panel = st.session_state.get("selected_project_for_panel")
        if user_role == "buyer" and not has_transactions and selected_project_for_panel:
            show_project_interest_panel(selected_project_for_panel)
            return
        
        # Contenido diferente según el rol
        if user_role == "buyer":
            show_buyer_panel(client_email)
        elif user_role == "owner":
            show_owner_panel_v2(client_email)
        else:
            st.error("Error: No se pudo determinar el tipo de panel apropiado")
            st.stop()

def show_selected_project_panel(client_email: str, project_id: str):
    """Panel para mostrar proyecto seleccionado con detalles completos y opciones de compra"""
    st.subheader("🏗️ Proyecto Arquitectónico Seleccionado")

    # Obtener datos completos del proyecto
    conn = db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description, m2_construidos, area_m2, price, estimated_cost,
               price_memoria, price_cad, property_type, foto_principal, galeria_fotos,
               memoria_pdf, planos_pdf, planos_dwg, modelo_3d_glb, vr_tour, energy_rating,
               architect_name, characteristics_json, habitaciones, banos, garaje, plantas,
               m2_parcela_minima, m2_parcela_maxima, certificacion_energetica, tipo_proyecto
        FROM projects
        WHERE id = ?
    """, (project_id,))
    row = cursor.fetchone()

    if not row:
        st.error("❌ Proyecto no encontrado")
        conn.close()
        return

    # Extraer datos del proyecto
    project_data = {
        'id': row[0],
        'title': row[1],
        'description': row[2],
        'm2_construidos': row[3],
        'area_m2': row[4],
        'price': row[5],
        'estimated_cost': row[6],
        'price_memoria': row[7] or 1800,
        'price_cad': row[8] or 2500,
        'property_type': row[9],
        'foto_principal': row[10],
        'galeria_fotos': row[11],
        'memoria_pdf': row[12],
        'planos_pdf': row[13],
        'planos_dwg': row[14],
        'modelo_3d_glb': row[15],
        'vr_tour': row[16],
        'energy_rating': row[17],
        'architect_name': row[18],
        'characteristics': json.loads(row[19]) if row[19] else {},
        'habitaciones': row[20],
        'banos': row[21],
        'garaje': row[22],
        'plantas': row[23],
        'm2_parcela_minima': row[24],
        'm2_parcela_maxima': row[25],
        'certificacion_energetica': row[26],
        'tipo_proyecto': row[27]
    }

    # Calcular superficie mínima requerida
    m2_proyecto = project_data['m2_construidos'] or project_data['area_m2'] or 0
    if project_data['m2_parcela_minima']:
        superficie_minima = project_data['m2_parcela_minima']
    else:
        superficie_minima = m2_proyecto / 0.33 if m2_proyecto > 0 else 0

    # Título principal
    st.title(f"🏗️ {project_data['title']}")
    st.markdown(f"**👨‍💼 Arquitecto:** {project_data['architect_name'] or 'No especificado'}")

    # Galería completa de fotos
    st.header("📸 Galería Completa del Proyecto")

    # Obtener imágenes válidas usando la función existente
    from modules.marketplace.plot_detail import get_project_images
    project_images = get_project_images({
        'foto_principal': project_data['foto_principal'],
        'galeria_fotos': json.loads(project_data['galeria_fotos']) if isinstance(project_data['galeria_fotos'], str) else project_data['galeria_fotos']
    })

    if project_images:
        # Mostrar imágenes en grid responsivo
        cols = st.columns(min(len(project_images), 3))
        for idx, img_path in enumerate(project_images):
            with cols[idx % 3]:
                try:
                    st.image(img_path, width='stretch', caption=f"Imagen {idx + 1}")
                except Exception as e:
                    st.warning(f"No se pudo cargar la imagen {idx + 1}")
    else:
        st.info("No hay imágenes disponibles para este proyecto")

    # Información técnica completa
    st.header("📋 Información Técnica Completa")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏠 Características Constructivas")
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
        st.write(f"• 📄 PDF (Memoria completa): €{project_data['price_memoria']}")
        st.write(f"• 🖥️ CAD (Planos editables): €{project_data['price_cad']}")
        total_price = project_data['price_memoria'] + project_data['price_cad']
        st.write(f"• 💰 **TOTAL:** €{total_price}")

    # Descripción completa
    if project_data['description']:
        st.header("📝 Descripción del Proyecto")
        st.write(project_data['description'])

    # Características adicionales
    if project_data['characteristics']:
        st.header("✨ Características Adicionales")
        chars = project_data['characteristics']
        if isinstance(chars, dict):
            for key, value in chars.items():
                st.write(f"• **{key}:** {value}")

    # SISTEMA DE COMPRA
    st.header("🛒 Adquirir Proyecto Completo")

    # Verificar si ya compró este proyecto
    cursor.execute("SELECT id FROM ventas_proyectos WHERE proyecto_id = ? AND cliente_email = ?", (project_id, client_email))
    ya_comprado = cursor.fetchone()
    conn.close()

    if ya_comprado:
        st.success("✅ **Ya has adquirido este proyecto**")
        st.info("Puedes descargar los archivos desde la sección 'Mis Proyectos'")

        # Mostrar botones de descarga
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 Descargar Memoria PDF", use_container_width=True, type="primary"):
                st.info("Descarga iniciada... (simulado)")
        with col2:
            if st.button("🖥️ Descargar Planos CAD", use_container_width=True, type="primary"):
                st.info("Descarga iniciada... (simulado)")
        with col3:
            if st.button("🏗️ Descargar Modelo 3D", use_container_width=True, type="primary"):
                st.info("Descarga iniciada... (simulado)")

    else:
        # Formulario de compra
        st.info("💳 Completa tu compra para acceder a todos los archivos del proyecto")

        with st.form("compra_proyecto"):
            st.subheader("📋 Datos de Facturación")

            col1, col2 = st.columns(2)
            with col1:
                nombre_fact = st.text_input("Nombre completo", placeholder="Nombre y apellidos")
                email_fact = st.text_input("Email", value=client_email, disabled=True)
                telefono_fact = st.text_input("Teléfono", placeholder="+34 600 000 000")

            with col2:
                direccion_fact = st.text_area("Dirección completa", placeholder="Calle, número, piso, CP, ciudad")
                nif_fact = st.text_input("NIF/CIF", placeholder="12345678A")

            st.subheader("🛒 Productos a Comprar")

            # Opciones de compra
            col_pdf, col_cad, col_3d = st.columns(3)

            with col_pdf:
                comprar_pdf = st.checkbox(f"📄 Memoria PDF - €{project_data['price_memoria']}", value=True)
                if project_data['memoria_pdf']:
                    st.caption("✅ Archivo disponible")
                else:
                    st.caption("⚠️ Archivo no disponible")

            with col_cad:
                comprar_cad = st.checkbox(f"🖥️ Planos CAD - €{project_data['price_cad']}", value=True)
                if project_data['planos_dwg']:
                    st.caption("✅ Archivo disponible")
                else:
                    st.caption("⚠️ Archivo no disponible")

            with col_3d:
                comprar_3d = st.checkbox("🏗️ Modelo 3D - €500" if project_data.get('modelo_3d_glb') else "🏗️ Modelo 3D - No disponible", disabled=not project_data.get('modelo_3d_glb'))

            # Cálculo total
            total = 0
            if comprar_pdf: total += project_data['price_memoria']
            if comprar_cad: total += project_data['price_cad']
            if comprar_3d: total += 500

            st.markdown(f"### 💰 **Total a pagar: €{total}**")

            # Método de pago (simulado)
            st.subheader("💳 Método de Pago")
            metodo_pago = st.selectbox("Selecciona método de pago",
                                      ["💳 Tarjeta de Crédito", "🏦 Transferencia Bancaria", "📱 Bizum"],
                                      help="Pago simulado - en producción se integraría con pasarela real")

            # Términos y condiciones
            aceptar_terminos = st.checkbox("✅ Acepto los términos y condiciones de compra")
            aceptar_privacidad = st.checkbox("✅ Acepto la política de privacidad")

            # Botón de compra
            submitted = st.form_submit_button("🚀 Completar Compra", type="primary", use_container_width=True)

            if submitted:
                if not nombre_fact or not telefono_fact or not direccion_fact or not nif_fact:
                    st.error("❌ Por favor completa todos los campos obligatorios")
                elif not aceptar_terminos or not aceptar_privacidad:
                    st.error("❌ Debes aceptar los términos y condiciones")
                elif total == 0:
                    st.error("❌ Debes seleccionar al menos un producto")
                else:
                    # Simular proceso de compra
                    with st.spinner("Procesando pago..."):
                        import time
                        time.sleep(2)

                    # Registrar venta en base de datos
                    try:
                        conn = db_conn()
                        cursor = conn.cursor()

                        # Insertar venta
                        cursor.execute("""
                            INSERT INTO ventas_proyectos
                            (proyecto_id, cliente_email, nombre_cliente, telefono, direccion, nif,
                             productos_comprados, total_pagado, metodo_pago, fecha_compra)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                        """, (project_id, client_email, nombre_fact, telefono_fact, direccion_fact, nif_fact,
                              f"PDF:{comprar_pdf},CAD:{comprar_cad},3D:{comprar_3d}", total, metodo_pago))

                        conn.commit()
                        conn.close()

                        st.success("🎉 **¡Compra completada con éxito!**")
                        st.balloons()

                        # Mostrar resumen
                        st.info(f"📧 Recibirás un email de confirmación en {client_email}")
                        st.info("📄 Los archivos estarán disponibles para descarga en 'Mis Proyectos'")

                        # Limpiar query params para evitar re-compra
                        if "selected_project" in st.query_params:
                            del st.query_params["selected_project"]

                        st.rerun()

                    except Exception as e:
                        st.error(f"Error al procesar la compra: {e}")

    # FINCAS COMPATIBLES DEL USUARIO
    st.header("🏠 Fincas Compatibles")

    # Obtener fincas del usuario (compradas o propias)
    conn = db_conn()
    cursor = conn.cursor()

    # Fincas compradas
    cursor.execute("""
        SELECT p.id, p.title, p.surface_m2, p.buildable_m2
        FROM reservations r
        JOIN plots p ON r.plot_id = p.id
        WHERE r.buyer_email = ?
    """, (client_email,))

    fincas_compradas = cursor.fetchall()

    # Fincas propias (si es propietario)
    cursor.execute("""
        SELECT id, title, surface_m2, buildable_m2
        FROM plots
        WHERE owner_email = ?
    """, (client_email,))

    fincas_propias = cursor.fetchall()
    conn.close()

    fincas_usuario = fincas_compradas + fincas_propias

    if fincas_usuario:
        for finca in fincas_usuario:
            finca_id, finca_title, surface_m2, buildable_m2 = finca

            # Calcular superficie edificable
            superficie_edificable = buildable_m2 if buildable_m2 else surface_m2 * 0.33

            # Verificar compatibilidad
            compatible = False
            if m2_proyecto <= superficie_edificable:
                compatible = True

            with st.expander(f"🏠 {finca_title} - {'✅ Compatible' if compatible else '❌ No compatible'}", expanded=compatible):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Superficie total:** {surface_m2} m²")
                    st.write(f"**Superficie edificable:** {superficie_edificable:.0f} m²")
                    st.write(f"**Proyecto requiere:** {m2_proyecto:.0f} m²")

                with col2:
                    if compatible:
                        st.success("🎯 **¡Perfecto match!** Este proyecto cabe en tu finca")
                        if st.button(f"🚀 Diseñar en {finca_title}", key=f"design_{finca_id}", use_container_width=True):
                            st.info("🎨 Redirigiendo al diseñador... (próximamente)")
                    else:
                        deficit = m2_proyecto - superficie_edificable
                        st.warning(f"⚠️ Necesitas {deficit:.0f} m² más de superficie edificable")
    else:
        st.info("No tienes fincas registradas. Para usar este proyecto, primero compra una finca compatible.")

    # ACCIONES ADICIONALES
    st.header("🎯 ¿Qué deseas hacer ahora?")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📋 Ver Más Proyectos", use_container_width=True):
            st.query_params.clear()
            st.query_params["page"] = "🏠 HOME"
            st.rerun()

    with col2:
        if st.button("🛒 Mi Historial de Compras", use_container_width=True):
            # Limpiar proyecto seleccionado para mostrar panel normal
            if "selected_project" in st.query_params:
                del st.query_params["selected_project"]
            st.rerun()

    with col3:
        if st.button("📧 Contactar Arquitecto", use_container_width=True):
            st.info(f"📧 Contacto: {project_data['architect_name'] or 'Equipo ARCHIRAPID'}")
            st.write("Email: proyectos@archirapid.com")
            st.write("Teléfono: +34 900 123 456")

def show_buyer_panel(client_email):
    """Panel para compradores con transacciones e intereses"""
    
    # Pestañas para organizar el contenido
    tab_intereses, tab_transacciones = st.tabs(["⭐ Mis Proyectos de Interés", "📋 Mis Transacciones"])
    
    with tab_intereses:
        show_client_interests(client_email)
    
    with tab_transacciones:
        show_client_transactions(client_email)

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

# Añadir import necesario
import os


def show_project_interest_panel(project_id):
    st.subheader("🏗️ Proyecto Seleccionado")

    from modules.marketplace.project_detail import get_project_by_id
    project = get_project_by_id(project_id)

    if not project:
        st.error("Proyecto no encontrado")
        return

    st.markdown(f"### {project['nombre']}")
    st.markdown(f"**Superficie:** {project['total_m2']} m²")
    st.markdown(f"**Coste estimado:** €{project['coste_estimado']:,.0f}")

    img = project.get("imagen_principal")
    if img:
        st.image(f"assets/projects/{img}", use_container_width=True)

    st.markdown("---")
    st.subheader("💳 Acciones")

    if st.button("Comprar Proyecto", type="primary"):
        st.success("Compra simulada realizada")
        st.info("Ahora puedes descargar memoria, planos y archivos 3D")
