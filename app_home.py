import os
import io
import json
import base64
from PIL import Image
from src.query_params import get_query_params, set_query_params, update_query_params, clear_query_params
import streamlit as st
import folium
from streamlit_folium import st_folium

# Define the base path for the application
BASE = os.path.dirname(os.path.abspath(__file__))

def get_image_base64(image_path):
    """Convierte una imagen a base64 para mostrarla en HTML"""
    try:
        with Image.open(image_path) as img:
            # Redimensionar si es necesario
            max_size = (800, 600)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.LANCZOS)
            
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Guardar en buffer y convertir a base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=85)
            return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        st.error(f"Error al procesar la imagen {image_path}: {str(e)}")
        return ""

def show_home():
    """Muestra la página principal con mapa interactivo y panel de detalle."""
    st.title("ARCHIRAPID — Home")
    st.write("Busca fincas en la izquierda y visualízalas en el mapa interactivo. Haz clic en un marcador para abrir el panel detalle a la derecha.")

    # If a plot_id arrived directly to this page (e.g. from a folium popup link using window.top),
    # ensure session_state is set so the right-side preview opens.
    try:
        qp = get_query_params()
        if "plot_id" in qp and qp.get("plot_id"):
            val = qp.get("plot_id")[0] if isinstance(qp.get("plot_id"), (list, tuple)) else qp.get("plot_id")
            if val:
                st.session_state["selected_plot"] = val
                # remove plot_id from URL to keep it clean
                new_q = {k: v for k, v in qp.items() if k != "plot_id"}
                # Use the stable query params API instead of experimental APIs to
                # avoid mixing APIs that raises StreamlitAPIException.
                set_query_params(new_q)
                try:
                    with open(os.path.join(BASE, 'debug_trace.log'), 'a', encoding='utf-8') as fh:
                        fh.write(f"app_home.show_home detected plot_id={val}\n")
                except Exception:
                    pass
                try:
                    print(f"app_home.show_home detected plot_id={val}")
                except Exception:
                    pass
    except Exception:
        pass

    # Layout: filtros (izq) + mapa y panel detalle (der)
    left_col, main_col = st.columns([1, 3])

    # --- LEFT: filtros ---
    with left_col:
        st.header("Filters")
        min_m2 = st.number_input("Min m²", min_value=0, value=0)
        max_m2 = st.number_input("Max m²", min_value=0, value=100000)
        province = st.text_input("Province / Region", value="")
        type_sel = st.selectbox("Type", options=["any", "rural", "urban", "industrial"])
        min_price = st.number_input("Min price (€)", min_value=0, value=0)
        max_price = st.number_input("Max price (€)", min_value=0, value=10000000)
        q = st.text_input("Search text (locality, title...)", "")
        if st.button("Apply filters"):
            st.experimental_rerun()

    # --- MAIN: map + right preview panel ---
    # Cargar datos de fincas.json
    fincas_path = os.path.join(BASE, "fincas.json")
    with open(fincas_path, 'r', encoding='utf-8') as f:
        df_plots = json.load(f)

    # Aplicar filtros
    filtered_plots = []
    for plot in df_plots:
        if (plot['m2'] >= min_m2 and plot['m2'] <= max_m2 and
            plot['price'] >= min_price and plot['price'] <= max_price):
            if province and province.lower() not in plot['province'].lower():
                continue
            if type_sel != "any" and plot['type'] != type_sel:
                continue
            if q and q.lower() not in plot['title'].lower() and q.lower() not in plot['province'].lower():
                continue
            filtered_plots.append(plot)

    # Create map
    m = folium.Map(location=[40.0, -4.0], zoom_start=6, tiles="CartoDB positron")

    # Add markers
    for plot in filtered_plots:
        # Get image if available
        img_html = ""
        if 'images' in plot and plot['images']:
            img_path = os.path.join(BASE, plot['images'][0])
            if os.path.exists(img_path):
                img_b64 = get_image_base64(img_path)
                if img_b64:
                    img_html = f"""
                    <div style='text-align:center;margin-bottom:10px;'>
                        <img src="data:image/jpeg;base64,{img_b64}" 
                             style="width:220px;height:140px;object-fit:cover;
                                    border-radius:10px;box-shadow:0 2px 6px rgba(0,0,0,0.2);" />
                    </div>
                    """

        # Modern popup HTML
        popup_html = f"""
        <div style="width:240px;font-family:'Segoe UI',Roboto,sans-serif;
                    background:#fff;border-radius:12px;padding:12px;
                    text-align:center;box-shadow:0 3px 8px rgba(0,0,0,0.15);">
            {img_html}
            <h4 style='margin:6px 0;font-size:15px;font-weight:600;color:#004080;'>{plot['title']}</h4>
            <div style='font-size:13px;color:#444;margin:4px 0;'>
                <b>{int(plot['m2']):,} m²</b> · €{int(plot['price']):,}
            </div>
            <div style='font-size:12px;color:#666;'>📍 {plot['province']}</div>
            <div style='margin-top:10px;'>
                <a href="#" onclick="window.top.location.href='?plot_id={plot["id"]}'" 
                   style='display:inline-block;
                          background:linear-gradient(135deg,#0066cc,#004080);
                          color:#fff;border-radius:6px;padding:6px 12px;
                          text-decoration:none;font-weight:500;
                          transition:all 0.3s ease;'>
                    🔍 Ver detalles
                </a>
            </div>
        </div>
        """

        # Add marker
        folium.Marker(
            location=[plot['lat'], plot['lon']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=plot['title'],
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

    # Display map and detail panel
    map_col, panel_col = main_col.columns([2, 1])
    
    with map_col:
        st.header("Map (Spain & Portugal)")
        map_data = st_folium(m, width="100%", height=650)

    # Show detail panel if plot is selected
    with panel_col:
        # --- DEBUG INFO (temporary) ---
        st.markdown("**DEBUG**")
        st.write("query_params:", get_query_params())
        st.write("session selected_plot:", st.session_state.get("selected_plot"))
        # show whether df_plots contains the selected id
        selid = st.session_state.get("selected_plot")
        if selid:
            found = next((p for p in df_plots if str(p.get('id')) == str(selid)), None)
            st.write("found in fincas.json:", bool(found))
            if found:
                st.write(found)
        st.markdown("---")
        if "selected_plot" in st.session_state:
            plot_id = st.session_state["selected_plot"]
            # Find plot in data
            selected_plot = next((p for p in df_plots if p['id'] == plot_id), None)
            
            if selected_plot:
                st.markdown(f"### {selected_plot['title']}")
                
                if 'images' in selected_plot and selected_plot['images']:
                    img_path = os.path.join(BASE, selected_plot['images'][0])
                    if os.path.exists(img_path):
                        st.image(img_path, use_column_width="always")
                    else:
                        st.info("Imagen no disponible")

                st.markdown(f"**{selected_plot.get('description', '-')}**")
                st.write(f"**Superficie:** {int(selected_plot['m2']):,} m²")
                st.write(f"**Precio:** €{int(selected_plot['price']):,}")
                st.write(f"**Tipo:** {selected_plot['type']}")
                st.write(f"**Provincia:** {selected_plot['province']}")

                st.markdown("---")
                if st.button("Cerrar vista detalle"):
                    st.session_state.pop("selected_plot", None)
                    st.experimental_rerun()
        else:
            st.info("Selecciona una finca en el mapa para ver sus detalles aquí")

if __name__ == "__main__":
    show_home()