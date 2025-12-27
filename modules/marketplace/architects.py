# modules/marketplace/architects.py
import streamlit as st
from modules.marketplace.utils import save_upload, db_conn, insert_user, get_user_by_email
from src import db
import uuid, json
from datetime import datetime, timedelta
from time import sleep

def check_subscription(arch_id):
    """Verifica si el arquitecto tiene suscripción activa."""
    conn = db.get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT plan_type, end_date, monthly_proposals_limit FROM subscriptions WHERE architect_id=? AND status='active' ORDER BY created_at DESC LIMIT 1", (arch_id,))
        row = cur.fetchone()
        if row:
            return {"plan": row[0], "end_date": row[1], "limit": row[2], "active": True}
        return {"active": False}
    except Exception:
        return {"active": False}
    finally:
        conn.close()

def main():
    st.header("🏗️ Portal para Arquitectos")

    # --- 1. LOGIN / IDENTIFICACIÓN ---
    if "arch_id" not in st.session_state:
        st.info("Accede a tu cuenta profesional.")
        with st.form("login_arch"):
            email = st.text_input("Email profesional")
            name = st.text_input("Nombre del Estudio / Arquitecto")
            submitted = st.form_submit_button("Entrar / Registrarse")
            
            if submitted:
                if not email or not name:
                    st.error("Campos requeridos.")
                else:
                    # Lookup real DB
                    user_data = get_user_by_email(email)
                    
                    if user_data:
                        st.session_state["arch_id"] = user_data["id"]
                        st.session_state["arch_name"] = user_data["name"]
                        st.session_state["arch_email"] = user_data["email"]
                        st.success(f"Bienvenido, {user_data['name']}")
                    else:
                        new_id = uuid.uuid4().hex
                        insert_user({"id": new_id, "name": name, "email": email, "role": "architect", "company": name})
                        st.session_state["arch_id"] = new_id
                        st.session_state["arch_name"] = name
                        st.session_state["arch_email"] = email
                        st.success("Cuenta creada. Bienvenido.")
                    sleep(1)
                    st.rerun()
        return

    # --- 2. DASHBOARD ---
    st.write(f"Conectado como: **{st.session_state.arch_name}**")
    
    sub_status = check_subscription(st.session_state["arch_id"])
    if sub_status["active"]:
        st.caption(f"✅ Suscripción Activa: **Plan {sub_status['plan']}** (Renueva: {sub_status['end_date']})")
    else:
        st.warning("⚠️ No tienes una suscripción activa. Tu visibilidad es limitada.")

    tab_planes, tab_subir, tab_proyectos, tab_matching, tab_ia = st.tabs(["💎 Planes", "📤 Subir Proyecto", "📂 Mis Proyectos", "🎯 Oportunidades", "🤖 Asistente IA"])

    with tab_ia:
        st.subheader("Boceto Generativo con IA (Gemini Flash)")
        st.info("Genera distribuciones preliminares para tus solares o proyectos.")
        
        c_ia_1, c_ia_2 = st.columns(2)
        with c_ia_1:
            ia_m2 = st.number_input("Superficie Finca (m²)", 200, 5000, 1000)
            ia_habs = st.slider("Habitaciones", 1, 6, 3)
            if st.button("✨ Generar Distribución"):
                with st.spinner("Gemini está dibujando..."):
                    from modules.marketplace import ai_engine
                    plan = ai_engine.plan_vivienda(ia_m2, ia_habs)
                    if "error" in plan:
                        st.error(plan["error"])
                    else:
                        st.session_state["ia_plan"] = plan
                        st.success("Distribución calculada.")
        
        with c_ia_2:
            if "ia_plan" in st.session_state:
                p = st.session_state["ia_plan"]
                st.write(p.get("descripcion", ""))
                st.dataframe(p.get("habitaciones", []))
                
                # SVG Generation
                if st.button("🎨 Renderizar Boceto"):
                    from modules.marketplace import ai_engine
                    total = p.get("total_m2", ia_m2*0.33)
                    svg = ai_engine.generate_sketch_svg(p.get("habitaciones", []), total)
                    
                    # Render SVG
                    import base64
                    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
                    html = f'<img src="data:image/svg+xml;base64,{b64}" width="100%"/>'
                    st.markdown("### Boceto Preliminar")
                    st.markdown(html, unsafe_allow_html=True)
                    with st.expander("Ver Código SVG"):
                        st.code(svg, language="xml")

    with tab_planes:
        st.subheader("Elige tu nivel de visibilidad")
        col1, col2, col3 = st.columns(3)
        
        plans = [
            {"name": "BASIC", "price": 29, "limit": 1, "fee": 10},
            {"name": "PRO", "price": 99, "limit": 5, "fee": 8},
            {"name": "ENTERPRISE", "price": 299, "limit": 999, "fee": 5}
        ]
        
        for p in plans:
            with col1 if p['name']=="BASIC" else col2 if p['name']=="PRO" else col3:
                with st.container(border=True):
                    st.markdown(f"### {p['name']}")
                    st.markdown(f"**{p['price']}€ / mes**")
                    st.write(f"- {p['limit']} Proyectos activos")
                    st.write(f"- {p['fee']}% Comisión plataforma")
                    if st.button(f"Contratar {p['name']}", key=f"plan_{p['name']}"):
                        # Crear suscripcion
                        try:
                            with db.transaction() as c:
                                sub_id = uuid.uuid4().hex
                                start = datetime.now()
                                end = start + timedelta(days=30)
                                c.execute("""
                                    INSERT INTO subscriptions (id, architect_id, plan_type, price, monthly_proposals_limit, commission_rate, status, start_date, end_date, created_at)
                                    VALUES (?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)
                                """, (sub_id, st.session_state["arch_id"], p['name'], p['price'], p['limit'], p['fee'], start.isoformat(), end.isoformat(), datetime.now().isoformat()))
                            st.success(f"¡Suscripción {p['name']} activada!")
                            sleep(1.5)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

    with tab_subir:
        if not sub_status["active"]:
            st.error("Necesitas un plan activo para subir proyectos.")
        else:
            st.subheader("Nuevo Proyecto de Catálogo")
            st.info("Los proyectos se 'emparejan' automáticamente con fincas compatibles basándose en la edificabilidad.")
            
            with st.form("new_project"):
                c1, c2 = st.columns(2)
                with c1:
                    title = st.text_input("Título del Modelo")
                    style = st.selectbox("Estilo", ["Moderno", "Mediterráneo", "Industrial", "Minimalista"])
                    floors = st.number_input("Plantas", min_value=1, value=1)
                with c2:
                    price = st.number_input("Precio Estimado Construcción (€)", min_value=50000.0)
                    area = st.number_input("Superficie Construida (m²)", min_value=30.0)
                    footprint = st.number_input("Ocupación en Planta (m²)", min_value=30.0, help="Huella del edificio en el suelo. Importante para matching.")

                desc = st.text_area("Descripción y Acabados")
                
                # Calculation of requirements
                min_plot = footprint / 0.33  # Regla aproximada del 33% de ocupacion maxima
                st.caption(f"📏 **Requisito Automático:** Este proyecto requerirá una parcela de al menos **{min_plot:.0f} m²** (asumiendo coef. ocupación 33%)")

                uploaded_file = st.file_uploader("Render Principal (JPG/PNG)", type=['jpg','png','jpeg'])
                uploaded_pdf = st.file_uploader("Memoria / Planos (PDF)", type=['pdf'])
                
                if st.form_submit_button("Publicar Proyecto"):
                    if not title or area <= 0:
                        st.error("Datos incompletos.")
                    else:
                         # Save files
                        img_path = save_upload(uploaded_file, prefix="proj_img") if uploaded_file else None
                        pdf_path = save_upload(uploaded_pdf, prefix="proj_pdf") if uploaded_pdf else None
                        
                        proj_data = {
                            "id": uuid.uuid4().hex,
                            "architect_id": st.session_state["arch_id"],
                            "title": title,
                            "description": desc,
                            "area_m2": area,
                            "price": price,
                            "architect_name": st.session_state["arch_name"],
                            "m2_parcela_minima": min_plot, # Guardamos el requisito
                            "style": style,
                            "plantas": floors,
                            "files_json": json.dumps({"pdf": pdf_path} if pdf_path else {}),
                            "foto_principal": img_path
                        }
                        
                        try:
                            # Usamos la funcion flexible de db.py
                            db.insert_project(proj_data)
                            st.success("✅ Proyecto publicado en el marketplace.")
                            sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error guardando: {e}")

    with tab_proyectos:
        st.subheader("Tu Catálogo")
        # Query simple manual
        conn = db.get_conn()
        import pandas as pd
        try:
            df = pd.read_sql_query("SELECT id, title, area_m2, price, m2_parcela_minima FROM projects WHERE architect_id=?", conn, params=(st.session_state["arch_id"],))
            if not df.empty:
                st.dataframe(df)
            else:
                st.info("No hay proyectos.")
        except Exception as e:
            st.error(e)
        finally:
            conn.close()

    with tab_matching:
        st.subheader("🎯 Oportunidades (Solares Compatibles)")
        if not sub_status["active"]:
             st.warning("Suscríbete para ver oportunidades y contactar clientes.")
        else:
            # 1. Traer mis proyectos
            try:
                conn = db.get_conn()
                my_projects = pd.read_sql_query("SELECT id, title, m2_parcela_minima FROM projects WHERE architect_id=?", conn, params=(st.session_state["arch_id"],))
                
                # 2. Traer todos los solares
                # Nota: En prod, hacer esto con SQL join espacial o filtros más inteligentes
                all_plots = pd.read_sql_query("SELECT id, title, m2, province, price, description FROM plots", conn)
                
                if my_projects.empty:
                    st.info("Sube proyectos primero para encontrar solares compatibles.")
                elif all_plots.empty:
                    st.info("No hay solares registrados en la plataforma aún.")
                else:
                    st.write(f"Analizando compatibilidad de tus **{len(my_projects)} proyectos** con **{len(all_plots)} solares** disponibles...")
                    
                    found_matches = False
                    
                    for idx, plot in all_plots.iterrows():
                        # Lógica simple de matching: El solar debe ser mayor que el requerimiento mínimo del proyecto
                        # Convertimos a numérico por si acaso
                        plot_m2 = float(plot['m2']) if plot['m2'] else 0
                        
                        compatible_projects = my_projects[my_projects['m2_parcela_minima'] <= plot_m2]
                        
                        if not compatible_projects.empty:
                            found_matches = True
                            with st.expander(f"📍 Solar en {plot['province']} - {plot['title']} ({plot_m2} m²)", expanded=True):
                                c1, c2 = st.columns([3, 1])
                                with c1:
                                    st.write(f"**Precio:** {plot['price']}€")
                                    st.write(f"_{plot['description']}_")
                                    st.write("---")
                                    st.write(f"✅ **{len(compatible_projects)} Proyectos Compatibles:**")
                                    for idx_p, proj in compatible_projects.iterrows():
                                        st.write(f"- 🏠 **{proj['title']}** (Req: {proj['m2_parcela_minima']:.0f} m²)")
                                    
                                    # AI Analysis
                                    with st.expander("🤖 Análisis de Viabilidad IA"):
                                        if st.button("Analizar Compatibilidad", key=f"ai_{plot['id']}"):
                                            with st.spinner("Gemini analizando normativa y encaje..."):
                                                from modules.marketplace import ai_engine
                                                prompt = f"Analiza la viabilidad preliminar de construir un proyecto residencial en un solar de {plot['m2']} m2 en {plot['province']}. Descripción del terreno: {plot['description']}. Precio suelo: {plot['price']}€. Dame 3 pros y 1 contra."
                                                analysis = ai_engine.generate_text(prompt)
                                                st.write(analysis)
                                
                                with c2:
                                    # Formulario de propuesta rápida
                                    st.markdown(f"**Proponer para: {plot['title']}**")
                                    proj_selected = st.selectbox("Elige Proyecto", compatible_projects['title'], key=f"sel_{plot['id']}")
                                    msg = st.text_area("Mensaje al Propietario", "Hola, me interesa este solar para mi proyecto...", key=f"msg_{plot['id']}")
                                    bid_price = st.number_input("Oferta / Precio Proyecto (€)", value=0.0, key=f"prc_{plot['id']}")
                                    
                                    if st.button("Enviar 🚀", key=f"btn_{plot['id']}"):
                                        # Encontrar ID del proyecto seleccionado
                                        proj_id = compatible_projects[compatible_projects['title'] == proj_selected].iloc[0]['id']
                                        
                                        prop_data = {
                                            "id": uuid.uuid4().hex,
                                            "architect_id": st.session_state["arch_id"],
                                            "plot_id": plot['id'],
                                            "project_id": proj_id,
                                            "message": msg,
                                            "price": bid_price,
                                            "status": "pending",
                                            "created_at": datetime.now().isoformat()
                                        }
                                        try:
                                            db.insert_proposal(prop_data)
                                            st.success("Propuesta enviada correctamente.")
                                        except Exception as e:
                                            st.error(f"Error al enviar: {e}")

                    if not found_matches:
                        st.info("No se encontraron solares compatibles con tus proyectos actuales (por requisitos de superficie).")
            
            except Exception as e:
                st.error(f"Error cargando oportunidades: {e}")
            finally:
                if 'conn' in locals(): conn.close()

