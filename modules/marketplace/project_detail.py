# modules/marketplace/project_detail.py
"""
Página de detalles de proyecto arquitectónico
Vista previa básica para usuarios no registrados
"""

import streamlit as st
import json
from modules.marketplace.plot_detail import get_project_images
from src import db

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
    project_images = get_project_images({
        'foto_principal': project_data['foto_principal'],
        'galeria_fotos': gallery
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

    if st.button("Generar Resumen Completo del Proyecto con IA", key="btn_ia_summary"):
        if project_data.get("memoria_pdf"):
            try:
                import PyPDF2
                with open(project_data["memoria_pdf"], "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages[:10]:  # Más páginas para usuarios logueados
                        text += page.extract_text() + "\n"

                if text.strip():
                    # Prompt más detallado pero protegido para usuarios logueados
                    prompt = f"""Analiza este proyecto arquitectónico y proporciona un resumen completo y detallado en español.

                    INCLUIR:
                    - Estilo arquitectónico y filosofía de diseño
                    - Distribución general de espacios y ambientes
                    - Materiales y acabados utilizados
                    - Aspectos estéticos y de iluminación
                    - Características sostenibles y eficiencia energética
                    - Elementos innovadores o diferenciadores
                    - Contexto y emplazamiento recomendado

                    EXCLUIR COMPLETAMENTE:
                    - Dimensiones exactas, medidas o proporciones específicas
                    - Datos constructivos técnicos detallados
                    - Información que permita replicar o copiar el proyecto
                    - Detalles de estructura o cimentación
                    - Especificaciones técnicas de instalaciones

                    Sé informativo pero protege la propiedad intelectual del proyecto.

                    Texto del proyecto:
                    {text[:4000]}"""

                    from modules.marketplace import ai_engine_groq as ai
                    summary = ai.generate_text(prompt)

                    if "Error:" in summary:
                        st.error(summary)
                    else:
                        st.success("✅ Resumen completo generado por IA:")
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

                # HTML con Three.js para visor 3D
                three_html = f"""
                <div id="container3d" style="width: 100%; height: 700px; border: 1px solid #ccc;"></div>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
                <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
                <script>
                    // Inicializar escena, cámara y renderer
                    const scene = new THREE.Scene();
                    scene.background = new THREE.Color(0xf0f0f0);

                    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                    camera.position.set(5, 5, 5);

                    const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                    renderer.setSize(document.getElementById('container3d').clientWidth, 700);
                    renderer.shadowMap.enabled = true;
                    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
                    document.getElementById('container3d').appendChild(renderer.domElement);

                    // Controles de órbita
                    const controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.enableDamping = true;
                    controls.dampingFactor = 0.05;

                    // Luces
                    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
                    scene.add(ambientLight);

                    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
                    directionalLight.position.set(10, 10, 5);
                    directionalLight.castShadow = true;
                    scene.add(directionalLight);

                    // Cargar modelo GLTF
                    const loader = new THREE.GLTFLoader();
                    loader.load(
                        '{model_url}',
                        function (gltf) {{
                            const model = gltf.scene;
                            scene.add(model);

                            // Calcular bounding box para centrar la cámara
                            const box = new THREE.Box3().setFromObject(model);
                            const center = box.getCenter(new THREE.Vector3());
                            const size = box.getSize(new THREE.Vector3());

                            // Centrar modelo en origen
                            model.position.sub(center);

                            // Ajustar cámara para ver todo el modelo
                            const maxDim = Math.max(size.x, size.y, size.z);
                            const fov = camera.fov * (Math.PI / 180);
                            let cameraZ = Math.abs(maxDim / Math.sin(fov / 2));

                            camera.position.set(center.x, center.y, center.z + cameraZ * 1.5);
                            camera.lookAt(center);

                            controls.target.copy(center);
                            controls.update();

                            // Habilitar sombras si el modelo las soporta
                            model.traverse(function (child) {{
                                if (child.isMesh) {{
                                    child.castShadow = true;
                                    child.receiveShadow = true;
                                }}
                            }});
                        }},
                        function (xhr) {{
                            console.log((xhr.loaded / xhr.total * 100) + '% loaded');
                        }},
                        function (error) {{
                            console.error('Error loading GLTF:', error);
                            alert('Error cargando el modelo 3D. Verifica que el archivo exista.');
                        }}
                    );

                    // Función de animación
                    function animate() {{
                        requestAnimationFrame(animate);
                        controls.update();
                        renderer.render(scene, camera);
                    }}
                    animate();

                    // Ajustar tamaño al cambiar ventana
                    window.addEventListener('resize', function() {{
                        camera.aspect = document.getElementById('container3d').clientWidth / 700;
                        camera.updateProjectionMatrix();
                        renderer.setSize(document.getElementById('container3d').clientWidth, 700);
                    }});
                </script>
                """

                st.components.v1.html(three_html, height=700, scrolling=False)
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
            if gallery:
                st.subheader("Galería Adicional")
                for idx, foto in enumerate(gallery):
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
                        st.session_state["just_registered"] = True  # Flag para saber que acabamos de registrarnos
                        st.session_state["registration_success"] = True  # Flag para mostrar opciones después del formulario

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