from dotenv import load_dotenv
load_dotenv()

# Configurar página con layout amplio
import streamlit as st
st.set_page_config(layout='wide')

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

# Detectar si hay una finca seleccionada en los parámetros de consulta
params = st.query_params

# Detectar navegación al panel de cliente desde project_detail
if st.session_state.get("navigate_to_client_panel"):
    # Limpiar el flag de navegación
    del st.session_state["navigate_to_client_panel"]
    # Usar el mismo mecanismo que el botón "Acceso Clientes" en HOME
    st.query_params["page"] = "👤 Panel de Cliente"
    # Si hay proyecto seleccionado, mantenerlo en query_params
    if "selected_project_for_panel" in st.session_state:
        if "selected_project" in st.query_params:
            del st.query_params["selected_project"]
        del st.session_state["selected_project_for_panel"]
    st.rerun()

# Detectar página seleccionada por query param
page_from_query = params.get("page")

# Interceptar páginas especiales por query param
if page_from_query == "🛒 Comprar Proyecto":
    try:
        import modules.marketplace.project_purchase_panel as project_purchase_panel
        project_purchase_panel.main()
        st.stop()
    except Exception as e:
        st.error(f"Error mostrando panel de compra: {e}")

if page_from_query == "👤 Panel de Cliente":
    try:
        from modules.marketplace import client_panel_fixed as client_panel
        client_panel.main()
        st.stop()
    except Exception as e:
        st.error(f"Error mostrando panel de cliente: {e}")

if "selected_plot" in params:
    try:
        plot_id = params["selected_plot"]
        from modules.marketplace.plot_detail import show_plot_detail_page
        show_plot_detail_page(plot_id)
        st.stop()  # Detener la ejecución para no mostrar el resto de la app
    except Exception as e:
        st.error(f"Error mostrando detalles de la finca: {e}")

# Routing de selected_project desactivado: las fichas se sirven ahora desde project_app.py (puerto 8502).

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
PAGES = {
    "Home":  ("modules.marketplace.marketplace", "main"),
    "Propietarios (Subir Fincas)": ("modules.marketplace.owners", "main"),
    "Arquitectos (Marketplace)": ("modules.marketplace.marketplace_upload", "main"),
    "Intranet": ("modules.marketplace.intranet", "main"),
    "Fincas Guardadas": ("modules.marketplace.plots_table", "main"),
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


# TODO: render_portal_cliente_proyecto desactivado temporalmente para evitar duplicados de ficha.
def render_portal_cliente_proyecto():
    pass


# Navigation state handling (restore `page` variable)
page_keys = list(PAGES.keys())
default_page = page_from_query or st.session_state.get("auto_select_page", "Home")
selected_page = st.session_state.get("selected_page", default_page)
try:
    index = page_keys.index(selected_page) if selected_page in page_keys else 0
except Exception:
    index = 0
page = st.sidebar.radio("Navegación", page_keys, index=index, key="main_navigation")

# Inicializar vista_actual si no existe (no altera comportamiento por defecto)
if "vista_actual" not in st.session_state:
    st.session_state["vista_actual"] = None

# Añadir botón aditivo en el sidebar para abrir el Portal Cliente (no conectado por defecto)
if st.sidebar.button("📂 Portal Cliente"):
    st.query_params["page"] = "👤 Panel de Cliente"
    st.rerun()



# Only handle Home here; other pages delegate to modules
if selected_page == "Home":
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
                                st.rerun()
                else:
                    with st.expander("Acceso"):
                        login_val = st.text_input("Email o Clave", key="login_input_no_modal")
                        if st.button("Entrar", key="login_submit_no_modal"):
                            val = st.session_state.get("login_input_no_modal", "")
                            if val == "admin123":
                                st.success("Acceso admin aceptado")
                                st.session_state['selected_page'] = "Intranet"
                                st.rerun()

# ========== HOME: LANDING + MARKETPLACE + PROYECTOS ==========

    # PASO 1: Renderizar los 3 botones de roles
    st.markdown("---")
    st.markdown('<div class="role-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="role-card">
            <div class="card-icon">🏗️</div>
            <div class="card-title">Tengo un Terreno</div>
            <div class="card-text">Publica tu finca y recibe propuestas reales de arquitectos.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acceso Propietarios", key="btn_prop_home"):
            st.query_params["page"] = "Propietarios (Subir Fincas)"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="role-card">
            <div class="card-icon">📐</div>
            <div class="card-title">Soy Arquitecto</div>
            <div class="card-text">Sube tus proyectos ejecutables y conecta con clientes reales.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acceso Arquitectos", key="btn_arq_home"):
            st.query_params["page"] = "Arquitectos (Marketplace)"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="role-card">
            <div class="card-icon">🏡</div>
            <div class="card-title">Busco Casa</div>
            <div class="card-text">Explora fincas, proyectos compatibles o diseña tu casa con IA.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acceso Clientes", key="btn_cli_home"):
            st.query_params["page"] = "👤 Panel de Cliente"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

    # PASO 2: Renderizar MARKETPLACE (miniaturas + mapa)
    try:
        from modules.marketplace import marketplace
        marketplace.main()
    except Exception as e:
        import traceback
        st.error(f"❌ Error cargando marketplace:  {e}")
        st.code(traceback.format_exc())

    # PASO 3: Renderizar PROYECTOS ARQUITECTÓNICOS
    st.markdown("---")
    st.header("🏗️ Proyectos Arquitectónicos Disponibles")

    try:
        from src import db
        projects = db.get_featured_projects(limit=6)
        
        if projects: 
            cols = st.columns(3)
            for idx, p in enumerate(projects):
                with cols[idx % 3]:
                    # Usar la misma lógica que en plot_detail.py para obtener imágenes válidas
                    from modules.marketplace.plot_detail import get_project_images
                    
                    # Convertir el formato del proyecto para que sea compatible con get_project_images
                    proyecto_compat = {
                        'foto_principal': p.get('files', {}).get('fotos', [])[0] if p.get('files', {}).get('fotos') else None,
                        'galeria_fotos': p.get('files', {}).get('fotos', [])[1:] if p.get('files', {}).get('fotos') else []
                    }
                    
                    project_images = get_project_images(proyecto_compat)
                    thumbnail = project_images[0] if project_images else "assets/fincas/image1.jpg"
                    
                    st.image(thumbnail, width=250)
                    st.subheader(p.get('title', 'Proyecto'))
                    st.write(f"**€{p.get('price', 0):,.0f}** | {p.get('area_m2', 0)} m²")
                    project_url = f"http://localhost:8502/?project_id={p['id']}"
                    st.markdown(
                        f'<a href="{project_url}" target="_blank">'
                        f'<button style="width:100%; padding:8px 12px;">Ver Detalles</button>'
                        f'</a>',
                        unsafe_allow_html=True
                    )
        else:
            st.info("No hay proyectos arquitectónicos disponibles aún.")
    except Exception as e:
        st.error(f"Error cargando proyectos: {e}")

    

elif selected_page == "Propietario (Gemelo Digital)":
    with st.container():
        # Flujo principal: Propietario sube finca → IA genera plan
        from modules.marketplace import gemelo_digital
        gemelo_digital.main()

elif selected_page == "Propietarios (Subir Fincas)":
    with st.container():
        # Propietarios suben fincas al marketplace inmobiliario
        from modules.marketplace import owners
        owners.main()

elif selected_page == "Diseñador de Vivienda":
    with st.container():
        # Flujo secundario: Cliente diseña vivienda personalizada
        from modules.marketplace import disenador_vivienda
        disenador_vivienda.main()

# "Inmobiliaria (Mapa)" route removed — Home now uses `marketplace.main()` directly.

elif selected_page == "👤 Panel de Cliente":
    with st.container():
        # Panel de cliente con acceso a transacciones y servicios
        from modules.marketplace import client_panel_fixed as client_panel
        client_panel.main()

elif selected_page == "Arquitectos (Marketplace)":
    with st.container():
        # Use the new main() entrypoint which handles auth, plans and upload flow
        from modules.marketplace import marketplace_upload
        marketplace_upload.main()

elif selected_page == "Intranet":
    with st.container():
        from modules.marketplace import intranet
        intranet.main()
