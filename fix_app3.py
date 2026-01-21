with open('c:/ARCHIRAPID_PROYECT25/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Reemplazar la sección problemática
old_section = '''        with access_col:
                client_email = st.session_state.get("client_email", "")
                if not st.session_state.get("logged_in", False) or not st.session_state.get("email", ""):
                if not st.session_state.get('logged_in', False) or not st.session_state.get('email', ''):
                    # No hay sesión - ir a login
                    st.query_params["page"] = "Iniciar Sesión"
                    st.rerun()
                else:
                    # Hay sesión - determinar destino según rol
                    try:
                        from modules.marketplace.utils import get_user_by_email
                        user_data = get_user_by_email(st.session_state.get('email', ''))
                        if user_data:
                            user_role = user_data.get('role')
                            st.session_state["rol"] = user_role  # asegurar persistencia
                            if user_role == 'admin':
                                st.query_params["page"] = "Intranet"
                            elif user_role == 'architect':
                                st.query_params["page"] = "Arquitectos (Marketplace)"
                            else:  # client u otros
                                st.query_params["page"] = "👤 Panel de Cliente"
                        else:
                            # Fallback si no se puede determinar rol
                            st.query_params["page"] = "👤 Panel de Cliente"
                    except:
                        # Fallback a panel de cliente
                        st.query_params["page"] = "👤 Panel de Cliente"
                    st.rerun()'''

new_section = '''        with access_col:
            if st.button("� Acceder", key="btn_acceder"):
                if not st.session_state.get('logged_in', False) or not st.session_state.get('email', ''):
                    # No hay sesión - ir a login
                    st.query_params["page"] = "Iniciar Sesión"
                    st.rerun()
                else:
                    # Hay sesión - determinar destino según rol
                    try:
                        from modules.marketplace.utils import get_user_by_email
                        user_data = get_user_by_email(st.session_state.get('email', ''))
                        if user_data:
                            user_role = user_data.get('role')
                            st.session_state["rol"] = user_role  # asegurar persistencia
                            if user_role == 'admin':
                                st.query_params["page"] = "Intranet"
                            elif user_role == 'architect':
                                st.query_params["page"] = "Arquitectos (Marketplace)"
                            else:  # client u otros
                                st.query_params["page"] = "👤 Panel de Cliente"
                        else:
                            # Fallback si no se puede determinar rol
                            st.query_params["page"] = "👤 Panel de Cliente"
                    except:
                        # Fallback a panel de cliente
                        st.query_params["page"] = "👤 Panel de Cliente"
                    st.rerun()'''

content = content.replace(old_section, new_section)

with open('c:/ARCHIRAPID_PROYECT25/app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed access_col section')