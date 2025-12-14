#!/usr/bin/env python3
"""
Panel Cliente Integrado ARCHIRAPID
IA Avanzada + Precios en Vivo + Exportación Profesional
"""

import streamlit as st
import json
import os
import html
from datetime import datetime
import time
import requests
from geopy.geocoders import Nominatim
from streamlit.components.v1 import html as components_html

# ==========================================
# COMPONENTES LOCALES
# ==========================================

def render_header():
    """Header con logo de ARCHIRAPID"""
    col1, col2 = st.columns([1, 3])

    with col1:
        # Logo de ARCHIRAPID
        logo_path = "assets/branding/logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
        else:
            st.title("🏗️ ARCHIRAPID")

    with col2:
        st.markdown("### IA Avanzada + Precios en Vivo + Exportación Profesional")
        st.markdown("*Diseña tu casa ideal con inteligencia artificial*")

    st.markdown("---")

def render_footer():
    """Footer con información de contacto y copyright"""
    st.divider()
    st.caption("© 2025 ARCHIRAPID — Todos los derechos reservados. No se permite la copia o reproducción sin autorización expresa.")
    st.caption("📧 moskovia@me.com | 📱 +34 623 172 704 | 📍 Madrid (Spain)")

# ==========================================
# IMPORTS DEL SISTEMA INTEGRADO
# ==========================================

from design_ops import parametric_engine, calculate_live_price
from export_ops import generate_professional_export, get_export_options
from data_access import (
    obtener_fincas_con_fallback, obtener_proyectos_con_fallback,
    crear_proyecto, actualizar_proyecto, exportar_proyecto,
    mostrar_estado_conexion, inicializar_conexion,
    demo_fincas
)

# ==========================================
# CONFIGURACIÓN DE LA APP
# ==========================================

st.set_page_config(
    page_title="ARCHIRAPID - IA + Precios en Vivo",
    layout="wide",
    page_icon="🏗️"
)

# ==========================================
# FUNCIONES AUXILIARES PARA FINCAS
# ==========================================

def load_fincas():
    """Carga fincas desde backend o demo con manejo robusto de errores"""
    try:
        BACKEND_URL = "http://localhost:8000"
        r = requests.get(f"{BACKEND_URL}/fincas", timeout=5)
        if r.status_code == 200:
            fincas = r.json()
            if not fincas:  # Si backend responde pero no hay fincas, usar demo
                fincas = demo_fincas()
        else:
            fincas = demo_fincas()
    except requests.exceptions.ConnectionError:
        # Backend no está disponible
        st.warning("❌ **Backend no disponible**: El servidor FastAPI no está ejecutándose en http://localhost:8000")
        st.info("💡 **Solución**: Ejecute `uvicorn main:app --host 0.0.0.0 --port 8000` en la carpeta backend")
        st.info("🔄 **Modo demo activado**: Usando datos de ejemplo para demostración")
        fincas = demo_fincas()
    except Exception as e:
        st.error(f"❌ Error inesperado al cargar fincas: {str(e)}")
        fincas = demo_fincas()
    return fincas

def normalize_id(fid):
    """Normaliza ID: acepta str/int y evita None"""
    try:
        return int(fid)
    except Exception:
        return fid  # si viene string ya usable

def get_finca_by_id(fincas, fid):
    if fid is None: return None
    fid_str = str(fid)
    for f in fincas:
        if str(f.get("id")) == fid_str:
            return f
    return None

def get_thumb(finca, placeholder="https://via.placeholder.com/320x240?text=No+Photo"):
    """Return a usable image URL for Streamlit. If the finca has no valid
    image (or uses the local '/static/no-photo.png' placeholder), return
    the external placeholder URL to avoid Streamlit trying to open a
    non-existent local file.
    """
    val = finca.get("foto_url")
    if not val:
        return placeholder

    # If it's a list, prefer the first valid entry
    if isinstance(val, list):
        first = val[0] if len(val) > 0 else None
        if not first or first == "/static/no-photo.png":
            return placeholder
        return first

    # If it's a string
    if isinstance(val, str):
        if val == "/static/no-photo.png":
            return placeholder
        return val

    return placeholder

# Placeholder para imágenes
placeholder = "https://via.placeholder.com/320x240?text=No+Photo"

# Función para convertir URLs relativas a absolutas para Streamlit
def get_image_url(relative_path):
    """Convierte URL relativa a URL absoluta accesible por Streamlit"""
    if relative_path.startswith("/static/"):
        # Para desarrollo local, usar ruta absoluta del sistema de archivos
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, relative_path.lstrip("/"))
        return full_path
    return relative_path

# Función para obtener URL del navegador (para popups)
def get_browser_image_url(relative_path):
    """Convierte URL relativa a URL accesible desde el navegador"""
    if relative_path.startswith("/static/"):
        # Usar data URLs para imágenes pequeñas (base64 encoded)
        import os
        import base64

        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_path = os.path.join(base_dir, relative_path.lstrip("/"))

        if os.path.exists(full_path):
            try:
                with open(full_path, "rb") as f:
                    image_data = f.read()
                    encoded = base64.b64encode(image_data).decode()
                    ext = os.path.splitext(full_path)[1].lower()
                    mime_type = "image/png" if ext == ".png" else "image/jpeg"
                    return f"data:{mime_type};base64,{encoded}"
            except:
                pass

        # Fallback a placeholder externo (evita recursión si no existe el archivo)
        return placeholder

    return relative_path


def inject_history_replace():
    """Inject a small client-side script to remove query params from the URL (history.replaceState).
    This helps avoid leaving query parameters or iframe navigation remnants after closing modals.
    """
    try:
        import streamlit.components.v1 as components
        script = """
        <script>
        (function(){
            try {
                if (window.history && window.history.replaceState) {
                    const base = window.location.protocol + '//' + window.location.host + window.location.pathname;
                    window.history.replaceState({}, document.title, base);
                }
            } catch(e) {
                /* ignore */
            }
        })();
        </script>
        """
        # height 0 ensures minimal footprint
        components.html(script, height=0)
    except Exception:
        pass


def render_small_card(top_modal, finca):
    """Render a compact card in the top placeholder with thumb, brief info and 'Ver más detalles'"""
    if finca is None:
        return
    thumb = get_browser_image_url(get_thumb(finca))
    with top_modal.container():
        cols = st.columns([1, 3, 1])
        with cols[0]:
            try:
                st.image(thumb, width=120)
            except Exception:
                st.image(placeholder, width=120)
        with cols[1]:
            st.markdown(f"**{finca.get('direccion','—')}**")
            st.markdown(f"Superficie: {finca.get('superficie_m2','—')} m2")
            st.markdown(f"PVP: {finca.get('pvp','—')} €")
        with cols[2]:
            if st.button("Ver más detalles", key=f"vermas_{finca.get('id')}"):
                st.session_state['show_small_card'] = False
                st.session_state['show_modal'] = True
                st.session_state['finca_id'] = str(finca.get('id'))
                st.experimental_rerun()
            if st.button("Cerrar", key=f"close_small_{finca.get('id')}"):
                st.session_state['clicked_fid'] = None
                st.session_state['show_small_card'] = False
                try:
                    st.experimental_set_query_params()
                except Exception:
                    pass
                try:
                    top_modal.empty()
                except Exception:
                    pass
                try:
                    inject_history_replace()
                except Exception:
                    pass
                st.experimental_rerun()


def render_large_modal(top_modal, finca):
    """Render detailed modal using native Streamlit widgets inside the top placeholder.
    Buttons here trigger Python state changes so closure is clean.
    """
    if finca is None:
        return
    thumb = get_browser_image_url(get_thumb(finca))
    # Prefer native Streamlit modal if available (overlay handled by Streamlit)
    try:
        with st.modal("Detalles de la Finca"):
            c1, c2 = st.columns([1, 2])
            with c1:
                try:
                    st.image(thumb, use_column_width=True)
                except Exception:
                    st.image(placeholder, use_column_width=True)
            with c2:
                st.header(finca.get('direccion','—'))
                st.write(f"**Superficie:** {finca.get('superficie_m2','—')} m2")
                st.write(f"**PVP:** {finca.get('pvp','—')} €")
                st.write(f"**Ref. catastral:** {finca.get('ref_catastral','—')}")
                st.write(f"\n{finca.get('descripcion','')}")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Reservar", key=f"reserve_{finca.get('id')}"):
                        st.experimental_set_query_params(action='reserve', fid=finca.get('id'))
                with col_b:
                    if st.button("Comprar", key=f"buy_{finca.get('id')}"):
                        st.experimental_set_query_params(action='buy', fid=finca.get('id'))
                if st.button("Cerrar", key=f"close_modal_{finca.get('id')}"):
                    st.session_state['show_modal'] = False
                    st.session_state['clicked_fid'] = None
                    st.session_state['finca_id'] = None
                    try:
                        st.experimental_set_query_params()
                    except Exception:
                        pass
                    try:
                        inject_history_replace()
                    except Exception:
                        pass
                    st.experimental_rerun()
    except Exception:
        # Fallback to rendering inside top_modal if st.modal isn't available
        with top_modal.container():
            c1, c2 = st.columns([1, 2])
            with c1:
                try:
                    st.image(thumb, use_column_width=True)
                except Exception:
                    st.image(placeholder, use_column_width=True)
            with c2:
                st.header(finca.get('direccion','—'))
                st.write(f"**Superficie:** {finca.get('superficie_m2','—')} m2")
                st.write(f"**PVP:** {finca.get('pvp','—')} €")
                st.write(f"**Ref. catastral:** {finca.get('ref_catastral','—')}")
                st.write(f"\n{finca.get('descripcion','')}")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Reservar", key=f"reserve_{finca.get('id')}"):
                        st.experimental_set_query_params(action='reserve', fid=finca.get('id'))
                with col_b:
                    if st.button("Comprar", key=f"buy_{finca.get('id')}"):
                        st.experimental_set_query_params(action='buy', fid=finca.get('id'))
                if st.button("Cerrar", key=f"close_modal_{finca.get('id')}"):
                    st.session_state['show_modal'] = False
                    st.session_state['clicked_fid'] = None
                    st.session_state['finca_id'] = None
                    try:
                        st.experimental_set_query_params()
                    except Exception:
                        pass
                    try:
                        top_modal.empty()
                    except Exception:
                        pass
                    try:
                        inject_history_replace()
                    except Exception:
                        pass
                    st.experimental_rerun()

# ==========================================
# FUNCIONES DE DIAGNÓSTICO
# ==========================================

def check_backend():
    try:
        r = requests.get("http://localhost:8000/health", timeout=2)
        return r.status_code == 200 and r.json().get("status") == "ok"
    except Exception:
        return False

# ==========================================
# INICIALIZACIÓN DEL SISTEMA
# ==========================================

inicializar_conexion()

# ==========================================
# HEADER PRINCIPAL
# ==========================================

def render_app_header():
    """Header de la aplicación"""
    render_header()

# ==========================================
# PANEL PRINCIPAL DEL CLIENTE
# ==========================================

def main():
    # Inicializar estado de sesión para coherencia
    if "finca_id" not in st.session_state:
        st.session_state["finca_id"] = None
    if "show_modal" not in st.session_state:
        st.session_state["show_modal"] = False
    if "clicked_fid" not in st.session_state:
        st.session_state["clicked_fid"] = None
    if "show_small_card" not in st.session_state:
        st.session_state["show_small_card"] = False

    # Normalizar estado y entrada (query params + session)
    params = st.experimental_get_query_params()
    if params.get("modal", ["0"])[0] == "1" and params.get("fid"):
        st.session_state["finca_id"] = params["fid"][0]
        st.session_state["show_modal"] = True
    # Manejar acciones de reserva/compra vía query params (página de confirmación)
    action = params.get("action", [None])[0]
    if action in ("reserve", "buy") and params.get("fid"):
        fid_act = params["fid"][0]
        # Mostrar página simple de confirmación y evitar render normal
        st.title("Confirmación de acción")
        if action == "reserve":
            st.success(f"✅ Reserva registrada para finca {fid_act}")
            st.write("Te enviaremos más detalles por email (MVP).")
        else:
            st.success(f"✅ Compra simulada completada para finca {fid_act}")
            st.write("Gracias por tu compra. Se abrirán más opciones para seguir (MVP).")
        st.write("[Volver al inicio](./)")
        return

    # Mostrar header siempre
    render_app_header()
    # Placeholder en la parte superior para modal (se usa para mostrar overlay en top)
    top_modal = st.empty()

    # Indicador global de backend mejorado
    BACKEND_URL = "http://localhost:8000"
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=2)
        is_backend_ok = r.status_code == 200 and r.json().get("status") == "ok"
    except Exception:
        is_backend_ok = False

    if is_backend_ok:
        status_label = "🟢 **Backend conectado** - Modo Producción"
        status_color = "green"
    else:
        status_label = "🔴 **Backend desconectado** - Modo Demo"
        status_color = "red"

    st.markdown(f"<h4 style='color: {status_color};'>{status_label}</h4>", unsafe_allow_html=True)

    if not is_backend_ok:
        st.warning("⚠️ El backend FastAPI no está disponible. La aplicación funciona en modo demostración con datos de ejemplo.")
        st.info("💡 **Para activar modo producción**: Ejecute en terminal: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8000`")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Actualizar estado", help="Verificar conexión con backend"):
            st.rerun()

    # Sidebar con navegación
    with st.sidebar:
        st.markdown("### 🎯 Mi Panel")

        # Navegación principal
        opciones = [
            "🏠 Inicio",
            "👥 Owners",
            "📊 Panel Cliente",
            "🏡 Ficha Finca",
            "📊 Mis Proyectos",
            "🏢 Intranet Arquitectos",
            "🧠 Gemelo Digital",
            "📦 Exportar Proyecto"
        ]

        seleccion = st.radio("Navegación:", opciones, key="navegacion_radio")

        # Actualizar session_state
        st.session_state.seleccion = seleccion

        # Sección de acceso (no bloqueante)
        st.markdown("### 🔐 Acceso")
        email = st.text_input(
            "Tu email (opcional para explorar, requerido para guardar/exportar)",
            value=st.session_state.get("email", ""),
            key="user_email"
        )
        if email:
            st.session_state["email"] = email
            st.success(f"✅ Acceso completo: {email}")
        else:
            st.info("💡 Puedes explorar libremente. Para guardar/exportar, introduce tu email.")

        # Información del sistema
        with st.expander("ℹ️ Estado del Sistema"):
            mostrar_estado_conexion()

            if st.session_state.get("proyecto_actual"):
                st.markdown(f"**Proyecto:** {st.session_state.proyecto_actual.get('titulo', 'N/A')}")
                st.markdown(f"**Versión:** {st.session_state.proyecto_actual.get('version', 0)}")

    # Contenido principal - SIEMPRE accesible
    if seleccion == "🏠 Inicio":
        render_inicio(top_modal)
    elif seleccion == "👥 Owners":
        render_owners()
    elif seleccion == "📊 Panel Cliente":
        render_panel_cliente()
    elif seleccion == "🏡 Ficha Finca":
        render_ficha_finca()
    elif seleccion == "📊 Mis Proyectos":
        render_mis_proyectos()
    elif seleccion == "🏢 Intranet Arquitectos":
        render_intranet_arquitectos()
    elif seleccion == "🧠 Gemelo Digital":
        render_gemelo_digital()
        render_precios_vivo()
    elif seleccion == "📦 Exportar Proyecto":
        render_exportacion()

# ==========================================
# PANTALLA DE INICIO
# ==========================================

def render_inicio(top_modal=None):
    st.header("🏠 Bienvenido a ARCHIRAPID")

    st.markdown("""
    ### 🚀 Tu casa ideal en minutos con IA

    **ARCHIRAPID** combina inteligencia artificial avanzada con precios en tiempo real
    para crear diseños arquitectónicos profesionales al instante.

    #### ✨ Lo que puedes hacer:
    - 🎨 **Diseñar con IA**: Describe tu casa ideal y la IA la crea
    - 💰 **Precios en Vivo**: Ve cómo cambian los precios en tiempo real
    - 📦 **Exportación Profesional**: Obtén planos CAD, memorias técnicas y presupuestos
    - 🔄 **Iteración Continua**: Modifica y perfecciona tu diseño paso a paso
    """)

    # Ensure we have a top placeholder to render modal overlay
    if top_modal is None:
        top_modal = st.empty()

    # Limpieza: si no hay card ni modal activo, asegurarse de vaciar el placeholder superior
    if not st.session_state.get('show_small_card', False) and not st.session_state.get('show_modal', False):
        try:
            top_modal.empty()
        except Exception:
            pass

    # Mostrar mapa con fincas disponibles
    fincas = load_fincas()
    if not fincas:
        st.warning("No hay fincas disponibles. El sistema está en modo demo.")
        return
    render_mapa_inmobiliario(fincas)

    # Si el usuario ha hecho clic en un marcador, mostrar el small card en el placeholder superior
    if st.session_state.get('clicked_fid') and st.session_state.get('show_small_card', False):
        finca = get_finca_by_id(fincas, st.session_state.get('clicked_fid'))
        render_small_card(top_modal, finca)

    # Si el usuario pide ver más detalles, mostrar modal grande
    if st.session_state.get('show_modal'):
        fid = st.session_state.get('finca_id') or st.session_state.get('clicked_fid')
        finca = get_finca_by_id(fincas, fid)
        render_large_modal(top_modal, finca)

    # Lista lateral con fincas para explorar
    st.markdown("---")
    st.subheader("🏡 Fincas Disponibles")

    if not fincas:
        st.warning("No hay fincas disponibles. El sistema está en modo demo.")
        return

    # Mostrar lista de fincas en formato 3x3
    # Ordenar por ID descendente (más recientes primero) y tomar máximo 9
    fincas_ordenadas = sorted(fincas, key=lambda x: x.get('id', 0), reverse=True)[:9]

    if not fincas_ordenadas:
        st.info("No hay fincas disponibles.")
    else:
        # Mostrar fincas en filas de 3 columnas
        for i in range(0, len(fincas_ordenadas), 3):
            row = st.columns(3)
            for j in range(3):
                if i + j < len(fincas_ordenadas):
                    f = fincas_ordenadas[i + j]
                    foto = f.get("foto_url", [placeholder])[0]
                    with row[j]:
                        cols = st.columns([1, 2])
                        with cols[0]:
                            img_src = get_browser_image_url(foto)
                            st.image(img_src, width=120)
                        with cols[1]:
                            st.write(f"{f['direccion']}")
                            st.write(f"Superficie: {f['superficie_m2']} m2")
                            st.write(f"PVP: {f.get('pvp','—')} €")
                            if st.button(f"Ver detalles {f.get('id','')}"):
                                st.session_state["finca_id"] = str(f.get("id"))
                                st.session_state["show_modal"] = True
                                st.experimental_rerun()  # usar st.rerun si está disponible

    # Modal — render en el placeholder superior para que aparezca encima del mapa
    if st.session_state.get("show_modal", False):
        fid = st.session_state.get("finca_id")
        finca = get_finca_by_id(fincas, fid)

        # Render overlay via components.html to ensure true overlay behavior
        img_src = get_browser_image_url(get_thumb(finca)) if finca else ""
        fid_js = fid or ""
        direccion = finca.get('direccion') if finca else ''
        superficie = finca.get('superficie_m2') if finca else ''
        pvp_val = finca.get('pvp') if finca else ''
        ref_cat = finca.get('ref_catastral') if finca else ''

        popup_html = """
<style>
.ar_overlay {{ position: fixed; inset: 0; background: rgba(0,0,0,0.25); z-index: 9999; display:flex; align-items:center; justify-content:center; padding:24px; }}
.ar_modal {{ background: #fff; border-radius:8px; width:90%; max-width:920px; padding:20px; box-shadow:0 12px 32px rgba(0,0,0,0.25); font-family: Arial, sans-serif; max-height:85vh; overflow:auto; }}
.ar_row {{ display:flex; gap:16px; flex-wrap:wrap; }}
.ar_img {{ width:320px; flex:0 0 320px; }}
.ar_actions button {{ margin-right:8px; padding:8px 12px; border-radius:6px; border:none; cursor:pointer; }}
.btn_reserve {{ background:#f0ad4e; color:#111 }}
.btn_buy {{ background:#d9534f; color:#fff }}
.btn_close {{ background:#6c757d; color:#fff }}
</style>
<div class="ar_overlay" id="ar_overlay">
    <div class="ar_modal" role="dialog" aria-modal="true">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
            <h3 style="margin:0;">Detalles de la Finca</h3>
            <button onclick="(function(){document.getElementById('ar_overlay').style.display='none';})()" class="btn_close">Cerrar</button>
        </div>
        <div class="ar_row">
            <div class="ar_img"><img src="{img_src}" style="width:100%;border-radius:6px;"/></div>
            <div style="flex:1;min-width:260px;">
                <h4 id="ar_direccion">{direccion}</h4>
                <p id="ar_superficie"><strong>Superficie:</strong> {superficie} m2</p>
                <p id="ar_pvp"><strong>PVP:</strong> {pvp_val} €</p>
                <p id="ar_ref"><strong>Ref. catastral:</strong> {ref_cat}</p>
                <div class="ar_actions" style="margin-top:12px;">
                    <button class="btn_reserve" onclick="window.top.location.href='?action=reserve&fid={fid_js}'">Reservar</button>
                    <button class="btn_buy" onclick="window.top.location.href='?action=buy&fid={fid_js}'">Comprar</button>
                </div>
            </div>
        </div>
    </div>
"""
        # Use safe replacements instead of .format() to avoid interpreting CSS/JS braces
        popup_html = popup_html.replace('{img_src}', img_src)
        popup_html = popup_html.replace('{direccion}', direccion)
        popup_html = popup_html.replace('{superficie}', str(superficie))
        popup_html = popup_html.replace('{pvp_val}', str(pvp_val))
        popup_html = popup_html.replace('{ref_cat}', str(ref_cat))
        popup_html = popup_html.replace('{fid_js}', str(fid_js))

        # Render the HTML inside the top placeholder so it appears above all content
        try:
            with top_modal:
                components_html(popup_html, height=700)
        except Exception:
            # Fallback: render in-place if top_modal context fails
            components_html(popup_html, height=700)

    render_footer()

def render_owners():
    st.header("👥 Panel de Propietarios - Subir Fincas")

    st.markdown("""
    ### 🏠 Sube tu finca al mercado inmobiliario

    Completa tus datos personales y los de tu propiedad para que aparezca en el mapa y arquitectos puedan diseñar proyectos con IA.
    """)

    # Verificar si hay una finca recién creada para mostrar confirmación
    if st.session_state.get("finca_creada", False):
        propietario = st.session_state.get("propietario_actual", {})
        finca = st.session_state.get("finca_reciente", {})

        st.success("✅ ¡Propiedad registrada correctamente!")
        st.balloons()

        st.markdown(f"""
        ### 🎉 ¡Registro completado!

        **Propietario:** {propietario.get('nombre', 'N/A')}  
        **Finca:** {finca.get('direccion', 'N/A')}  
        **Superficie:** {finca.get('superficie_m2', 0)} m2

        Tu propiedad ha sido añadida al mapa y está disponible para que arquitectos diseñen proyectos con IA.

        **¿Qué sigue?**
        - Los arquitectos podrán ver tu finca en el mapa
        - Recibirás notificaciones cuando haya interés
        - Podrás acceder a tu Panel Cliente para gestionar proyectos
        """)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("👤 Ir a Mi Panel Cliente", type="primary", use_container_width=True):
                st.session_state.seleccion = "📊 Panel Cliente"
                st.session_state.finca_creada = False  # Limpiar flag
                st.rerun()

        with col2:
            if st.button("➕ Registrar Otra Propiedad", use_container_width=True):
                st.session_state.finca_creada = False  # Limpiar flag
                st.rerun()

        render_footer()
        return

    # Formulario completo: datos personales + finca
    with st.form("form_propietario_finca"):
        # Sección 1: Datos Personales del Propietario
        st.subheader("👤 Datos Personales del Propietario")

        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Nombre completo", placeholder="Juan Pérez García")
            email = st.text_input("Email", placeholder="juan@email.com")
            telefono = st.text_input("Teléfono", placeholder="+34 600 000 000")

        with col2:
            dni = st.text_input("DNI/NIF", placeholder="12345678A")
            direccion_propietario = st.text_input("Dirección del propietario", placeholder="Calle Mayor 123, Madrid")
            banco = st.text_input("Cuenta bancaria (opcional)", placeholder="ES12 3456 7890 1234 5678 9012")

        # Sección 2: Datos de la Finca
        st.subheader("🏠 Datos de la Finca")

        col1, col2 = st.columns(2)

        with col1:
            direccion = st.text_input("Dirección completa de la finca", placeholder="Calle Mayor 123, Madrid")
            superficie = st.number_input("Superficie (m2)", min_value=1.0, step=1.0, value=100.0)
            pvp = st.number_input("Precio de venta (PVP, €)", min_value=0.0, step=1000.0, value=150000.0)

        with col2:
            ref_catastral = st.text_input("Referencia catastral (opcional)")
            # Campos de coordenadas (se actualizarán después de geocodificación)
            default_lat = st.session_state.get("calculated_lat", 40.4168)
            default_lng = st.session_state.get("calculated_lng", -3.7038)
            lat = st.number_input("Latitud", value=default_lat, format="%.6f", key="lat_input")
            lng = st.number_input("Longitud", value=default_lng, format="%.6f", key="lng_input")

        # Nota catastral
        st.subheader("📄 Nota Catastral")
        nota_catastral_text = st.text_area("Descripción o resumen de la nota catastral", height=100)
        nota_catastral_file = st.file_uploader("Subir nota catastral (PDF/imagen)", type=["pdf","png","jpg","jpeg"])

        # Fotos
        st.subheader("📸 Fotos de la Finca")
        fotos = st.file_uploader("Subir fotos", type=["png","jpg","jpeg"], accept_multiple_files=True)

        # Geocodificación
        st.subheader("📍 Ubicación")
        if st.form_submit_button("🔍 Calcular coordenadas por dirección", use_container_width=True):
            if direccion:
                try:
                    geolocator = Nominatim(user_agent="archirapid_mvp")
                    loc = geolocator.geocode(direccion)
                    if loc:
                        # Actualizar los campos de coordenadas
                        st.session_state.calculated_lat = loc.latitude
                        st.session_state.calculated_lng = loc.longitude
                        st.success(f"✅ Coordenadas calculadas: {loc.latitude:.6f}, {loc.longitude:.6f}")
                        st.rerun()
                    else:
                        st.warning("⚠️ No se encontraron coordenadas para esa dirección. Introduce manualmente.")
                except Exception as e:
                    st.error(f"❌ Error en geocodificación: {e}")
            else:
                st.warning("⚠️ Introduce una dirección primero.")

        # Comisión estimada
        if pvp and pvp > 0:
            st.subheader("💰 Estimación de Comisión")
            com_min = round(pvp * 0.07, 2)
            com_max = round(pvp * 0.10, 2)
            neto_min = round(pvp - com_min, 2)
            neto_max = round(pvp - com_max, 2)

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Comisión mínima (7%)", f"€{com_min:,.0f}")
                st.metric("Neto para empresa", f"€{neto_min:,.0f}")
            with col2:
                st.metric("Comisión máxima (10%)", f"€{com_max:,.0f}")
                st.metric("Neto para empresa", f"€{neto_max:,.0f}")

            st.caption("La comisión real se ajustará según negociación y servicios prestados.")

        # Botón de guardar
        submitted = st.form_submit_button("💾 Guardar Propiedad y Acceder al Panel Cliente", type="primary")

        if submitted:
            # Validaciones
            if not nombre or not email or not telefono or not direccion or superficie <= 0 or (lat == 0.0 and lng == 0.0):
                st.error("❌ Nombre, email, teléfono, dirección de la finca, superficie y coordenadas son obligatorios.")
                return

            # Preparar payload con datos del propietario
            foto_urls = []
            if fotos:
                # Guardar fotos en static/fotos/ con nombres únicos
                import uuid
                import os
                from datetime import datetime
                
                fotos_dir = "static/fotos"
                os.makedirs(fotos_dir, exist_ok=True)
                
                # Generar ID único para la finca (temporal hasta que el backend asigne el real)
                temp_id = str(uuid.uuid4())[:8]
                
                for i, foto in enumerate(fotos):
                    # Generar nombre único para cada foto
                    extension = os.path.splitext(foto.name)[1].lower()
                    if extension not in ['.jpg', '.jpeg', '.png']:
                        extension = '.jpg'
                    
                    filename = f"finca_{temp_id}_{i+1}{extension}"
                    filepath = os.path.join(fotos_dir, filename)
                    
                    # Guardar imagen
                    with open(filepath, "wb") as f:
                        f.write(foto.getbuffer())
                    
                    # Generar URL relativa
                    foto_urls.append(f"/static/fotos/{filename}")
            else:
                # Si no hay fotos, usar placeholder
                foto_urls = ["/static/no-photo.png"]

            payload = {
                "direccion": direccion,
                "superficie_m2": float(superficie),
                "ref_catastral": ref_catastral or None,
                "foto_url": foto_urls,
                "ubicacion_geo": {"lat": float(lat), "lng": float(lng)},
                "max_construible_m2": float(superficie * 0.33),  # 33% de la superficie
                "retranqueos": None,
                "propietario": {
                    "nombre": nombre,
                    "email": email,
                    "telefono": telefono,
                    "dni": dni or None,
                    "direccion": direccion_propietario or None,
                    "cuenta_bancaria": banco or None
                },
                "estado": "pendiente",
                "pvp": float(pvp) if pvp else None,
                "sync_intranet": False  # Preparado para futura sincronización
            }

            # Enviar al backend
            try:
                BACKEND_URL = "http://localhost:8000"
                r = requests.post(f"{BACKEND_URL}/fincas", json=payload, timeout=5)
                if r.status_code in (200, 201):
                    # Guardar datos del propietario en session_state para el panel cliente
                    st.session_state.propietario_actual = {
                        "nombre": nombre,
                        "email": email,
                        "telefono": telefono,
                        "dni": dni,
                        "direccion": direccion_propietario,
                        "cuenta_bancaria": banco
                    }
                    st.session_state.finca_reciente = payload
                    st.session_state.finca_creada = True  # Flag para mostrar confirmación
                    # Limpiar coordenadas calculadas para la siguiente finca
                    if "calculated_lat" in st.session_state:
                        del st.session_state.calculated_lat
                    if "calculated_lng" in st.session_state:
                        del st.session_state.calculated_lng
                    st.rerun()

                else:
                    st.error(f"❌ Error al crear propiedad: {r.status_code} → {r.text}")
            except Exception as e:
                st.error(f"❌ Error de conexión al backend: {e}")

    render_footer()

def render_panel_cliente():
    st.header("📊 Panel Cliente - Mis Propiedades")

    # Verificar si hay datos del propietario
    propietario = st.session_state.get("propietario_actual")
    if not propietario:
        st.warning("⚠️ No tienes propiedades registradas aún. Ve al panel de Owners para subir tu primera propiedad.")
        if st.button("👥 Ir a Panel de Owners", type="primary"):
            st.session_state.seleccion = "👥 Owners"
            st.rerun()
        render_footer()
        return

    # Bienvenida personalizada
    st.markdown(f"""
    ### 👋 ¡Hola {propietario['nombre']}!

    Bienvenido a tu Panel Cliente personal. Aquí puedes gestionar tus propiedades y ver el progreso de los proyectos arquitectónicos.
    """)

    # Información del propietario
    with st.expander("👤 Mis Datos Personales", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Nombre:** {propietario['nombre']}")
            st.markdown(f"**Email:** {propietario['email']}")
            st.markdown(f"**Teléfono:** {propietario['telefono']}")
        with col2:
            if propietario.get('dni'):
                st.markdown(f"**DNI/NIF:** {propietario['dni']}")
            if propietario.get('direccion'):
                st.markdown(f"**Dirección:** {propietario['direccion']}")
            if propietario.get('cuenta_bancaria'):
                st.markdown(f"**Cuenta Bancaria:** {'*' * 16 + propietario['cuenta_bancaria'][-4:]}")

    # Obtener propiedades del propietario
    try:
        BACKEND_URL = "http://localhost:8000"
        r = requests.get(f"{BACKEND_URL}/fincas?propietario_email={propietario['email']}", timeout=5)
        if r.status_code == 200:
            fincas = r.json()
        else:
            fincas = []
    except Exception as e:
        st.error(f"❌ Error al cargar propiedades: {e}")
        fincas = []

    if not fincas:
        st.info("📭 No tienes propiedades registradas aún.")
        if st.button("➕ Registrar Primera Propiedad", type="primary"):
            st.session_state.seleccion = "👥 Owners"
            st.rerun()
    else:
        st.subheader("🏠 Mis Propiedades")

        for finca in fincas:
            with st.container():
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"**🏡 {finca['direccion']}**")
                    st.markdown(f"**Superficie:** {finca['superficie_m2']} m2")
                    if finca.get('pvp'):
                        st.markdown(f"**PVP:** €{finca['pvp']:,.0f}")
                    st.markdown(f"**Estado:** {finca.get('estado', 'Pendiente')}")

                    # Estado visual
                    if finca.get('estado') == 'activa':
                        st.success("✅ Propiedad activa en el mercado")
                    elif finca.get('estado') == 'vendida':
                        st.info("💰 Propiedad vendida")
                    else:
                        st.warning("⏳ Pendiente de activación")

                with col2:
                    st.markdown("### 🎯 Acciones")

                    # Botón para ver diseños con IA
                    if st.button(f"🎨 Ver Diseños IA", key=f"disenos_{finca['id']}", use_container_width=True):
                        st.session_state.finca_actual = finca
                        st.session_state.pantalla_actual = "diseno_ia"
                        st.rerun()

                    # Botón para ver proyectos existentes
                    if st.button(f"📊 Ver Proyectos", key=f"proyectos_{finca['id']}", use_container_width=True):
                        proyectos = obtener_proyectos_con_fallback({"finca_id": finca["id"]})
                        if proyectos:
                            st.session_state.proyectos_finca = proyectos
                            st.session_state.pantalla_actual = "proyectos_finca"
                            st.rerun()
                        else:
                            st.info("No hay proyectos para esta finca aún.")

                    # Botón para editar propiedad
                    if st.button(f"✏️ Editar", key=f"editar_{finca['id']}", use_container_width=True):
                        st.info("Funcionalidad de edición próximamente disponible.")

                    # Botón para sincronizar con intranet
                    if finca.get('sync_intranet', False):
                        st.success("🔄 Sincronizado con Intranet")
                    else:
                        if st.button(f"🔄 Sync Intranet", key=f"sync_{finca['id']}", use_container_width=True):
                            st.info("Sincronización con intranet próximamente disponible.")

                st.divider()

        # Estadísticas generales
        st.subheader("📈 Estadísticas")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Propiedades", len(fincas))

        with col2:
            activas = sum(1 for f in fincas if f.get('estado') == 'activa')
            st.metric("Propiedades Activas", activas)

        with col3:
            total_valor = sum(f.get('pvp', 0) for f in fincas if f.get('pvp'))
            st.metric("Valor Total", f"€{total_valor:,.0f}")

    render_footer()

def render_ficha_finca():
    st.header("🏡 Ficha de Finca")

    # Obtener finca_id de session_state
    finca_id = st.session_state.get("finca_id")
    if not finca_id:
        st.error("No se ha seleccionado ninguna finca.")
        if st.button("← Volver al Inicio"):
            st.session_state.seleccion = "🏠 Inicio"
            st.rerun()
        render_footer()
        return

    # Obtener finca por ID
    try:
        BACKEND_URL = "http://localhost:8000"
        r = requests.get(f"{BACKEND_URL}/fincas", timeout=5)
        if r.status_code == 200:
            fincas = r.json()
            finca = next((f for f in fincas if str(f.get('id')) == str(finca_id)), None)
        else:
            finca = None
    except Exception as e:
        st.error(f"Error al cargar finca: {e}")
        finca = None

    if not finca:
        st.error("Finca no encontrada.")
        if st.button("← Volver al Inicio"):
            st.session_state.seleccion = "🏠 Inicio"
            st.rerun()
        render_footer()
        return

    # Mostrar ficha completa
    st.markdown(f"## 🏠 {finca['direccion']}")

    col1, col2 = st.columns([1, 2])

    with col1:
        # Foto principal
        foto_url = finca.get('foto_url', [])
        if foto_url and len(foto_url) > 0:
            st.image(foto_url[0], width=300, caption="Foto principal")
        else:
            st.image("https://via.placeholder.com/300x200.png?text=Sin+Foto", width=300, caption="Sin foto disponible")

        # Información básica
        st.subheader("📋 Información Básica")
        st.write(f"**Superficie:** {finca['superficie_m2']} m2")
        st.write(f"**Máx. Construible:** {finca.get('max_construible_m2', finca['superficie_m2'] * 0.33):.0f} m2")
        pvp = finca.get('pvp')
        st.write(f"**PVP:** {f'€{pvp:,.0f}' if pvp else 'No especificado'}")

        # Estado
        estado = finca.get('estado', 'pendiente')
        if estado == 'activa':
            st.success("✅ Propiedad activa en el mercado")
        elif estado == 'vendida':
            st.info("💰 Propiedad vendida")
        else:
            st.warning("⏳ Pendiente de activación")

    with col2:
        # Datos catastrales
        st.subheader("📄 Datos Catastrales")
        st.write(f"**Referencia Catastral:** {finca.get('ref_catastral', 'No especificada')}")

        # Ubicación
        st.subheader("📍 Ubicación")
        ubicacion = finca.get('ubicacion_geo', {})
        lat = ubicacion.get('lat', 'N/A')
        lng = ubicacion.get('lng', 'N/A')
        st.write(f"**Latitud:** {lat}")
        st.write(f"**Longitud:** {lng}")

        # Propietario (si está disponible)
        propietario = finca.get('propietario', {})
        if propietario:
            st.subheader("👤 Propietario")
            st.write(f"**Nombre:** {propietario.get('nombre', 'N/A')}")
            st.write(f"**Email:** {propietario.get('email', 'N/A')}")
            st.write(f"**Teléfono:** {propietario.get('telefono', 'N/A')}")

        # Acciones
        st.subheader("🎯 Acciones Disponibles")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎨 Diseñar con IA", type="primary", use_container_width=True):
                st.session_state.finca_actual = finca
                st.session_state.seleccion = "🧠 Gemelo Digital"
                st.rerun()

            if st.button("📊 Ver Proyectos Existentes", use_container_width=True):
                proyectos = obtener_proyectos_con_fallback({"finca_id": finca["id"]})
                if proyectos:
                    st.session_state.proyectos_finca = proyectos
                    st.session_state.seleccion = "📊 Mis Proyectos"
                    st.rerun()
                else:
                    st.info("No hay proyectos para esta finca aún.")

        with col2:
            if st.button("💰 Reservar/Comprar", use_container_width=True):
                st.success("✅ Reserva realizada (MVP demostrativo)")
                st.balloons()

            if st.button("📞 Contactar Propietario", use_container_width=True):
                st.info("Funcionalidad de contacto próximamente disponible.")

    # Botón volver
    st.markdown("---")
    if st.button("← Volver al Inicio"):
        st.session_state.seleccion = "🏠 Inicio"
        st.rerun()

    render_footer()

def render_diseno_ia():
    st.header("🎨 Diseño Inteligente con IA")

    if "finca_actual" not in st.session_state:
        st.warning("Primero selecciona una finca en la pantalla de inicio")
        return

    finca = st.session_state.finca_actual

    # Chat con IA para diseño
    st.subheader("💬 Describe tu casa ideal")

    # Historial de conversación
    if "chat_historial" not in st.session_state:
        st.session_state.chat_historial = []

    # Área de chat
    chat_container = st.container()

    with chat_container:
        for mensaje in st.session_state.chat_historial[-10:]:  # Últimos 10 mensajes
            if mensaje["tipo"] == "usuario":
                st.markdown(f"**👤 Tú:** {mensaje['texto']}")
            else:
                st.markdown(f"**🤖 IA:** {mensaje['texto']}")

    # Input para nuevo mensaje
    col1, col2 = st.columns([4, 1])

    with col1:
        mensaje_usuario = st.text_input(
            "Describe qué quieres en tu casa:",
            placeholder="Ej: Quiero una casa moderna de 3 habitaciones con piscina y garaje...",
            key="mensaje_ia",
            label_visibility="collapsed"
        )

    with col2:
        if st.button("📤 Enviar", type="primary", use_container_width=True):
            if mensaje_usuario.strip():
                # Añadir mensaje del usuario
                st.session_state.chat_historial.append({
                    "tipo": "usuario",
                    "texto": mensaje_usuario,
                    "timestamp": datetime.now()
                })

                # Procesar con IA y generar respuesta
                respuesta_ia = procesar_mensaje_ia(mensaje_usuario, finca)

                st.session_state.chat_historial.append({
                    "tipo": "ia",
                    "texto": respuesta_ia,
                    "timestamp": datetime.now()
                })

                st.rerun()

    # Mostrar plan actual si existe
    if "plan_actual" in st.session_state:
        render_plan_actual()

    # Acciones del plan
    if st.session_state.get("plan_actual"):
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Modificar con IA", use_container_width=True):
                st.info("Describe los cambios que quieres hacer")

        with col2:
            if st.button("💰 Ver Precios en Vivo", type="primary", use_container_width=True):
                st.session_state.pantalla_actual = "precios_vivo"
                st.rerun()

        with col3:
            if st.button("📦 Exportar Profesional", type="primary", use_container_width=True):
                st.session_state.pantalla_actual = "exportacion"
                st.rerun()

def procesar_mensaje_ia(mensaje: str, finca: dict) -> str:
    """
    Procesa mensaje del usuario y actualiza el plan usando el motor paramétrico
    """
    # Lógica simplificada de procesamiento de IA
    # En producción, esto usaría un LLM avanzado

    mensaje_lower = mensaje.lower()

    # Inicializar plan si no existe
    if "plan_actual" not in st.session_state:
        st.session_state.plan_actual = parametric_engine({}, "validate", {"finca": finca})

    plan = st.session_state.plan_actual

    # Procesar diferentes tipos de solicitudes
    if "habitacion" in mensaje_lower or "dormitorio" in mensaje_lower:
        # Extraer número de habitaciones
        import re
        nums = re.findall(r'\d+', mensaje)
        if nums:
            num_hab = int(nums[0])
            for i in range(num_hab):
                plan = parametric_engine(plan, "add_room", {
                    "type": "bedroom",
                    "name": f"Dormitorio {i+1}"
                })
            respuesta = f"✅ Añadidas {num_hab} habitaciones al plano"

    elif "baño" in mensaje_lower or "bathroom" in mensaje_lower:
        nums = re.findall(r'\d+', mensaje)
        if nums:
            num_banos = int(nums[0])
            for i in range(num_banos):
                plan = parametric_engine(plan, "add_room", {
                    "type": "bathroom",
                    "name": f"Baño {i+1}"
                })
            respuesta = f"✅ Añadidos {num_banos} baños al plano"

    elif "piscina" in mensaje_lower or "pool" in mensaje_lower:
        plan = parametric_engine(plan, "add_system", {
            "system_type": "pool",
            "config": {"exists": True, "area": 50}
        })
        respuesta = "✅ Piscina añadida al diseño"

    elif "moderno" in mensaje_lower or "modern" in mensaje_lower:
        plan = parametric_engine(plan, "set_style", {"style": "modern"})
        respuesta = "✅ Estilo moderno aplicado al diseño"

    elif "clasico" in mensaje_lower or "classic" in mensaje_lower:
        plan = parametric_engine(plan, "set_style", {"style": "classic"})
        respuesta = "✅ Estilo clásico aplicado al diseño"

    elif "distribuir" in mensaje_lower or "layout" in mensaje_lower:
        plan = parametric_engine(plan, "auto_layout")
        respuesta = "✅ Distribución automática optimizada"

    else:
        respuesta = "🤔 Entiendo tu solicitud. Estoy procesando los cambios en el plano. ¿Puedes darme más detalles sobre qué tipo de espacio necesitas?"

    # Actualizar plan en sesión
    st.session_state.plan_actual = plan

    return respuesta

def render_plan_actual():
    """Muestra el plan actual en formato visual"""
    plan = st.session_state.plan_actual

    st.subheader("📋 Plan Actual")

    col1, col2, col3 = st.columns(3)

    with col1:
        rooms = plan.get("program", {}).get("rooms", [])
        st.metric("Habitaciones", len([r for r in rooms if r.get("type") == "bedroom"]))
        st.metric("Baños", len([r for r in rooms if r.get("type") == "bathroom"]))

    with col2:
        total_m2 = plan.get("program", {}).get("total_m2", 0)
        st.metric("Superficie Total", f"{total_m2} m2")

    with col3:
        precio = calculate_live_price(plan)
        st.metric("Presupuesto Estimado", f"€{precio['breakdown']['total']:,.0f}")

    # Mostrar distribución
    with st.expander("📊 Ver distribución detallada"):
        st.json(plan)

    render_footer()

def render_precios_vivo():
    st.header("💰 Precios en Vivo")

    if "plan_actual" not in st.session_state:
        st.warning("Primero crea un diseño en la sección 'Diseñar con IA'")
        return

    plan = st.session_state.plan_actual

    st.markdown("""
    ### 🎛️ Configurador Interactivo

    Modifica las características de tu casa y ve cómo cambian los precios **en tiempo real**,
    igual que configurar un coche.
    """)

    # Controles interactivos en columnas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏠 Características de la Vivienda")

        # Sistema eléctrico inteligente
        electrico_smart = st.checkbox(
            "⚡ Sistema Eléctrico Inteligente (+€35/m2)",
            value=plan.get("systems", {}).get("electrical", {}).get("smart_home", False)
        )

        # Iluminación LED
        iluminacion_led = st.checkbox(
            "💡 Iluminación LED Premium (+€25/m2)",
            value=plan.get("systems", {}).get("lighting", {}).get("led_lighting", False)
        )

        # Domótica completa
        domotica = st.checkbox(
            "🏠 Domótica Completa (+€35/m2)",
            value=plan.get("systems", {}).get("smart_home", {}).get("enabled", False)
        )

        # Materiales premium
        materiales_premium = st.selectbox(
            "🛠️ Calidad de Materiales",
            ["Estándar", "Premium (+15%)", "Lujo (+30%)"],
            index=0
        )

    with col2:
        st.subheader("🌟 Acabados y Equipamiento")

        # Piscina
        piscina = st.checkbox(
            "🏊 Piscina (+€300/m2)",
            value=plan.get("site", {}).get("pool", {}).get("exists", False)
        )

        # Cocina premium
        cocina_premium = st.checkbox(
            "👨‍🍳 Cocina Premium (+€15,000)",
            value=False  # Por defecto no marcado
        )

        # Baños premium
        banos_premium = st.checkbox(
            "🛁 Baños Premium (+€8,000 c/u)",
            value=False
        )

        # Garaje
        garaje = st.checkbox(
            "🚗 Garaje (+€25/m2)",
            value=False
        )

    # Aplicar cambios al plan en tiempo real
    plan_actualizado = plan.copy()

    # Aplicar sistemas
    if electrico_smart:
        plan_actualizado = parametric_engine(plan_actualizado, "add_system", {
            "system_type": "electrical",
            "config": {"smart_home": True}
        })

    if iluminacion_led:
        plan_actualizado = parametric_engine(plan_actualizado, "add_system", {
            "system_type": "lighting",
            "config": {"led_lighting": True}
        })

    if domotica:
        plan_actualizado = parametric_engine(plan_actualizado, "add_system", {
            "system_type": "smart_home",
            "config": {"enabled": True}
        })

    # Aplicar piscina
    if piscina:
        plan_actualizado = parametric_engine(plan_actualizado, "add_system", {
            "system_type": "pool",
            "config": {"exists": True, "area": 50}
        })

    # Calcular precios con los cambios
    pricing = calculate_live_price(plan_actualizado)

    # Mostrar precios en tiempo real
    st.markdown("---")
    st.subheader("💎 Precio Total en Tiempo Real")

    # Métrica principal
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Precio Base",
            f"€{pricing['breakdown']['subtotal_construction']:,.0f}",
            help="Construcción básica"
        )

    with col2:
        st.metric(
            "Sistemas",
            f"€{pricing['breakdown']['systems']:,.0f}",
            help="Instalaciones avanzadas"
        )

    with col3:
        st.metric(
            "Acabados",
            f"€{pricing['breakdown']['finishes']:,.0f}",
            help="Materiales y mobiliario"
        )

    with col4:
        st.metric(
            "TOTAL",
            f"€{pricing['breakdown']['total']:,.0f}",
            delta=f"€{pricing['per_m2']:,.0f}/m2",
            help="Precio final completo"
        )

    # Desglose detallado
    with st.expander("📊 Desglose Completo del Presupuesto"):
        st.markdown("#### 🏗️ Construcción")
        st.write(f"- Base: €{pricing['breakdown']['base_construction']:,.0f}")
        st.write(f"- Multiplicador calidad: {pricing['breakdown']['construction_multiplier']:.2f}x")
        st.write(f"- **Subtotal construcción: €{pricing['breakdown']['subtotal_construction']:,.0f}**")

        st.markdown("#### ⚡ Sistemas e Instalaciones")
        st.write(f"- Sistemas avanzados: €{pricing['breakdown']['systems']:,.0f}")
        st.write(f"- Materiales: €{pricing['breakdown']['materials']:,.0f}")
        st.write(f"- Acabados: €{pricing['breakdown']['finishes']:,.0f}")

        st.markdown("#### 💼 Honorarios y Licencias")
        st.write(f"- Honorarios profesionales: €{pricing['breakdown']['professional_fees']:,.0f}")
        st.write(f"- Impuestos y licencias: €{pricing['breakdown']['taxes_licenses']:,.0f}")

        st.markdown(f"#### 📅 Cronograma: {pricing['estimated_duration_months']} meses")

    # Opciones de financiación
    with st.expander("💳 Opciones de Financiación"):
        for opcion in pricing["financing_options"]:
            st.markdown(f"**{opcion['type']}:** €{opcion['monthly_payment']:.0f}/meso")
            st.caption(f"Total a pagar: €{opcion['final_amount']:,.0f}")

    # Guardar cambios
    if st.button("💾 Guardar Configuración", type="primary"):
        st.session_state.plan_actual = plan_actualizado
        st.success("✅ Configuración guardada exitosamente")

    # Continuar al siguiente paso
    if st.button("📦 Continuar a Exportación Profesional", type="primary"):
        st.session_state.pantalla_actual = "exportacion"
        st.rerun()

    render_footer()

def render_exportacion():
    st.header("📦 Exportación Profesional")

    if "plan_actual" not in st.session_state:
        st.warning("Primero crea un diseño en la sección 'Diseñar con IA'")
        return

    plan = st.session_state.plan_actual

    st.markdown("""
    ### 🎯 Exportación Profesional Completa

    Genera todos los documentos técnicos necesarios para construir tu casa:
    planos CAD, memorias técnicas, presupuestos detallados y más.
    """)

    # Opciones de exportación disponibles
    opciones_disponibles = get_export_options()

    st.subheader("📋 Selecciona qué documentos necesitas:")

    # Crear checkboxes para cada opción
    opciones_seleccionadas = []
    cols = st.columns(2)

    for i, opcion in enumerate(opciones_disponibles):
        col_idx = i % 2
        with cols[col_idx]:
            if st.checkbox(opcion, value=True):  # Por defecto todas seleccionadas
                opciones_seleccionadas.append(opcion)

    # Información del proyecto
    st.markdown("---")
    st.subheader("📊 Información del Proyecto")

    col1, col2 = st.columns(2)

    with col1:
        titulo = st.text_input(
            "Título del proyecto:",
            value=f"Proyecto ARCHIRAPID - {datetime.now().strftime('%d/%m/%Y')}"
        )

        descripcion = st.text_area(
            "Descripción:",
            value="Proyecto de vivienda unifamiliar diseñado con IA avanzada",
            height=100
        )

    with col2:
        autor = st.text_input("Autor:", value="Cliente ARCHIRAPID")
        version = st.text_input("Versión:", value="1.0")

        # Calcular tamaño estimado
        from export_ops import estimate_export_size
        tamano_estimado = estimate_export_size(opciones_seleccionadas)
        st.metric("Tamaño estimado", f"{tamano_estimado:.1f} MB")

    # Botón de exportación
    if st.button("🚀 Generar Exportación Profesional", type="primary", use_container_width=True):
        with st.spinner("🎨 Generando documentos profesionales... Esto puede tomar unos minutos"):

            # Preparar datos del proyecto
            proyecto_data = {
                "titulo": titulo,
                "descripcion": descripcion,
                "autor": autor,
                "version": version,
                "plan_json": plan,
                "fecha_creacion": datetime.now().isoformat()
            }

            # Generar exportación
            try:
                export_result = exportar_proyecto(proyecto_data, opciones_seleccionadas)

                if export_result:
                    st.success("✅ ¡Exportación completada exitosamente!")

                    # Mostrar resumen
                    st.subheader("📁 Archivos Generados")

                    if "files_generated" in export_result:
                        for archivo in export_result["files_generated"]:
                            col1, col2, col3 = st.columns([3, 1, 1])
                            with col1:
                                st.write(f"📄 {archivo.get('description', archivo.get('filename', 'Archivo'))}")
                            with col2:
                                st.write(f"{archivo.get('type', 'N/A')}")
                            with col3:
                                st.write(f"{archivo.get('size_bytes', 0) / 1024:.1f} KB")

                    # Botón de descarga del bundle
                    if "bundle_file" in export_result:
                        st.download_button(
                            label="📥 Descargar Bundle Completo (ZIP)",
                            data=b"mock_zip_content",  # En producción sería el contenido real
                            file_name=export_result["bundle_file"].get("filename", "export.zip"),
                            mime="application/zip",
                            use_container_width=True
                        )

                    st.balloons()

                else:
                    st.error("❌ Error al generar la exportación")

            except Exception as e:
                st.error(f"❌ Error durante la exportación: {str(e)}")

    # Información adicional
    with st.expander("ℹ️ ¿Qué incluye cada documento?"):
        st.markdown("""
        #### 📄 Memoria Técnica PDF
        - Descripción completa del proyecto
        - Justificación técnica de las soluciones adoptadas
        - Cálculos estructurales y de instalaciones
        - Presupuesto detallado
        - Anexos con normativas aplicables

        #### 🏗️ Planos CAD/DWG
        - Planta baja, alzados y secciones
        - Planos de estructura, instalaciones y detalles
        - Formato compatible con AutoCAD y software similar

        #### 💰 Presupuesto Detallado
        - Desglose completo por partidas
        - Cronograma de pagos sugerido
        - Opciones de financiación
        - Comparativo de calidades

        #### 📊 Análisis Estructural
        - Cálculos de estructura portante
        - Análisis de cargas y solicitaciones
        - Certificados de cumplimiento normativo

        #### ⚡ Planos Eléctricos
        - Diagrama unifilar
        - Distribución de circuitos
        - Ubicación de puntos de luz y tomas

        #### 🚿 Planos de Fontanería
        - Distribución de agua fría y caliente
        - Sistema de evacuación
        - Ubicación de aparatos sanitarios

        #### 📋 Lista de Materiales
        - Catálogo completo de materiales
        - Cantidades y calidades
        - Referencias de proveedores

        #### 🪑 Plano de Muebles
        - Distribución del mobiliario
        - Especificaciones técnicas
        - Plano de implantación 2D
        """)

# ==========================================
# MIS PROYECTOS
# ==========================================

def render_mis_proyectos():
    st.header("📊 Mis Proyectos")

    # Obtener proyectos
    proyectos = obtener_proyectos_con_fallback()

    if not proyectos:
        st.info("Aún no tienes proyectos. ¡Comienza diseñando con IA!")
        return

    # Mostrar proyectos en cards
    for proyecto in proyectos:
        with st.expander(f"🏗️ {proyecto.get('titulo', 'Proyecto sin título')}"):

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Versión", proyecto.get("version", 1))
                st.metric("Superficie", f"{proyecto.get('total_m2', 0)} m2")

            with col2:
                presupuesto = proyecto.get("presupuesto", 0)
                st.metric("Presupuesto", f"€{presupuesto:,.0f}")

            with col3:
                estado = proyecto.get("estado", "borrador")
                if estado == "completado":
                    st.success("✅ Completado")
                elif estado == "en_progreso":
                    st.warning("🔄 En progreso")
                else:
                    st.info("📝 Borrador")

            # Acciones
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("👁️ Ver detalles", key=f"ver_{proyecto['id']}"):
                    st.session_state.proyecto_seleccionado = proyecto
                    st.session_state.pantalla_actual = "detalle_proyecto"

            with col2:
                if st.button("✏️ Continuar editando", key=f"editar_{proyecto['id']}"):
                    st.session_state.plan_actual = proyecto.get("plan_json", {})
                    st.session_state.pantalla_actual = "diseno_ia"

            with col3:
                if st.button("📦 Exportar", key=f"exportar_{proyecto['id']}"):
                    st.session_state.plan_actual = proyecto.get("plan_json", {})
                    st.session_state.pantalla_actual = "exportacion"

# ==========================================
# MAPA INMOBILIARIO
# ==========================================

def render_mapa_inmobiliario(fincas):
    st.header("🏠 Mapa Inmobiliario ARCHIRAPID")

    if not fincas:
        st.warning("No hay fincas disponibles para mostrar en el mapa.")
        return

    # Crear mapa interactivo
    import folium
    from streamlit_folium import st_folium

    # Centro de España por defecto
    mapa = folium.Map(
        location=[40.4168, -3.7038],  # Madrid
        zoom_start=6,
        tiles='OpenStreetMap'
    )

    # Añadir fincas al mapa
    for finca in fincas:
        # Coordenadas (usar reales si existen, sino cercanas a Madrid)
        lat = finca.get('ubicacion_geo', {}).get('lat', 40.4168 + (hash(finca['id']) % 100 - 50) * 0.01)
        lng = finca.get('ubicacion_geo', {}).get('lng', -3.7038 + (hash(finca['id']) % 100 - 50) * 0.01)

        # Color según estado
        color = 'green' if finca.get('estado') == 'disponible' else 'orange'

        # PVP para mostrar
        pvp = finca.get('pvp')
        pvp_str = f"€{pvp:,.0f}" if pvp else "Precio no especificado"

        # Foto para miniatura
        foto_url = finca.get('foto_url', [])
        if foto_url:
            img_src = get_browser_image_url(foto_url[0])
        else:
            img_src = get_browser_image_url(placeholder)

        # Escapar datos para prevenir XSS
        direccion_safe = html.escape(str(finca.get('direccion', 'Finca sin dirección')))
        superficie_safe = html.escape(str(finca.get('superficie_m2', 0)))
        pvp_safe = html.escape(str(finca.get('pvp', '—')))
        
        # Para el ID, usar json.dumps para escape completo en contexto JavaScript
        finca_id = str(finca.get('id', ''))
        finca_id_js = json.dumps(finca_id)[1:-1]  # Quitar comillas externas de JSON
        
        # Para img_src, validar que sea data URL de imagen válida o escapar si es URL externa
        if img_src.startswith('data:image/'):
            img_src_safe = img_src  # Data URLs de imagen son seguras
        else:
            img_src_safe = html.escape(img_src)
        
        # Popup con información y botón que fuerza la navegación en la ventana superior
        popup_html = f"""
        <div style="width: 220px; font-family: Arial, sans-serif;">
          <h4 style="margin: 0 0 8px 0; font-size:14px;">{direccion_safe}</h4>
          <img src="{img_src_safe}" width="140" height="90" style="border-radius: 4px; margin-bottom: 8px;"><br/>
          <p style="margin: 4px 0; font-size:13px;"><strong>Superficie:</strong> {superficie_safe} m²</p>
          <p style="margin: 4px 0; font-size:13px;"><strong>PVP:</strong> €{pvp_safe}</p>
                    <a href="javascript:void(0)" 
                       onclick="window.parent.location.href='?modal=1&fid={finca_id_js}';"
                       style="display:block;background:#d9534f;color:#fff;padding:6px 8px;border-radius:4px;width:100%;text-align:center;margin-top:6px;font-weight:600;text-decoration:none;cursor:pointer;">
                        Ver detalles
                    </a>
        </div>
        """

        # Crear popup directo (sin IFrame) - renderiza HTML correctamente
        popup = folium.Popup(popup_html, max_width=260)

        marker = folium.Marker(
            location=[lat, lng],
            popup=popup,
            tooltip='Haz clic aquí para ver más',
            icon=folium.Icon(color=color)
        )
        marker.add_to(mapa)

    # Mostrar mapa con captura de eventos (capturamos también 'last_object_clicked')
    map_data = st_folium(mapa, width=800, height=600, returned_objects=["last_clicked", "last_object_clicked"])

    # Manejar clic en marcador para mostrar card/modal
    clicked_obj = None
    if map_data:
        clicked_obj = map_data.get("last_object_clicked") or map_data.get("last_clicked")

    if clicked_obj:
        # 'last_object_clicked' y 'last_clicked' suelen exponer 'lat'/'lng'
        clicked_lat = clicked_obj.get("lat")
        clicked_lng = clicked_obj.get("lng")

        if clicked_lat is not None and clicked_lng is not None:
            # Encontrar finca por coordenadas (aproximado)
            for finca in fincas:
                finca_lat = finca.get('ubicacion_geo', {}).get('lat', 0)
                finca_lng = finca.get('ubicacion_geo', {}).get('lng', 0)
                if abs(finca_lat - clicked_lat) < 0.001 and abs(finca_lng - clicked_lng) < 0.001:
                    # Store clicked finca and show a small card (first step)
                    st.session_state.finca_id = str(finca.get('id'))
                    st.session_state['clicked_fid'] = str(finca.get('id'))
                    st.session_state['show_small_card'] = True
                    break

    # Estadísticas
    st.markdown("---")
    st.subheader("📊 Estadísticas de Fincas")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Fincas", len(fincas))

    with col2:
        superficie_total = sum(f.get('superficie_m2', 0) for f in fincas)
        st.metric("Superficie Total", f"{superficie_total:,.0f} m2")

    with col3:
        superficie_promedio = superficie_total / len(fincas) if fincas else 0
        st.metric("Superficie Promedio", f"{superficie_promedio:,.0f} m2")

    with col4:
        disponibles = sum(1 for f in fincas if f.get('estado') == 'disponible')
        st.metric("Disponibles", disponibles)

# ==========================================
# REGISTRO DE ARQUITECTOS
# ==========================================

def render_registro_arquitectos():
    st.header("👥 Registro de Arquitectos y Clientes")

    tab1, tab2 = st.tabs(["👨‍💼 Registrar Arquitecto", "🏠 Registrar Cliente"])

    with tab1:
        st.subheader("Registro de Arquitecto")

        with st.form("registro_arquitecto"):
            nombre = st.text_input("Nombre completo")
            email_arq = st.text_input("Email profesional")
            especialidad = st.selectbox("Especialidad", ["Arquitectura Residencial", "Arquitectura Comercial", "Urbanismo", "Restauración", "Interiorismo"])
            experiencia = st.slider("Años de experiencia", 0, 50, 5)
            ubicacion = st.text_input("Ubicación")
            descripcion = st.text_area("Descripción profesional")

            if st.form_submit_button("📝 Registrar Arquitecto", type="primary"):
                # Simular registro
                arquitecto_data = {
                    "id": f"arq_{len(st.session_state.get('arquitectos', [])) + 1}",
                    "nombre": nombre,
                    "email": email_arq,
                    "especialidad": especialidad,
                    "experiencia": experiencia,
                    "ubicacion": ubicacion,
                    "descripcion": descripcion,
                    "fecha_registro": datetime.now().isoformat()
                }

                if "arquitectos" not in st.session_state:
                    st.session_state.arquitectos = []
                st.session_state.arquitectos.append(arquitecto_data)

                st.success(f"✅ Arquitecto {nombre} registrado exitosamente!")
                st.balloons()

    with tab2:
        st.subheader("Registro de Cliente")

        with st.form("registro_cliente"):
            nombre_cliente = st.text_input("Nombre completo")
            email_cliente = st.text_input("Email")
            tipo_cliente = st.selectbox("Tipo de cliente", ["Particular", "Empresa", "Inversor"])
            presupuesto = st.number_input("Presupuesto aproximado (€)", min_value=0, step=10000)
            ubicacion_deseada = st.text_input("Ubicación deseada")
            necesidades = st.text_area("Necesidades específicas")

            if st.form_submit_button("📝 Registrar Cliente", type="primary"):
                # Simular registro
                cliente_data = {
                    "id": f"cli_{len(st.session_state.get('clientes', [])) + 1}",
                    "nombre": nombre_cliente,
                    "email": email_cliente,
                    "tipo": tipo_cliente,
                    "presupuesto": presupuesto,
                    "ubicacion_deseada": ubicacion_deseada,
                    "necesidades": necesidades,
                    "fecha_registro": datetime.now().isoformat()
                }

                if "clientes" not in st.session_state:
                    st.session_state.clientes = []
                st.session_state.clientes.append(cliente_data)

                st.success(f"✅ Cliente {nombre_cliente} registrado exitosamente!")
                st.balloons()

    # Mostrar registros existentes
    st.markdown("---")
    st.subheader("📋 Registros Recientes")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**👨‍💼 Arquitectos Registrados:**")
        arquitectos = st.session_state.get('arquitectos', [])
        if arquitectos:
            for arq in arquitectos[-3:]:  # Últimos 3
                st.markdown(f"- {arq['nombre']} ({arq['especialidad']})")
        else:
            st.info("No hay arquitectos registrados aún")

    with col2:
        st.markdown("**🏠 Clientes Registrados:**")
        clientes = st.session_state.get('clientes', [])
        if clientes:
            for cli in clientes[-3:]:  # Últimos 3
                st.markdown(f"- {cli['nombre']} ({cli['tipo']})")
        else:
            st.info("No hay clientes registrados aún")

# ==========================================
# INTRANET ARQUITECTOS
# ==========================================

def render_intranet_arquitectos():
    st.header("🏢 Intranet Arquitectos ARCHIRAPID")

    # Verificar si el usuario es arquitecto
    email = st.session_state.get("email")
    if not email or "@" not in email:
        st.warning("Debes iniciar sesión con un email válido para acceder a la intranet.")
        return

    st.markdown("### 🏗️ Panel de Control Arquitecto")

    # Métricas rápidas
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        proyectos_total = len(st.session_state.get('proyectos', []))
        st.metric("Mis Proyectos", proyectos_total)

    with col2:
        clientes_total = len(st.session_state.get('clientes', []))
        st.metric("Mis Clientes", clientes_total)

    with col3:
        # Simular proyectos activos
        proyectos_activos = sum(1 for p in st.session_state.get('proyectos', []) if p.get('estado') != 'completado')
        st.metric("Proyectos Activos", proyectos_activos)

    with col4:
        # Simular ingresos mensuales
        ingresos = sum(p.get('precio_estimado', 0) for p in st.session_state.get('proyectos', []) if p.get('estado') == 'completado')
        st.metric("Ingresos Totales", f"€{ingresos:,.0f}")

    # Herramientas del arquitecto
    st.markdown("---")
    st.subheader("🛠️ Herramientas Profesionales")

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "👥 Mis Clientes", "📋 Proyectos"])

    with tab1:
        st.markdown("### 📊 Dashboard de Rendimiento")

        # Gráfico simple de proyectos por estado
        import matplotlib.pyplot as plt

        proyectos = st.session_state.get('proyectos', [])
        estados = {}
        for p in proyectos:
            estado = p.get('estado', 'borrador')
            estados[estado] = estados.get(estado, 0) + 1

        if estados:
            fig, ax = plt.subplots()
            ax.bar(estados.keys(), estados.values())
            ax.set_ylabel('Número de Proyectos')
            ax.set_title('Proyectos por Estado')
            st.pyplot(fig)
        else:
            st.info("No hay proyectos para mostrar estadísticas")

    with tab2:
        st.markdown("### 👥 Gestión de Clientes")

        clientes = st.session_state.get('clientes', [])
        if clientes:
            for cliente in clientes:
                with st.expander(f"🏠 {cliente['nombre']} - {cliente['tipo']}"):
                    st.write(f"**Email:** {cliente['email']}")
                    st.write(f"**Presupuesto:** €{cliente['presupuesto']:,.0f}")
                    st.write(f"**Ubicación deseada:** {cliente['ubicacion_deseada']}")
                    st.write(f"**Necesidades:** {cliente['necesidades']}")

                    if st.button(f"📞 Contactar", key=f"contact_{cliente['id']}"):
                        st.info(f"Simulando contacto con {cliente['nombre']}...")
        else:
            st.info("No tienes clientes registrados aún")

    with tab3:
        st.markdown("### 📋 Gestión de Proyectos")

        proyectos = st.session_state.get('proyectos', [])
        if proyectos:
            for proyecto in proyectos:
                with st.expander(f"🏗️ {proyecto.get('titulo', 'Proyecto sin título')}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Estado", proyecto.get('estado', 'borrador').title())
                        st.metric("Versión", proyecto.get('version', 1))
                    with col2:
                        precio = proyecto.get('precio_estimado', 0)
                        st.metric("Precio Estimado", f"€{precio:,.0f}")

                    if st.button(f"✏️ Editar Proyecto", key=f"edit_proy_{proyecto['id']}"):
                        st.session_state.plan_actual = proyecto.get("plan_json", {})
                        st.session_state.pantalla_actual = "diseno_ia"
                        st.rerun()
        else:
            st.info("No tienes proyectos aún")

# ==========================================
# GEMELo DIGITAL
# ==========================================

def render_gemelo_digital():
    st.header("🧠 Gemelo Digital ARCHIRAPID")

    st.markdown("""
    ### 🚀 Tecnología de Vanguardia

    El **Gemelo Digital** de ARCHIRAPID es una representación virtual tridimensional
    de tu proyecto arquitectónico que te permite:

    - **Visualizar** la vivienda terminada antes de construir
    - **Interactuar** con el diseño en tiempo real
    - **Simular** iluminación, materiales y acabados
    - **Compartir** el proyecto con clientes de forma inmersiva
    """)

    # Estado del desarrollo
    st.info("🛠️ El Gemelo Digital está en desarrollo activo. Próximamente disponible.")

    # Preview conceptual
    st.subheader("🎯 Vista Previa Conceptual")

    # Simular una imagen 3D (placeholder)
    st.markdown("""
    ```
    [Vista 3D Interactiva - Próximamente]

         _____
       /     \\
      /  🏠   \\
     /_________\\
    |           |
    |   🪟 🪟    |
    |           |
    |   🚪      |
    |___________|
    ```
    """)

    # Características
    st.subheader("✨ Características del Gemelo Digital")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **🎨 Personalización Visual:**
        - Cambiar colores de paredes
        - Probar diferentes materiales
        - Ajustar iluminación

        **📐 Medidas Precisas:**
        - Dimensiones exactas
        - Áreas calculadas
        - Volúmenes 3D
        """)

    with col2:
        st.markdown("""
        **🌅 Simulación Ambiental:**
        - Orientación solar
        - Sombras proyectadas
        - Eficiencia energética

        **📱 Acceso Multiplataforma:**
        - Web y móvil
        - VR compatible
        - Compartir con un link
        """)

    # Call to action
    st.markdown("---")
    if st.button("🚀 Solicitar Acceso Anticipado", type="primary"):
        st.success("✅ ¡Gracias! Te notificaremos cuando el Gemelo Digital esté disponible.")
        st.balloons()

# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================

if __name__ == "__main__":
    main()
