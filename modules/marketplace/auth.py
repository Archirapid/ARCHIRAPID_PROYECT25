import streamlit as st
from modules.marketplace.utils import get_user_by_email, db_conn
from werkzeug.security import check_password_hash

# Función de navegación unificada
def navigate_to(page_name):
    st.query_params["page"] = page_name
    st.session_state["selected_page"] = page_name
    st.rerun()

def show_login():
    if st.session_state.get('login_role') == 'admin':
        # Login especial para admin
        st.title("🔐 Acceso Administrativo")
        admin_password = st.text_input("Contraseña de Acceso Administrativo", type="password", key="admin_pass")
        if st.button("🚀 Acceder como Admin", key="admin_login_btn"):
            if admin_password == "admin123":
                st.session_state['role'] = 'admin'
                st.session_state['logged_in'] = True
                st.session_state['selected_page'] = "Intranet"
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
        return
    
    st.title("🔐 Iniciar Sesión")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="tu@email.com")
        password = st.text_input("Contraseña", type="password", placeholder="Tu contraseña")

        submitted = st.form_submit_button("🚀 Iniciar Sesión", type="primary")

        if submitted:
            if not email or not password:
                st.error("Por favor, completa todos los campos.")
                return

            user = authenticate_user(email, password)
            if user:
                st.session_state["logged_in"] = True
                st.session_state["email"] = email
                st.session_state["rol"] = user['role']
                
                user_role = user.get('role')
                if user_role == 'admin':
                    st.query_params["page"] = "Intranet"
                elif user_role == 'architect':
                    st.query_params["page"] = "Arquitectos (Marketplace)"
                elif user_role == 'services':
                    st.query_params["page"] = "👤 Panel de Proveedor"
                else:
                    st.query_params["page"] = "👤 Panel de Cliente"
                st.rerun()
            else:
                st.error("Credenciales incorrectas. Verifica tu email y contraseña.")

    st.markdown("---")
    st.markdown("¿No tienes cuenta? [Regístrate aquí](?page=Registro%20de%20Usuario)")

def authenticate_user(email, password):
    try:
        conn = db_conn()
        c = conn.cursor()
        c.execute("SELECT id, email, full_name, role, password_hash FROM users WHERE email = ?", (email,))
        row = c.fetchone()
        conn.close()

        if row and check_password_hash(row[4], password):
            return {
                "id": row[0],
                "email": row[1],
                "full_name": row[2],
                "role": row[3]
            }
    except Exception as e:
        st.error(f"Error de autenticación: {e}")

    return None

def show_registration():
    st.title("📝 Registro de Usuario")

    with st.form("registro_form"):
        st.subheader("📋 Información Personal")

        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo *", placeholder="Tu nombre completo")
        with col2:
            email = st.text_input("Email *", placeholder="tu@email.com")

        telefono = st.text_input("Teléfono", placeholder="+34 600 000 000")
        direccion = st.text_input("Dirección", placeholder="Calle, Ciudad, Provincia")

        st.subheader("🔐 Credenciales de Acceso")
        password = st.text_input("Contraseña *", type="password", placeholder="Mínimo 6 caracteres")
        password_confirm = st.text_input("Confirmar contraseña *", type="password", placeholder="Repite tu contraseña")

        st.subheader("👤 Tipo de Usuario")
        tipo_usuario = st.selectbox(
            "Selecciona tu perfil *",
            ["Cliente (Busco proyectos)", "Arquitecto (Vendo proyectos)", "Propietario (Subo fincas)"],
            index=0
        )

        if tipo_usuario == "Arquitecto (Vendo proyectos)":
            empresa = st.text_input("Empresa/Estudio", placeholder="Nombre de tu empresa")
            especialidad = st.selectbox("Especialidad", ["Arquitectura Residencial", "Arquitectura Comercial", "Urbanismo", "Interiorismo", "Otros"])
        else:
            empresa = ""
            especialidad = ""

        submitted = st.form_submit_button("🚀 Registrarme y Acceder", type="primary")

        if submitted:
            if not nombre or not email or not password:
                st.error("Por favor, completa los campos obligatorios marcados con *.")
                return

            if password != password_confirm:
                st.error("Las contraseñas no coinciden.")
                return

            if len(password) < 6:
                st.error("La contraseña debe tener al menos 6 caracteres.")
                return

            if tipo_usuario == "Cliente (Busco proyectos)":
                role = "client"
            elif tipo_usuario == "Arquitecto (Vendo proyectos)":
                role = "architect"
            else:
                role = "owner"

            try:
                from werkzeug.security import generate_password_hash
                hashed_password = generate_password_hash(password)

                conn = db_conn()
                c = conn.cursor()

                c.execute("""
                    INSERT INTO users (email, full_name, role, is_professional, password_hash, phone, address, company, specialty, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    email, nombre, role,
                    1 if role in ['architect', 'owner'] else 0,
                    hashed_password, telefono, direccion, empresa, especialidad
                ))

                conn.commit()
                conn.close()

                st.success("🎉 ¡Registro completado exitosamente!")

                st.session_state["logged_in"] = True
                st.session_state["email"] = email
                st.session_state["rol"] = role

                if role == 'admin':
                    navigate_to("Intranet")
                elif role == 'architect':
                    navigate_to("Arquitectos (Marketplace)")
                elif role == 'client':
                    navigate_to("👤 Panel de Cliente")
                else:
                    navigate_to("👤 Panel de Cliente")

            except Exception as e:
                st.error(f"Error en el registro: {e}")

    st.markdown("---")
    st.markdown("¿Ya tienes cuenta? [Inicia sesión aquí](?page=Iniciar%20Sesión)")