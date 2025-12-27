import streamlit as st
import sqlite3
import pandas as pd
import os
import threading
import http.server
import socketserver
import functools
import time
from pathlib import Path
from src import db as _db
@st.cache_resource
def three_html_for(url_3d: str, project_id: str = "") -> str:
    three_html = """
<!doctype html>
<html>
    <head>
        <meta charset="utf-8" />
        <style>body { margin: 0; overflow: hidden; background: #f0f0f0; }</style>
    </head>
    <body>
        <div id="container" style="width:100%;height:600px;"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/js/loaders/OBJLoader.js"></script>
        <script src="https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/js/controls/OrbitControls.js"></script>
        <script>
            (function(){
                const container = document.getElementById('container');
                const scene = new THREE.Scene();
                scene.background = new THREE.Color(0xf0f0f0);
                
                const camera = new THREE.PerspectiveCamera(45, window.innerWidth / 600, 0.1, 20000);
                const renderer = new THREE.WebGLRenderer({antialias:true});
                renderer.setSize(window.innerWidth, 600);
                container.appendChild(renderer.domElement);

                const controls = new THREE.OrbitControls(camera, renderer.domElement);
                const ambient = new THREE.AmbientLight(0xffffff, 0.7); // Luz ambiental suave
                scene.add(ambient);

                const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 0.8); // Luz de cielo y suelo
                hemiLight.position.set(0, 20, 0);
                scene.add(hemiLight);

                const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
                dirLight.position.set(100, 100, 50);
                scene.add(dirLight);

                const loader = new THREE.OBJLoader();
                loader.load('""" + url_3d + """', function(obj){
                    // Escalado leve del modelo para hacerlo más visible (factor 1.5)
                    if(obj && obj.scale){ obj.scale.multiplyScalar(1.5); }
                    const box = new THREE.Box3().setFromObject(obj);
                    const center = box.getCenter(new THREE.Vector3());
                    const size = box.getSize(new THREE.Vector3());
                    obj.position.sub(center);

                    // Ajuste de cámara: 1.5 para que se vea más grande
                    const maxDim = Math.max(size.x, size.y, size.z);
                    const cameraZ = maxDim / 2 / Math.tan(Math.PI * camera.fov / 360) * 1.5;
                    camera.position.set(cameraZ, cameraZ, cameraZ);
                    camera.lookAt(0,0,0);

                    obj.traverse(function(child){
                        if(child.isMesh){
                            // Material Gris con bordes visibles para que no sea "todo blanco"
                            child.material = new THREE.MeshStandardMaterial({
                                color: 0xdddddd,
                                side: THREE.DoubleSide
                            });
                            const edges = new THREE.EdgesGeometry(child.geometry);
                            const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x888888 }));
                            child.add(line);
                        }
                    });
                    scene.add(obj);
                });

                function animate(){ requestAnimationFrame(animate); controls.update(); renderer.render(scene, camera); }
                animate();
                window.onresize = function(){ renderer.setSize(window.innerWidth, 600); };
            })();
        </script>
    </body>
</html>
"""
    return three_html

# Page configuration and navigation
# Ensure wide layout so projects don't overlap
st.set_page_config(layout='wide')
PAGES = {
    "Home": ("modules.marketplace.marketplace", "main"),
    "Propietario (Gemelo Digital)": ("modules.marketplace.gemelo_digital", "main"),
    "Propietarios (Subir Fincas)": ("modules.marketplace.owners", "main"),
    "Diseñador de Vivienda": ("modules.marketplace.disenador_vivienda", "main"),
    "Arquitectos (Marketplace)": ("modules.marketplace.marketplace_upload", None),
    "Intranet": ("modules.marketplace.intranet", "main"),
}


# Helper: start a simple static server for local assets (with CORS)
def _start_static_server(root_dir: Path, port: int = 8765):
    # If already started, return existing port
    if st.session_state.get("static_server_started"):
        return st.session_state.get("static_server_port")
    try:
        class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', '*')
                super().end_headers()
            def do_OPTIONS(self):
                self.send_response(200, "OK")
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', '*')
                self.end_headers()

        Handler = functools.partial(CORSRequestHandler, directory=str(root_dir))
        httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler)
    except Exception:
        return None
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    st.session_state["static_server_started"] = True
    st.session_state["static_server_port"] = port
    st.session_state["static_server_obj"] = httpd
    return port


def render_portal_cliente_proyecto():
    st.header("📂 Portal de Cliente — Proyecto Seleccionado")

    proyecto = st.session_state.get("proyecto_seleccionado")
    interes_id = st.session_state.get("interes_proyecto_id")
    interes_titulo = st.session_state.get("interes_proyecto_titulo")
    email = st.session_state.get("email", "")
    rol = st.session_state.get("rol", "cliente")  # futuro: cliente / propietario / arquitecto / admin

    if not proyecto and not interes_id:
        st.warning("No hay ningún proyecto seleccionado para mostrar en el portal de cliente.")
        return

    st.markdown("### 🏡 Información del Proyecto")

    if proyecto:
        st.write(f"**Título:** {proyecto.get('title', 'N/D')}")
        st.write(f"**💰 Precio:** {proyecto.get('price', 'N/D')} €")
        st.write(f"**📐 Superficie:** {proyecto.get('m2_construidos', 'N/D')} m²")
        st.write(f"**🛏️ Habitaciones:** {proyecto.get('habitaciones', 'N/D')}")
        st.write(f"**🛁 Baños:** {proyecto.get('banos', 'N/D')}")
        st.write(f"**🏠 Plantas:** {proyecto.get('plantas', 'N/D')}")
    else:
        st.warning("No hay proyecto seleccionado.")

    st.markdown("---")

    # VISUALIZACIONES (pestañas: 3D / VR / Fotos)
    st.markdown("### 🏗️ Visualizaciones del Proyecto")

    tab_3d, tab_vr, tab_fotos = st.tabs(["🎥 3D", "🥽 VR", "🖼️ Fotos / Planos"])

    # --- Pestaña 3D ---
    with tab_3d:
        st.markdown("#### 🎥 Visor 3D del Proyecto")

        if proyecto:
            # Usamos GLB siempre que exista
            glb_path = proyecto.get("modelo_3d_glb")

            if glb_path:
                rel_path = str(glb_path).replace("\\", "/").lstrip("/")
                # Obtener STATIC_URL si está definido, si no usar fallback
                STATIC_URL = globals().get('STATIC_URL', 'http://127.0.0.1:8765/')
                model_url = f"{STATIC_URL}{rel_path}".replace(" ", "%20")

                try:
                    html_final = three_html_for(model_url, str(proyecto.get("id")))
                    st.components.v1.html(html_final, height=700, scrolling=False)
                except Exception as e:
                    st.error(f"Error cargando visor 3D: {e}")
            else:
                st.info("Este proyecto no tiene modelo GLB. Próximamente convertiremos OBJ a GLB automáticamente.")
        else:
            st.warning("No hay proyecto seleccionado en el portal.")

    # --- Pestaña VR ---
    with tab_vr:
        st.markdown("#### 🥽 Visor de Realidad Virtual")

        model_glb = None
        if proyecto and proyecto.get("modelo_3d_glb"):
            model_glb = proyecto.get("modelo_3d_glb")

        if model_glb:
            rel = str(model_glb).replace("\\", "/").lstrip("/")
            glb_url = f"{globals().get('STATIC_URL','http://127.0.0.1:8765/')}{rel}".replace(" ", "%20")
            viewer_url = f"{globals().get('STATIC_URL','http://127.0.0.1:8765/')}static/vr_viewer.html?model={glb_url}"

            st.markdown(
                f'<a href="{viewer_url}" target="_blank">'
                f'<button style="padding:10px 16px;border-radius:6px;background:#0b5cff;color:#fff;border:none;">'
                f"Abrir experiencia RV en nueva pestaña"
                f"</button></a>",
                unsafe_allow_html=True,
            )
            st.caption("Se abrirá el visor RV en una nueva pestaña. Requiere navegador con WebXR o modo Desktop para previsualizar.")
        else:
            st.info("Este proyecto todavía no tiene modelo VR asociado. Usaremos el modelo 3D como base en futuras versiones.")

    # --- Pestaña Fotos / Planos ---
    with tab_fotos:
        st.markdown("#### 🖼️ Galería de Fotos y Planos")

        # Foto principal
        foto = proyecto.get("foto_principal")
        if foto:
            rel = foto.replace("\\", "/").lstrip("/")
            url = f"{globals().get('STATIC_URL','http://127.0.0.1:8765/')}{rel}"
            st.image(url, use_column_width=True)

        # Imagen adicional dentro de characteristics_json
        try:
            import json
            chars = json.loads(proyecto.get("characteristics_json", "{}"))
            img2 = chars.get("imagenes")
            # Evitar duplicados
            if img2 and img2 == foto:
                img2 = None
            if img2:
                rel2 = img2.replace("\\", "/").lstrip("/")
                url2 = f"{globals().get('STATIC_URL','http://127.0.0.1:8765/')}{rel2}"
                st.image(url2, use_column_width=True)
        except:
            pass

    st.markdown("---")
    st.markdown("### 🛒 Acciones del Cliente")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛒 COMPRAR ESTE PROYECTO (simulado)", key="btn_comprar_proyecto_portal"):
            st.success("Simulando compra. Nuestro equipo comercial se pondrá en contacto contigo.")
    with col2:
        if st.button("📞 QUIERO QUE ME LLAMEN", key="btn_llamar_proyecto_portal"):
            st.success("Hemos registrado tu interés para que te llame el equipo comercial.")

    st.caption(f"Portal vinculado al email: {email or 'No registrado'}")

    st.markdown("---")
    st.markdown("### 🔧 Módulos Profesionales (Futuro)")
    st.info("Estos módulos estarán disponibles en futuras versiones para monetización:")
    st.write("- 🎨 Decoradores (packs de interiorismo)")
    st.write("- 🏗️ Constructores (presupuestos automáticos)")
    st.write("- 🧱 Prefabricadas (catálogo integrado)")
    st.write("- 🛡️ Aseguradoras (pólizas vinculadas)")
    st.write("- 🧰 Materiales de construcción (marketplace)")
    st.write("- 🧑‍💼 Arquitectos (gestión avanzada)")
    st.write("- 🧑‍💼 Propietarios (seguimiento de obra)")


# Navigation state handling (restore `page` variable)
page_keys = list(PAGES.keys())
default_page = st.session_state.get("auto_select_page", "Home")
selected_page = st.session_state.get("selected_page", default_page)
try:
    index = page_keys.index(selected_page) if selected_page in page_keys else 0
except Exception:
    index = 0
page = st.sidebar.radio("Navegación", page_keys, index=index)

# Inicializar vista_actual si no existe (no altera comportamiento por defecto)
if "vista_actual" not in st.session_state:
    st.session_state["vista_actual"] = None

# Añadir botón aditivo en el sidebar para abrir el Portal Cliente (no conectado por defecto)
if st.sidebar.button("📂 Portal Cliente"):
    st.session_state["vista_actual"] = "portal_cliente"

# Si el usuario ha seleccionado explícitamente el Portal Cliente, mostrarlo y detener el flujo
if st.session_state.get("vista_actual") == "portal_cliente":
    try:
        render_portal_cliente_proyecto()
    except Exception as _e:
        st.error("Error mostrando el Portal Cliente: " + str(_e))
    st.stop()



# Only handle Home here; other pages delegate to modules
if page == "Home":
    STATIC_ROOT = Path(r"C:/ARCHIRAPID_PROYECT25")
    STATIC_PORT = _start_static_server(STATIC_ROOT, port=8765)
    # URL base del servidor estático (definida temprano para usar en el header de diagnóstico)
    if STATIC_PORT:
        STATIC_URL = f"http://127.0.0.1:{STATIC_PORT}/"
    else:
        STATIC_URL = "http://127.0.0.1:8765/"

    # Header
    with st.container():
        try:
            from components.header import render_header
            cols = render_header()
            access_col = cols[2]
        except Exception:
            cols = st.columns([1, 4, 1])
            with cols[0]:
                try:
                    st.image("assets/branding/logo.png", width=140)
                except Exception:
                    st.markdown("# 🏗️ ARCHIRAPID")
            with cols[1]:
                st.markdown("### IA Avanzada + Precios en Vivo + Exportación Profesional")
            access_col = cols[2]

        with access_col:
            if st.button("ACCESO"):
                if hasattr(st, 'modal'):
                    with st.modal("Acceso"):
                        login_val = st.text_input("Email o Clave", key="login_input")
                        if st.button("Entrar", key="login_submit"):
                            val = st.session_state.get("login_input", "")
                            if val == "admin123":
                                st.success("Acceso admin aceptado")
                                st.session_state['selected_page'] = "Intranet"
                                st.experimental_rerun()
                else:
                    with st.expander("Acceso"):
                        login_val = st.text_input("Email o Clave", key="login_input_no_modal")
                        if st.button("Entrar", key="login_submit_no_modal"):
                            val = st.session_state.get("login_input_no_modal", "")
                            if val == "admin123":
                                st.success("Acceso admin aceptado")
                                st.session_state['selected_page'] = "Intranet"
                                st.experimental_rerun()

    if 'role' not in st.session_state:
        from components.landing import render_landing
        render_landing()
    else:
        # Top-level title and visible version banner for verification
        st.title("ARCHIRAPID")
    try:
        st.warning(f"Versión de la App: 1.0.3 - 3D Integrado - {pd.Timestamp.now()}")
    except Exception:
        # Fallback in case pd.Timestamp isn't available for some reason
        st.warning("Versión de la App: 1.0.3 - 3D Integrado")

    # (Botón de prueba RV global eliminado por petición del usuario)

    st.markdown("---")

    # BUSCADOR + MAPA
    st.header("Buscar Fincas")
    try:
        from src import db
        from src import map_manager
    except Exception:
        st.error("Error cargando módulos de base de datos o mapa")
        db = None
        map_manager = None

    province_options = []
    if db:
        try:
            province_options = db.get_all_provinces()
        except Exception:
            province_options = []

    province = st.selectbox("Provincia", options=["Todas"] + province_options, index=0)
    query = st.text_input("Localidad o dirección", value="")

    filter_province = None if province == "Todas" else province
    try:
        from modules.marketplace import marketplace
        marketplace.main()
    except Exception:
        if map_manager:
            map_manager.mostrar_plots_on_map(province=filter_province, query=query, width=1100, height=650)
        else:
            st.info("Mapa no disponible (módulos faltantes)")

    st.markdown("---")
    st.header("Proyectos destacados")

    # 1. Obtención de datos
    projects = []
    try:
        if db:
            projects = db.get_featured_projects(limit=3)
    except Exception:
        projects = []

    import json
    # Creamos las columnas para las fichas
    cols = st.columns(3)
    project_to_show_3d = None  # Variable para saber qué proyecto expandir al ancho total

    for idx, p in enumerate(projects[:3]):
        with cols[idx]:
            try:
                raw = json.loads(p.get('characteristics_json') or '{}')
                data = raw.get('characteristics', raw) if isinstance(raw, dict) else {}
            except Exception:
                data = {}

            img = p.get('foto_principal') or data.get('imagenes') or "https://via.placeholder.com/640x360?text=No+Image"
            st.image(img, use_column_width=True)
            
            title = p.get('title') or p.get('titulo') or 'Proyecto Archi'
            st.subheader(title)

            # Checkbox para activar 3D (Solo uno a la vez se guardará en el estado)
            if st.checkbox("🏗️ Abrir Visor 3D", key=f"cb_3d_{p.get('id')}"):
                project_to_show_3d = p  # Marcamos este proyecto para mostrarlo abajo

            with st.expander("📄 Ficha Técnica Completa"):
                # Mostramos los datos clave de forma elegante
                st.markdown(f"### {title}")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"💰 **Precio:** {p.get('price') or 'Consultar'}")
                    st.write(f"📐 **Superficie:** {p.get('area_m2', '—')} m²")
                    st.write(f"🛏️ **Habitaciones:** {data.get('habitaciones', '—')}")
                with c2:
                    st.write(f"🛁 **Baños:** {data.get('baños', data.get('banos', '—'))}")
                    st.write(f"🏢 **Plantas:** {data.get('plantas', '—')}")
                    st.write(f"🅿️ **Garaje:** {'Sí' if data.get('garaje') else 'No'}")
                # Si hay extras o descripción, los añadimos (seguros ante datos faltantes o no-lista)
                if data.get('extras'):
                    extras = data.get('extras')
                    if isinstance(extras, list):
                        texto_extras = ", ".join(extras)
                    else:
                        texto_extras = str(extras)
                    st.info(f"✨ **Detalles adicionales:** {texto_extras}")
                if p.get('description'):
                    st.write(f"📝 {p.get('description')}")

    # --- EL VISOR 3D AHORA SE RENDERIZA AQUÍ (ANCHO COMPLETO) ---
    # Determine STATIC_URL for asset links (avoid NameError if server returned None)
    if STATIC_PORT:
        STATIC_URL = f"http://127.0.0.1:{STATIC_PORT}/"
    else:
        STATIC_URL = "http://127.0.0.1:8765/"

    if project_to_show_3d:
        st.markdown("---")
        st.subheader(f"🌐 Visor Interactivo: {project_to_show_3d.get('title')}")
        # DEBUG: mostrar contenido completo del proyecto antes de renderizar el visor 3D
        try:
            st.write(project_to_show_3d)
        except Exception:
            pass
        
        # Obtener URL del modelo
        modelo_path = project_to_show_3d.get('modelo_3d_path')
        if modelo_path:
            # Saneamiento de ruta para Windows/URL
            rel_path = modelo_path.replace("\\", "/").lstrip("/")
            model_url = f"{STATIC_URL}{rel_path}".replace(" ", "%20")

            # Llamada a la función con el fix de auto-zoom
            html_final = three_html_for(model_url, str(project_to_show_3d.get('id')))

            # Usamos st.components al ancho total
            st.components.v1.html(html_final, height=700, scrolling=False)
            # --- VR Viewer (aditivo, seguro) ---
            st.markdown("### 🥽 Visor de Realidad Virtual")

            # Intentar llamar a cualquier renderer VR conocido en el repo; si no hay ninguno, ofrecer fallback GLB
            renderer_called = False
            try:
                for name in ('render_vr_viewer', 'visor_vr', 'render_vr_experience'):
                    fn = globals().get(name)
                    if callable(fn):
                        try:
                            fn(project_to_show_3d)
                            renderer_called = True
                            break
                        except Exception as e:
                            st.warning(f'VR renderer {name} raised an error: {e}')
            except Exception as e:
                st.warning(f'Error while attempting to initialize VR renderers: {e}')

            # Si ningún renderer fue invocado, ofrecemos un enlace al visor GLB o un botón de prueba
            if not renderer_called:
                model_glb = project_to_show_3d.get('modelo_3d_glb') or None
                if not model_glb and project_to_show_3d.get('modelo_3d_path'):
                    modelo_path = project_to_show_3d.get('modelo_3d_path')
                    if str(modelo_path).lower().endswith('.glb'):
                        model_glb = modelo_path

                if model_glb:
                    rel = str(model_glb).replace('\\','/').lstrip('/')
                    glb_url = f"{STATIC_URL}{rel}".replace(' ', '%20')
                    viewer_url = f"{STATIC_URL}static/vr_viewer.html?model={glb_url}"
                    with st.container():
                        st.markdown(f'<a href="{viewer_url}" target="_blank"><button style="padding:10px 16px;border-radius:6px;background:#0b5cff;color:#fff;border:none;">Abrir experiencia RV</button></a>', unsafe_allow_html=True)
                        st.caption('Se abrirá el visor RV en una nueva pestaña. Requiere navegador con WebXR o modo Desktop para previsualizar.')
                else:
                    # Mostrar botón de prueba con un modelo GLB público para validar el flujo
                    test_glb = "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Duck/glTF-Binary/Duck.glb"
                    test_viewer = f"{STATIC_URL}static/vr_viewer.html?model={test_glb}"
                    with st.container():
                        st.markdown(f'<a href="{test_viewer}" target="_blank"><button style="padding:8px 12px;border-radius:6px;background:#28a745;color:#fff;border:none;">Probar RV (modelo de ejemplo)</button></a>', unsafe_allow_html=True)
                        st.caption('Botón de prueba: abre un modelo público para validar el visor VR. No modifica datos del proyecto.')

            # --- Bloque aditivo: Me gusta / Lo quiero (100% aditivo, no rompe nada) ---
            st.markdown("---")
            st.markdown("### ❤️ ¿Te gusta este proyecto?")

            email = st.session_state.get("email", "")
            proyecto_id = project_to_show_3d.get("id")
            proyecto_titulo = project_to_show_3d.get("titulo", "Proyecto sin título")

            if not email:
                st.info("Para guardar este proyecto en tu espacio de cliente, introduce tu email:")
                email_input = st.text_input("Tu email", key=f"email_interes_{proyecto_id}")

                if st.button("✅ Guardar este proyecto y continuar", key=f"btn_guardar_proyecto_email_{proyecto_id}"):
                    if email_input:
                        st.session_state["email"] = email_input
                        st.session_state["interes_proyecto_id"] = proyecto_id
                        st.session_state["interes_proyecto_titulo"] = proyecto_titulo
                        # Guardar el objeto de proyecto completo para que el Portal Cliente lo reciba
                        st.session_state["proyecto_seleccionado"] = project_to_show_3d
                        st.success("Proyecto guardado. Nuestro equipo comercial podrá contactarte si lo deseas.")
                        # Navegar automáticamente al Portal Cliente después de guardar interés
                        st.session_state["vista_actual"] = "portal_cliente"
                        st.experimental_rerun()
                    else:
                        st.warning("Por favor, introduce un email válido.")
            else:
                st.success(f"Estás navegando como: {email}")
                if st.button("💾 Me gusta este proyecto (guardarlo)", key=f"btn_me_gusta_proyecto_{proyecto_id}"):
                    st.session_state["interes_proyecto_id"] = proyecto_id
                    st.session_state["interes_proyecto_titulo"] = proyecto_titulo
                    # Guardar el objeto de proyecto completo para que el Portal Cliente lo reciba
                    st.session_state["proyecto_seleccionado"] = project_to_show_3d
                    st.success("✅ Hemos guardado tu interés por este proyecto.")
                    # Cambiar automáticamente a la vista Portal Cliente
                    st.session_state["vista_actual"] = "portal_cliente"
                    st.experimental_rerun()
        else:
            st.error("Este proyecto no tiene un archivo 3D vinculado.")

    

elif page == "Propietario (Gemelo Digital)":
    with st.container():
        # Flujo principal: Propietario sube finca → IA genera plan
        from modules.marketplace import gemelo_digital
        gemelo_digital.main()

elif page == "Propietarios (Subir Fincas)":
    with st.container():
        # Propietarios suben fincas al marketplace inmobiliario
        from modules.marketplace import owners
        owners.main()

elif page == "Diseñador de Vivienda":
    with st.container():
        # Flujo secundario: Cliente diseña vivienda personalizada
        from modules.marketplace import disenador_vivienda
        disenador_vivienda.main()

# "Inmobiliaria (Mapa)" route removed — Home now uses `marketplace.main()` directly.

elif page == "👤 Panel de Cliente":
    with st.container():
        # Panel de cliente con acceso a transacciones y servicios
        from modules.marketplace import client_panel_fixed as client_panel
        client_panel.main()

elif page == "Arquitectos (Marketplace)":
    with st.container():
        # Use the new main() entrypoint which handles auth, plans and upload flow
        from modules.marketplace import marketplace_upload
        marketplace_upload.main()

elif page == "Intranet":
    with st.container():
        from modules.marketplace import intranet
        intranet.main()
