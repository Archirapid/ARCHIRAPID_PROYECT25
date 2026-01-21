# modules/marketplace/service_providers.py
import streamlit as st
import sqlite3
from datetime import datetime
from .utils import db_conn, save_upload
from werkzeug.security import generate_password_hash
import json

def show_service_provider_registration():
    """Formulario de registro para proveedores de servicios"""
    st.header("🏗️ Registro de Proveedor de Servicios")

    with st.form("service_provider_registration"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Nombre completo *", key="sp_name")
            email = st.text_input("Email *", key="sp_email")
            phone = st.text_input("Teléfono *", key="sp_phone")
            nif = st.text_input("NIF/CIF *", key="sp_nif")

        with col2:
            company = st.text_input("Empresa", key="sp_company")
            specialty = st.selectbox("Especialidad principal *",
                ["direccion_obra", "visado", "bim", "sostenibilidad", "ssl", "topografia", "estructuras", "instalaciones", "electricista", "constructor"],
                key="sp_specialty")
            experience_years = st.number_input("Años de experiencia", min_value=0, max_value=50, key="sp_experience")
            service_area = st.text_input("Área de servicio (provincia/ciudad)", key="sp_area")

        address = st.text_area("Dirección completa", key="sp_address")
        certifications = st.text_area("Certificaciones (una por línea)", key="sp_certifications",
            help="Ej: Arquitecto Superior, Aparejador, Coordinador SSL, etc.")

        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("Contraseña *", type="password", key="sp_password")
        with col4:
            confirm_password = st.text_input("Confirmar Contraseña *", type="password", key="sp_confirm_password")

        submitted = st.form_submit_button("Registrar como Proveedor de Servicios")

        if submitted:
            if not all([name, email, phone, nif, specialty, password, confirm_password]):
                st.error("Por favor complete todos los campos obligatorios (*)")
                return

            if password != confirm_password:
                st.error("Las contraseñas no coinciden")
                return

            if len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres")
                return

            try:
                conn = db_conn()
                c = conn.cursor()

                # Verificar si ya existe
                c.execute("SELECT id FROM service_providers WHERE email=?", (email,))
                if c.fetchone():
                    st.error("Ya existe un proveedor registrado con este email")
                    conn.close()
                    return

                # Crear ID único
                provider_id = f"sp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

                # Insertar proveedor
                c.execute("""
                    INSERT INTO service_providers
                    (id, name, email, nif, specialty, company, phone, address, certifications, experience_years, service_area, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (provider_id, name, email, nif, specialty, company, phone, address,
                      certifications, experience_years, service_area, datetime.utcnow().isoformat()))

                # También insertar en tabla users general
                password_hash = generate_password_hash(password)
                c.execute("""
                    INSERT INTO users (id, email, password_hash, full_name, role, created_at)
                    VALUES (?, ?, ?, ?, 'services', ?)
                """, (provider_id, email, password_hash, name, datetime.utcnow().isoformat()))

                conn.commit()
                conn.close()

                st.success("✅ ¡Registro completado exitosamente!")
                st.info("🎉 Ahora puedes cerrar sesión y acceder desde la Home usando el botón 'Acceso' en la parte superior con tu email y contraseña.")
                st.balloons()

                # Botón para ir a Home
                if st.button("🏠 Ir a Inicio", key="go_home_after_registration"):
                    st.query_params["page"] = "🏠 Inicio / Marketplace"
                    st.rerun()

            except Exception as e:
                st.error(f"Error en el registro: {str(e)}")

def show_service_provider_panel():
    """Panel de control para proveedores de servicios"""
    st.header("🏗️ Panel de Proveedor de Servicios")

    # Obtener datos del proveedor actual
    user_email = st.session_state.get("email", "")
    if not user_email:
        st.error("Debes iniciar sesión primero")
        return

    conn = db_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, specialty, company, phone, address, certifications, experience_years, service_area
        FROM service_providers WHERE email=?
    """, (user_email,))
    provider = c.fetchone()
    conn.close()

    if not provider:
        st.error("No se encontró información del proveedor")
        return

    provider_id, name, specialty, company, phone, address, certifications, experience_years, service_area = provider

    # Mostrar información del perfil
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📋 Información del Perfil")
        st.write(f"**Nombre:** {name}")
        st.write(f"**Especialidad:** {specialty.replace('_', ' ').title()}")
        st.write(f"**Empresa:** {company or 'No especificada'}")
        st.write(f"**Experiencia:** {experience_years} años")
        st.write(f"**Área de servicio:** {service_area or 'No especificada'}")

    with col2:
        st.subheader("📞 Contacto")
        st.write(f"**Teléfono:** {phone}")
        st.write(f"**Dirección:** {address or 'No especificada'}")

        if certifications:
            st.subheader("🎓 Certificaciones")
            for cert in certifications.split('\n'):
                if cert.strip():
                    st.write(f"• {cert.strip()}")

    # Mostrar asignaciones de servicios
    st.divider()
    st.subheader("📋 Asignaciones de Servicios")

    # Nueva conexión para la segunda query
    conn = db_conn()
    c = conn.cursor()
    c.execute("""
        SELECT sa.id, sa.servicio_tipo, sa.cliente_email, sa.proyecto_id, sa.precio_servicio,
               sa.estado, sa.fecha_asignacion, sa.fecha_completado, sa.notas,
               vp.nombre_cliente, vp.productos_comprados
        FROM service_assignments sa
        JOIN ventas_proyectos vp ON sa.venta_id = vp.id
        WHERE sa.proveedor_id = ?
        ORDER BY sa.fecha_asignacion DESC
    """, (provider_id,))

    assignments = c.fetchall()
    conn.close()

    if assignments:
        for assignment in assignments:
            (assignment_id, servicio_tipo, cliente_email, proyecto_id, precio_servicio,
             estado, fecha_asignacion, fecha_completado, notas,
             nombre_cliente, productos_comprados) = assignment

            estado_emoji = {
                "pendiente": "⏳",
                "en_progreso": "🔄",
                "completado": "✅",
                "cancelado": "❌"
            }.get(estado, "❓")

            with st.expander(f"{estado_emoji} {servicio_tipo.replace('_', ' ').title()} - {nombre_cliente} ({fecha_asignacion[:10]})"):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Cliente:** {nombre_cliente} ({cliente_email})")
                    st.write(f"**Proyecto ID:** {proyecto_id}")
                    st.write(f"**Productos:** {productos_comprados}")
                    st.write(f"**Precio del servicio:** {precio_servicio}€")

                with col2:
                    st.write(f"**Estado:** {estado.title()}")
                    st.write(f"**Fecha asignación:** {fecha_asignacion[:10]}")
                    if fecha_completado:
                        st.write(f"**Fecha completado:** {fecha_completado[:10]}")

                    # Controles de estado
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if estado == "pendiente" and st.button("▶️ Iniciar", key=f"start_{assignment_id}"):
                            update_assignment_status(assignment_id, "en_progreso")
                            st.rerun()
                    with col_b:
                        if estado == "en_progreso" and st.button("✅ Completar", key=f"complete_{assignment_id}"):
                            update_assignment_status(assignment_id, "completado")
                            st.rerun()
                    with col_c:
                        if estado in ["pendiente", "en_progreso"] and st.button("❌ Cancelar", key=f"cancel_{assignment_id}"):
                            update_assignment_status(assignment_id, "cancelado")
                            st.rerun()

                if notas:
                    st.write(f"**Notas:** {notas}")

                # Agregar notas
                nueva_nota = st.text_area("Agregar nota", key=f"nota_{assignment_id}", height=50)
                if st.button("💬 Agregar Nota", key=f"add_note_{assignment_id}") and nueva_nota.strip():
                    add_assignment_note(assignment_id, nueva_nota.strip())
                    st.rerun()
    else:
        st.info("No tienes asignaciones de servicios activas")

def show_service_contracts(provider_id, specialty):
    """Mostrar contratos de servicios para este proveedor"""
    st.subheader("📋 Contratos de Servicio")

    conn = db_conn()
    c = conn.cursor()

    # Buscar en ventas_proyectos donde se compraron servicios de esta especialidad
    c.execute("""
        SELECT vp.id, vp.proyecto_id, vp.cliente_email, vp.nombre_cliente,
               vp.productos_comprados, vp.total_pagado, vp.fecha_compra
        FROM ventas_proyectos vp
        WHERE vp.productos_comprados LIKE ?
        ORDER BY vp.fecha_compra DESC
    """, (f"%{specialty}%",))

    contracts = c.fetchall()
    conn.close()

    if contracts:
        for contract in contracts:
            contract_id, project_id, client_email, client_name, products, total, date = contract

            with st.expander(f"Contrato #{contract_id} - {client_name} ({date[:10]})"):
                st.write(f"**Cliente:** {client_name} ({client_email})")
                st.write(f"**Proyecto ID:** {project_id}")
                st.write(f"**Servicios contratados:** {products}")
                st.write(f"**Total:** {total}€")

                # Botón para marcar como completado (simulado)
                if st.button(f"Marcar completado #{contract_id}", key=f"complete_{contract_id}"):
                    st.success("✅ Servicio marcado como completado")
    else:
        st.info("No hay contratos activos para tu especialidad")

def show_services_marketplace():
    """Marketplace de servicios para clientes"""
    st.header("🛠️ Marketplace de Servicios Profesionales")

    # Filtros
    col1, col2, col3 = st.columns(3)

    with col1:
        specialty_filter = st.selectbox("Especialidad",
            ["todas", "direccion_obra", "visado", "bim", "sostenibilidad", "ssl", "electricista", "constructor"],
            format_func=lambda x: "Todas" if x == "todas" else x.replace('_', ' ').title())

    with col2:
        area_filter = st.text_input("Área geográfica", placeholder="Provincia o ciudad")

    with col3:
        experience_filter = st.slider("Mínima experiencia (años)", 0, 20, 0)

    # Buscar proveedores
    conn = db_conn()
    c = conn.cursor()

    query = """
        SELECT id, name, specialty, company, phone, experience_years, service_area, certifications
        FROM service_providers
        WHERE 1=1
    """
    params = []

    if specialty_filter != "todas":
        query += " AND specialty = ?"
        params.append(specialty_filter)

    if area_filter:
        query += " AND service_area LIKE ?"
        params.append(f"%{area_filter}%")

    if experience_filter > 0:
        query += " AND experience_years >= ?"
        params.append(experience_filter)

    c.execute(query, params)
    providers = c.fetchall()
    conn.close()

    if providers:
        st.success(f"Encontrados {len(providers)} proveedores")

        for provider in providers:
            provider_id, name, specialty, company, phone, experience, area, certifications = provider

            with st.expander(f"🏗️ {name} - {specialty.replace('_', ' ').title()}"):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Empresa:** {company or 'Profesional independiente'}")
                    st.write(f"**Experiencia:** {experience} años")
                    st.write(f"**Área:** {area or 'No especificada'}")
                    st.write(f"**Teléfono:** {phone}")

                    if certifications:
                        st.write("**Certificaciones:**")
                        for cert in certifications.split('\n')[:3]:  # Mostrar máximo 3
                            if cert.strip():
                                st.write(f"• {cert.strip()}")

                with col2:
                    # Simular contacto
                    if st.button("Contactar", key=f"contact_{provider_id}"):
                        st.success(f"✅ Contacto solicitado con {name}")
                        st.info("En una implementación real, aquí se enviaría un email o se abriría un chat.")
    else:
        st.info("No se encontraron proveedores con los criterios especificados")

def update_assignment_status(assignment_id, new_status):
    """Actualizar el estado de una asignación de servicio"""
    conn = db_conn()
    c = conn.cursor()

    if new_status == "completado":
        c.execute("""
            UPDATE service_assignments
            SET estado = ?, fecha_completado = datetime('now')
            WHERE id = ?
        """, (new_status, assignment_id))
    else:
        c.execute("""
            UPDATE service_assignments
            SET estado = ?
            WHERE id = ?
        """, (new_status, assignment_id))

    conn.commit()
    conn.close()

def add_assignment_note(assignment_id, note):
    """Agregar una nota a una asignación de servicio"""
    conn = db_conn()
    c = conn.cursor()

    # Obtener notas existentes
    c.execute("SELECT notas FROM service_assignments WHERE id = ?", (assignment_id,))
    result = c.fetchone()

    existing_notes = result[0] if result and result[0] else ""
    new_notes = f"{existing_notes}\n{datetime.utcnow().isoformat()}: {note}".strip()

    c.execute("""
        UPDATE service_assignments
        SET notas = ?
        WHERE id = ?
    """, (new_notes, assignment_id))

    conn.commit()
    conn.close()