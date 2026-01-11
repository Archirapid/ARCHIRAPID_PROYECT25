# modules/marketplace/project_detail.py
"""
Página de detalles de proyecto arquitectónico
Vista previa básica para usuarios no registrados
"""

import streamlit as st
import json
from modules.marketplace.plot_detail import get_project_images
from src import db

def show_project_detail_page(project_id: str):
    """Muestra la página de vista previa de un proyecto arquitectónico"""

    # Limpiar sidebar para vista dedicada
    st.sidebar.empty()

    # Obtener datos del proyecto
    conn = db.get_conn()
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
    conn.close()

    if not row:
        st.error("❌ Proyecto no encontrado")
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
    project_images = get_project_images({
        'foto_principal': project_data['foto_principal'],
        'galeria_fotos': json.loads(project_data['galeria_fotos']) if isinstance(project_data['galeria_fotos'], str) else project_data['galeria_fotos']
    })

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

    # RESUMEN INTELIGENTE CON IA
    st.header("🤖 Resumen Inteligente con IA")

    if st.button("Generar Resumen del Proyecto con IA", key="btn_ia_summary"):
        if project_data.get("memoria_pdf"):
            try:
                import PyPDF2
                with open(project_data["memoria_pdf"], "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages[:5]:  # Limitar a primeras 5 páginas para no exceder tokens
                        text += page.extract_text() + "\n"

                if text.strip():
                    prompt = f"Resume este proyecto arquitectónico en español, destacando características principales, distribución de espacios, materiales utilizados y aspectos técnicos relevantes. Sé conciso pero informativo:\n\n{text[:3000]}"
                    
                    from modules.marketplace import ai_engine_groq as ai
                    summary = ai.generate_text(prompt)
                    
                    if "Error:" in summary:
                        st.error(summary)
                    else:
                        st.success("✅ Resumen generado por IA:")
                        st.write(summary)
                else:
                    st.warning("No se pudo extraer texto del PDF.")
            except ImportError:
                st.error("Librería PyPDF2 no instalada. Instala con: pip install PyPDF2")
            except Exception as e:
                st.error(f"Error generando resumen: {e}")
        else:
            st.info("No hay memoria PDF disponible para este proyecto.")

    # VISUALIZACIONES DEL PROYECTO
    st.header("🏗️ Visualizaciones del Proyecto")

    tab_3d, tab_vr, tab_fotos = st.tabs(["🎥 3D", "🥽 VR", "🖼️ Fotos / Planos"])

    with tab_3d:
        if client_logged_in:
            st.markdown("#### 🎥 Visor 3D del Proyecto")
            if project_data.get("modelo_3d_glb"):
                # Mostrar visor 3D completo
                rel_path = str(project_data["modelo_3d_glb"]).replace("\\", "/").lstrip("/")
                model_url = f"http://127.0.0.1:8765/{rel_path}".replace(" ", "%20")
                try:
                    # Usar la función three_html_for definida en app.py
                    from app import three_html_for
                    html_final = three_html_for(model_url, str(project_data["id"]))
                    st.components.v1.html(html_final, height=700, scrolling=False)
                except Exception as e:
                    st.error(f"Error cargando visor 3D: {e}")
            else:
                st.info("Este proyecto no tiene modelo 3D disponible.")
        else:
            st.info("🔒 Para ver el modelo 3D interactivo completo, regístrate como cliente.")
            st.markdown("**Vista previa limitada:** Los modelos 3D se desbloquean tras registro.")

    with tab_vr:
        if client_logged_in:
            st.markdown("#### 🥽 Visor de Realidad Virtual")
            if project_data.get("modelo_3d_glb"):
                rel = str(project_data["modelo_3d_glb"]).replace("\\", "/").lstrip("/")
                glb_url = f"http://127.0.0.1:8765/{rel}".replace(" ", "%20")
                viewer_url = f"http://127.0.0.1:8765/static/vr_viewer.html?model={glb_url}"
                st.markdown(
                    f'<a href="{viewer_url}" target="_blank">'
                    f'<button style="padding:10px 16px;border-radius:6px;background:#0b5cff;color:#fff;border:none;">'
                    f"Abrir experiencia VR en nueva pestaña"
                    f"</button></a>",
                    unsafe_allow_html=True,
                )
                st.caption("Se abrirá el visor VR en una nueva pestaña. Requiere navegador con WebXR.")
            else:
                st.info("Este proyecto no tiene modelo VR disponible.")
        else:
            st.info("🔒 Para acceder a la experiencia VR completa, regístrate como cliente.")
            st.markdown("**Vista previa:** VR disponible tras registro.")

    with tab_fotos:
        if client_logged_in:
            st.markdown("#### 🖼️ Galería Completa de Fotos y Planos")
            # Foto principal
            if project_data.get("foto_principal"):
                rel = project_data["foto_principal"].replace("\\", "/").lstrip("/")
                url = f"http://127.0.0.1:8765/{rel}"
                st.image(url, width=400, caption="Foto Principal")
            # Galería adicional
            if project_data.get("galeria_fotos"):
                st.subheader("Galería Adicional")
                for idx, foto in enumerate(project_data["galeria_fotos"]):
                    if foto:
                        rel = foto.replace("\\", "/").lstrip("/")
                        url = f"http://127.0.0.1:8765/{rel}"
                        st.image(url, width=300, caption=f"Imagen {idx + 1}")
            # Planos
            if project_data.get("planos_pdf") or project_data.get("planos_dwg"):
                st.subheader("Planos Técnicos")
                if project_data.get("planos_pdf"):
                    st.download_button("📄 Descargar Planos PDF", data=open(project_data["planos_pdf"], "rb"), file_name="planos.pdf")
                if project_data.get("planos_dwg"):
                    st.download_button("📐 Descargar Planos DWG", data=open(project_data["planos_dwg"], "rb"), file_name="planos.dwg")
        else:
            st.info("🔒 Para ver la galería completa de fotos y planos, regístrate como cliente.")
            st.markdown("**Vista previa limitada:**")
            # Mostrar solo foto principal como preview
            if project_data.get("foto_principal"):
                rel = project_data["foto_principal"].replace("\\", "/").lstrip("/")
                url = f"http://127.0.0.1:8765/{rel}"
                st.image(url, width=300, caption="Vista Previa - Foto Principal")

    # Botón "Saber más" - Registro/Login
    st.header("🔍 ¿Interesado en este proyecto?")
    
    # Verificar si el usuario ya está logueado
    client_logged_in = st.session_state.get("client_logged_in", False)
    client_email = st.session_state.get("client_email", "")

    if client_logged_in and client_email:
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
    else:
        st.info("Para ver planos detallados, ficha técnica completa, archivos 3D y realidad virtual, regístrate como cliente.")
        
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
                direccion = st.text_input("Dirección", placeholder="Calle, Ciudad, Provincia")

            submitted = st.form_submit_button("🚀 Registrarme y Acceder", type="primary", width='stretch')

            if submitted:
                # Validaciones básicas
                if not nombre or not apellidos or not email:
                    st.error("Por favor completa nombre, apellidos y email")
                elif email != confirmar_email:
                    st.error("Los emails no coinciden")
                elif "@" not in email:
                    st.error("Por favor introduce un email válido")
                else:
                    # Registrar usuario en base de datos
                    try:
                        conn = db.get_conn()
                        cursor = conn.cursor()

                        # Verificar si el email ya existe
                        cursor.execute("SELECT id FROM clients WHERE email = ?", (email,))
                        existing = cursor.fetchone()

                        if existing:
                            st.success("✅ Ya estabas registrado. Accediendo al portal...")
                        else:
                            # Insertar nuevo cliente (combinar nombre y apellidos)
                            full_name = f"{nombre} {apellidos}".strip()
                            cursor.execute("""
                                INSERT INTO clients (name, email, phone, address, created_at)
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

                        # Auto-login
                        st.session_state["client_logged_in"] = True
                        st.session_state["client_email"] = email
                        st.session_state["user_role"] = "buyer"
                        st.session_state["has_transactions"] = False
                        st.session_state["has_properties"] = False

                        # ═══════════════════════════════════════════════════════════════
                        # NAVEGAR AL PANEL DE COMPRA CON PROYECTO SELECCIONADO
                        # ═══════════════════════════════════════════════════════════════
                        st.query_params.update({
                            "page": "🛒 Comprar Proyecto",
                            "selected_project": project_id
                        })
                        
                        # Pequeña pausa visual antes de recargar
                        import time
                        time.sleep(0.5)
                        
                        st.rerun()

                    except Exception as e:
                        st.error(f"Error en el registro: {e}")

        st.markdown("---")
        st.info("💡 **¿Ya tienes cuenta?** Si has realizado compras anteriores, usa tu email para acceder directamente.")

    # Botón volver
    if st.button("← Volver al Inicio"):
        st.query_params.clear()
        st.rerun()


def get_project_by_id(project_id: str) -> dict:
    """Obtiene los datos básicos de un proyecto por su ID"""
    try:
        conn = db.get_conn()
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
        conn.close()

        if not row:
            return None

        # Retornar datos básicos del proyecto
        return {
            'id': row[0],
            'nombre': row[1],
            'descripcion': row[2],
            'total_m2': row[3] or row[4],  # Usar m2_construidos o area_m2
            'coste_estimado': row[6] or 0,  # estimated_cost
            'imagen_principal': row[10],  # foto_principal
            'tipo_propiedad': row[9],  # property_type
            'precio': row[5] or 0,  # price
        }
    except Exception as e:
        print(f"Error obteniendo proyecto {project_id}: {e}")
        return None