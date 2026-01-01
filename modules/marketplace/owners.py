# modules/marketplace/owners.py
import streamlit as st
from modules.marketplace.utils import save_upload, create_plot_record, get_user_by_email, update_proposal_status
from src import db
import uuid
import json
import geopy.geocoders
from time import sleep
from datetime import datetime
import os


def obtener_coordenadas_gps(municipio, provincia="Madrid"):
    """
    Obtiene coordenadas GPS (lat, lon) de un municipio usando geopy.
    Si falla, devuelve coordenadas por defecto del centro del municipio.
    """
    try:
        # Usar Nominatim (OpenStreetMap) para geocodificación
        geolocator = geopy.geocoders.Nominatim(user_agent="archi_rapid_app")

        # Buscar por municipio + provincia
        location_query = f"{municipio}, {provincia}, Spain"
        location = geolocator.geocode(location_query, timeout=10)

        if location:
            return location.latitude, location.longitude
        else:
            # Si no encuentra, intentar solo con el municipio
            location = geolocator.geocode(f"{municipio}, Spain", timeout=10)
            if location:
                return location.latitude, location.longitude

    except Exception as e:
        st.warning(f"⚠️ No se pudieron obtener coordenadas GPS automáticas: {str(e)}")

    # Coordenadas por defecto para municipios comunes de Madrid
    coordenadas_default = {
        "Madrid": (40.4168, -3.7038),
        "Alcalá de Henares": (40.4821, -3.3599),
        "Alcobendas": (40.5475, -3.6424),
        "Alcorcón": (40.3458, -3.8249),
        "Algete": (40.5971, -3.4974),
        "Aranjuez": (40.0311, -3.6025),
        "Arganda del Rey": (40.3008, -3.4382),
        "Boadilla del Monte": (40.4050, -3.8783),
        "Collado Villalba": (40.6341, -4.0053),
        "Colmenar Viejo": (40.6590, -3.7676),
        "Coslada": (40.4238, -3.5613),
        "Fuenlabrada": (40.2842, -3.7942),
        "Galapagar": (40.5789, -3.9616),
        "Getafe": (40.3083, -3.7329),
        "Leganés": (40.3272, -3.7635),
        "Majadahonda": (40.4735, -3.8718),
        "Móstoles": (40.3223, -3.8645),
        "Parla": (40.2360, -3.7675),
        "Pinto": (40.2415, -3.6999),
        "Pozuelo de Alarcón": (40.4379, -3.8134),
        "Rivas-Vaciamadrid": (40.3260, -3.5181),
        "San Sebastián de los Reyes": (40.5448, -3.6268),
        "Torrejón de Ardoz": (40.4586, -3.4783),
        "Tres Cantos": (40.6091, -3.7144),
        "Valdemoro": (40.1889, -3.6787),
        "Villaviciosa de Odón": (40.3572, -3.9001)
    }

    # Buscar municipio en coordenadas por defecto
    municipio_lower = municipio.lower().strip()
    for mun, coords in coordenadas_default.items():
        if mun.lower() in municipio_lower or municipio_lower in mun.lower():
            return coords

    # Si no encuentra nada, usar Madrid centro como fallback
    st.info("📍 Usando coordenadas por defecto de Madrid centro")
    return 40.4168, -3.7038  # Madrid centro


def guardar_datos_catastrales(data_extracted, pdf_path):
    """
    Guarda los datos catastrales extraídos por Gemini en la base de datos.
    Si la referencia catastral ya existe, actualiza el registro.
    """
    try:
        # Verificar que tenemos la referencia catastral (campo obligatorio)
        referencia = data_extracted.get("referencia_catastral")
        if not referencia:
            st.warning("⚠️ No se pudo guardar: falta referencia catastral")
            return False

        # Preparar datos para insertar en la tabla plots
        plot_data = {
            "id": referencia,  # Usar referencia catastral como ID único
            "catastral_ref": referencia,
            "m2": data_extracted.get("superficie_grafica_m2"),
            "locality": data_extracted.get("municipio"),
            "province": "Madrid",  # Default Madrid
            "plano_catastral_path": pdf_path,  # Guardar ruta del PDF
            "type": "plot",  # Tipo de propiedad
            "status": "draft",  # Estado inicial
            "created_at": datetime.utcnow().isoformat(),
            "title": f"Parcela {referencia}",
            "description": f"Parcela catastral {referencia} - {data_extracted.get('municipio', 'Sin municipio')}",
            # Campos opcionales con valores por defecto
            "price": 0,
            "height": None,
            "owner_name": st.session_state.get("owner_name", ""),
            "owner_email": st.session_state.get("owner_email", ""),
            "owner_phone": st.session_state.get("owner_phone", ""),
        }

        # Obtener coordenadas GPS del municipio
        municipio = data_extracted.get("municipio", "")
        if municipio:
            lat, lon = obtener_coordenadas_gps(municipio, "Madrid")
            plot_data["lat"] = lat
            plot_data["lon"] = lon
            st.info(f"📍 Coordenadas GPS obtenidas: {lat:.4f}, {lon:.4f}")
        else:
            # Coordenadas por defecto si no hay municipio
            plot_data["lat"] = 40.4168  # Madrid centro
            plot_data["lon"] = -3.7038
            st.warning("⚠️ No se detectó municipio, usando coordenadas por defecto de Madrid")

        # Insertar/actualizar en la base de datos
        db.insert_plot(plot_data)

        st.success(f"✅ Datos guardados correctamente en BD (Referencia: {referencia})")
        return True

    except Exception as e:
        st.error(f"❌ Error guardando en base de datos: {str(e)}")
        return False


def main():
    st.header("Panel de Propietarios — Venta de Suelo")

    # --- 1. LOGIN / IDENTIFICACIÓN ---
    if "owner_id" not in st.session_state:
        st.info("Para empezar, identifícate como propietario.")
        
        col_a, col_b = st.columns(2)
        with col_a:
            email = st.text_input("Tu email *", placeholder="ejemplo@correo.com")
            name = st.text_input("Nombre completo *", placeholder="Juan Pérez")
        with col_b:
            phone = st.text_input("Teléfono *", placeholder="+34 600 000 000")
            address = st.text_input("Dirección completa *", placeholder="Calle, CP, Ciudad, Provincia")
        
        submitted = st.button("Acceder / Registrarse", type="primary")
        
        if submitted:
            if not email or not name or not phone or not address:
                st.error("Por favor completa todos los campos obligatorios (*)")
            else:
                # Lógica simple de "Auth sin password" para MVP
                user_data = get_user_by_email(email)
                if user_data:
                    st.success(f"Bienvenido de nuevo, {user_data['name']}")
                    st.session_state["owner_id"] = user_data["id"]
                    st.session_state["owner_email"] = user_data["email"]
                    st.session_state["owner_name"] = user_data["name"]
                    st.session_state["owner_phone"] = user_data.get("phone", phone)
                    st.session_state["owner_address"] = user_data.get("address", address)
                else:
                    new_id = uuid.uuid4().hex
                    from modules.marketplace.utils import insert_user
                    insert_user({
                        "id": new_id, 
                        "name": name, 
                        "email": email, 
                        "role": "owner", 
                        "company": "",
                        "phone": phone,
                        "address": address
                    })
                    st.success("Cuenta creada. Bienvenido.")
                    st.session_state["owner_id"] = new_id
                    st.session_state["owner_email"] = email
                    st.session_state["owner_name"] = name
                    st.session_state["owner_phone"] = phone
                    st.session_state["owner_address"] = address
                sleep(1)
                st.rerun()
        return

    # --- 2. LOGGED IN VIEW ---
    st.write(f"Conectado como: **{st.session_state.owner_name}** ({st.session_state.owner_email})")
    
    # Navegación interna del módulo (si se llama desde `app.py` directamente)
    tab_subir, tab_mis_fincas = st.tabs(["➕ Subir Nueva Finca", "📋 Mis Fincas y Propuestas"])

    with tab_subir:
        st.markdown("### 📝 Datos de la Nueva Finca")
        st.info("Solo aceptamos fincas **Urbanas** o **Industriales**. Fincas rústicas no son admitidas en esta plataforma.")


        # Remove form wrapper to allow interactive AI buttons
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Título del Anuncio", placeholder="Ej: Parcela en zona residencial...")
            date_address = st.text_input("Dirección Exacta (Calle, Número, Ciudad, CP)", placeholder="Para ubicar en el mapa")
            surface = st.number_input("Superficie Total (m²)", min_value=50.0, step=10.0)
            finca_type = st.selectbox("Tipo de Suelo", ["Urbana", "Industrial", "Rústica (No admitida)"])
        
        with col2:
            price = st.number_input("Precio de Venta deseado (€)", min_value=1000.0, step=500.0)
            st.caption(f"ℹ️ Nuestra comisión: 7% - 10%.")
            services = st.multiselect("Servicios Disponibles", ["Agua", "Luz", "Alcantarillado", "Gas", "Fibra Óptica"])
            
            # AI Description Generator
            if st.button("✨ Generar Descripción con IA"):
                if not finca_type or not title:
                    st.warning("Completa tipo y título para generar la descripción.")
                else:
                    with st.spinner("Redactando anuncio..."):
                        from modules.marketplace import ai_engine
                        prompt = f"Redacta una descripción atractiva para vender una finca {finca_type} de {surface} m2 en {date_address}. Título: {title}. Servicios: {', '.join(services)}."
                        desc_ia = ai_engine.generate_text(prompt)
                        st.session_state["desc_ia_cache"] = desc_ia

        description_val = st.session_state.get("desc_ia_cache", f"Dirección: {date_address}. Servicios: {', '.join(services)}")
        description = st.text_area("Descripción (Editable)", value=description_val, height=100)
            
        st.markdown("---")
        st.markdown("### 📂 Documentación y Fotos")
        st.info("💡 Consejo: Sube una foto o captura de la Nota Simple y la IA extraerá los datos automáticamente.")
        uploaded_nota = st.file_uploader("Nota Simple / Catasteral (Imagen/PDF)", type=["png", "jpg", "jpeg", "pdf"])
        
        if uploaded_nota and st.button("👁️ Extraer Datos de Nota Simple (IA)"):
            with st.spinner("Analizando documento con Gemini Vision..."):
                try:
                    from modules.marketplace.ai_engine import extraer_datos_catastral
                    import tempfile
                    import os

                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_nota.getvalue())
                        tmp_path = tmp_file.name

                    try:
                        # Llamar a la función de extracción de ai_engine
                        resultado = extraer_datos_catastral(tmp_path)

                        # Verificar si hay error
                        if isinstance(resultado, dict) and "error" in resultado:
                            error_msg = resultado["error"]
                            if "agotado la cuota" in error_msg or "429" in error_msg:
                                st.warning("😴 La IA está descansando, espera 30 segundos")
                                st.info("💡 La cuota de la API se resetea automáticamente cada hora.")
                            else:
                                st.error(f"❌ Error: {error_msg}")
                        else:
                            # Datos extraídos correctamente
                            st.success("✅ Datos extraídos correctamente del documento.")

                            # Mostrar datos extraídos en pantalla
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.markdown("**📋 Datos Catastrales Extraídos:**")
                                st.markdown(f"**Referencia Catastral:** {resultado.get('referencia_catastral', 'No detectada')}")
                                st.markdown(f"**Superficie Gráfica:** {resultado.get('superficie_grafica_m2', 'No detectada')} m²")
                                st.markdown(f"**Municipio:** {resultado.get('municipio', 'No detectado')}")

                            with col_b:
                                st.markdown("**💾 Preparado para guardar:**")
                                st.info("Los datos están listos para guardarse en la base de datos database.db")
                                if st.button("💾 Guardar en Base de Datos"):
                                    # Preparar datos para guardar
                                    guardar_datos_catastrales(resultado, tmp_path)
                                    st.success("✅ Datos guardados correctamente en la base de datos!")

                            # Guardar en session state para autocompletar
                            if resultado.get("referencia_catastral"):
                                st.session_state["auto_ref"] = resultado["referencia_catastral"]
                            if resultado.get("superficie_grafica_m2"):
                                st.session_state["auto_m2"] = resultado["superficie_grafica_m2"]
                            if resultado.get("municipio"):
                                st.session_state["auto_municipio"] = resultado["municipio"]

                    finally:
                        # Clean up temporary file
                        if 'tmp_path' in locals():
                            try:
                                os.unlink(tmp_path)
                            except:
                                pass
                except Exception as e:
                    st.error(f"❌ Error procesando documento: {e}")

        # Usar valores autocompletados
        def_ref = st.session_state.get("auto_ref", "")
        catastral_ref = st.text_input("Referencia Catastral", value=def_ref, help="Clave para ubicar la parcela exacta.")
        
        # Optional coordinates
        col_coord1, col_coord2 = st.columns(2)
        with col_coord1:
            manual_lat = st.number_input("Latitud (Opcional)", value=st.session_state.get("auto_lat", 0.0), format="%.6f", help="Déjalo en 0 para usar geocodificación automática")
        with col_coord2:
            manual_lon = st.number_input("Longitud (Opcional)", value=st.session_state.get("auto_lon", 0.0), format="%.6f", help="Déjalo en 0 para usar geocodificación automática")
        
        # Catastro validation button - Mejorado para validar por dirección o referencia
        col_val1, col_val2 = st.columns(2)
        with col_val1:
            if st.button("🔍 Validar Dirección (Geocodificación)"):
                if date_address:
                    with st.spinner("Geocodificando dirección..."):
                        try:
                            from geopy.geocoders import Nominatim
                            geolocator = Nominatim(user_agent="archirapid_mvp", timeout=10)
                            # Intentar con formato completo: dirección, municipio, provincia, España
                            search_address = f"{date_address}, {st.session_state.get('auto_provincia', 'Málaga')}, España"
                            loc = geolocator.geocode(search_address)
                            if loc:
                                st.session_state["auto_lat"] = loc.latitude
                                st.session_state["auto_lon"] = loc.longitude
                                st.success(f"✅ Ubicación encontrada: {loc.latitude:.6f}, {loc.longitude:.6f}")
                                st.info(f"📍 {loc.address}")
                                st.rerun()
                            else:
                                st.warning("⚠️ No se pudo geocodificar la dirección. Intenta ser más específico (incluye ciudad/provincia).")
                        except Exception as e:
                            st.error(f"Error en geocodificación: {str(e)}")
                else:
                    st.warning("⚠️ Ingresa primero la dirección de la finca")
        
        with col_val2:
            if catastral_ref and st.button("🔍 Validar Referencia Catastral"):
                with st.spinner("Consultando Catastro oficial..."):
                    from modules.marketplace import catastro_api
                    cat_data = catastro_api.fetch_by_ref_catastral(catastral_ref)
                    if cat_data and cat_data.get("estado") == "validado_oficial":
                        st.success(f"✅ Validado: {cat_data['ubicacion_geo']['direccion_completa']}")
                        st.session_state["auto_lat"] = cat_data['ubicacion_geo']['lat']
                        st.session_state["auto_lon"] = cat_data['ubicacion_geo']['lng']
                        st.rerun()
                    else:
                        st.warning("⚠️ No se pudo validar en Catastro. Verifica la referencia.")
        
        uploaded_photos = st.file_uploader("Fotos del terreno", accept_multiple_files=True, type=['jpg','png'])

        submitted_finca = st.button("📢 PUBLICAR FINCA", type="primary")

        if submitted_finca:
            if finca_type == "Rústica (No admitida)":
                st.error("⛔ Lo sentimos, ARCHIRAPID no opera con suelo rústico. Solo Urbano o Industrial.")
            elif not title or not date_address or surface <= 0 or price <= 0:
                st.error("Por favor completa todos los campos obligatorios.")
            elif not uploaded_nota:
                st.error("La Nota Simple es obligatoria para verificar la propiedad.")
            else:
                # Procesar Geo - SIEMPRE generar coordenadas (PRIORIDAD: session_state > manual > geocodificación > fallback)
                lat, lon = None, None
                
                # PRIORIDAD 1: Usar coordenadas de session_state (validadas previamente)
                if st.session_state.get("auto_lat") and st.session_state.get("auto_lon"):
                    lat = float(st.session_state["auto_lat"])
                    lon = float(st.session_state["auto_lon"])
                    st.info(f"📍 Usando coordenadas validadas: {lat:.6f}, {lon:.6f}")
                # PRIORIDAD 2: Usar coordenadas manuales si se proporcionaron
                elif manual_lat != 0.0 and manual_lon != 0.0:
                    lat, lon = float(manual_lat), float(manual_lon)
                    st.info(f"📍 Usando coordenadas manuales: {lat:.6f}, {lon:.6f}")
                # PRIORIDAD 3: Geocode from address - INTENTAR MÚLTIPLES MÉTODOS
                else:
                    geocoded = False
                    
                    # Método 1: Geopy Nominatim con dirección completa
                    try:
                        from geopy.geocoders import Nominatim
                        geolocator = Nominatim(user_agent="archirapid_mvp", timeout=10)
                        # Construir dirección completa: dirección, provincia, España
                        provincia_name = st.session_state.get("auto_provincia", "Málaga")
                        search_address = f"{date_address}, {provincia_name}, España"
                        loc = geolocator.geocode(search_address)
                        if loc:
                            lat, lon = loc.latitude, loc.longitude
                            geocoded = True
                            st.success(f"✅ Ubicación encontrada por geocodificación: {lat:.6f}, {lon:.6f}")
                            st.caption(f"📍 {loc.address}")
                            # Guardar en session_state para futuras referencias
                            st.session_state["auto_lat"] = lat
                            st.session_state["auto_lon"] = lon
                    except Exception as e:
                        st.warning(f"Método 1 (Geocodificación) falló: {str(e)}")
                    
                    # Método 2: Si falla, intentar con referencia catastral
                    if not geocoded and catastral_ref:
                        try:
                            from modules.marketplace import catastro_api
                            cat_data = catastro_api.fetch_by_ref_catastral(catastral_ref)
                            if cat_data and cat_data.get("ubicacion_geo"):
                                lat = cat_data['ubicacion_geo'].get('lat')
                                lon = cat_data['ubicacion_geo'].get('lng')
                                if lat and lon:
                                    geocoded = True
                                    st.success(f"✅ Coordenadas desde Catastro: {lat:.6f}, {lon:.6f}")
                                    # Guardar en session_state
                                    st.session_state["auto_lat"] = lat
                                    st.session_state["auto_lon"] = lon
                        except Exception as e:
                            st.warning(f"Método 2 (Catastro) falló: {str(e)}")
                    
                    # Método 3: Fallback a ubicación genérica de la provincia (no Madrid genérico)
                    if not geocoded:
                        provincia_name = st.session_state.get("auto_provincia", "Málaga")
                        # Coordenadas aproximadas del centro de algunas provincias españolas comunes
                        centro_provincias = {
                            "Málaga": (36.7213, -4.4214),
                            "Madrid": (40.4168, -3.7038),
                            "Barcelona": (41.3851, 2.1734),
                            "Valencia": (39.4699, -0.3763),
                            "Sevilla": (37.3891, -5.9845),
                            "Bilbao": (43.2627, -2.9253)
                        }
                        fallback_coords = centro_provincias.get(provincia_name, (40.4168, -3.7038))
                        lat, lon = fallback_coords
                        st.warning(f"⚠️ No se pudo geocodificar la dirección. Usando coordenadas aproximadas del centro de {provincia_name}. Por favor, valida y corrige manualmente.")


                # Guardar archivos
                pdf_path = save_upload(uploaded_nota, prefix="nota")
                photo_paths = []
                if uploaded_photos:
                    for p in uploaded_photos[:5]: # Max 5
                        photo_paths.append(save_upload(p, prefix="finca"))
                
                # Generar ID y Comision
                commission_val = price * 0.07 # 7% base
                
                # Convertir photo_paths a JSON string
                import json as json_module
                photo_paths_json = json_module.dumps(photo_paths) if photo_paths else "[]"
                
                plot_data = {
                    "id": uuid.uuid4().hex,
                    "owner_id": st.session_state["owner_id"],
                    "owner_email": st.session_state["owner_email"],
                    "owner_name": st.session_state["owner_name"],
                    "owner_phone": st.session_state.get("owner_phone", ""),
                    "owner_address": st.session_state.get("owner_address", ""),
                    "title": title,
                    "description": description,
                    "address": date_address,
                    "lat": lat, 
                    "lon": lon,
                    "m2": surface,
                    "price": price,
                    "type": finca_type,
                    "catastral_ref": catastral_ref,
                    "services": ",".join(services) if services else "",
                    "image_path": photo_paths[0] if photo_paths else None,
                    "photo_paths": photo_paths_json,
                    "registry_note_path": pdf_path,
                    "plano_catastral_path": pdf_path,  # El mismo archivo PDF como plano catastral
                    "vertices_coordenadas": st.session_state.get("auto_vertices"),
                    "numero_parcela_principal": st.session_state.get("auto_parcela_principal"),
                    "created_at": str(datetime.now())
                }
                
                create_plot_record(plot_data)
                st.success(f"✅ Finca Publicada. Precio: {price}€ (Comisión est.: {commission_val}€). Disponible en mapa y gestión.")
                
                # Redirección manual a "Mis Fincas" (cambiando estado para que al recargar se vea)
                st.session_state['current_page'] = 'mis_fincas'
                sleep(1.5)
                st.rerun()

    with tab_mis_fincas:
        st.subheader("📋 Mis Propiedades")
        
        my_plots = db.get_plots_by_owner(st.session_state["owner_email"])
        
        if not my_plots.empty:
            # Mostrar tabla interactiva
            st.dataframe(
                my_plots[['title', 'price', 'm2', 'type', 'status', 'created_at']],
                use_container_width=True,
                hide_index=True
            )
            
            # Tarjetas de detalle
            for idx, row in my_plots.iterrows():
                with st.expander(f"🏡 {row['title']} ({row['status']})"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Precio:** {row['price']}€")
                        st.write(f"**Superficie:** {row['m2']} m²")
                        st.write(f"**Tipo:** {row['type']}")
                    with c2:
                        st.write(f"**Fecha:** {row['created_at']}")
                        if row.get('registry_note_path'):
                            st.download_button(f"📄 Descargar Nota - {row['title']}", "Nota dummy content", file_name="nota_simple.pdf", key=f"download_nota_{row['id']}_{row['title'].replace(' ', '_')}")
                    
                    # Acciones adicionales
                    c_act1, c_act2 = st.columns(2)
                    with c_act1:
                       if st.button(f"🗑️ Eliminar Finca '{row['title']}'", key=f"del_{row['id']}"):
                           # db.delete_plot(p['id']) # TODO: Implementar delete real
                           st.warning("Funcionalidad de borrado pendiente.")
                    with c_act2:
                        if st.button(f"🔮 Simular Proyecto (Gemelo Digital)", key=f"sim_{row['id']}"):
                             st.session_state["page"] = "gemelo_digital" # Switch page logic (mock)
                             st.info("Para este MVP, accede al menú lateral 'Gemelo Digital' y selecciona esta finca.")
        else:
            st.info("No tienes fincas publicadas todavía. Ve a la pestaña 'Subir Nueva Finca'.")

        
        st.subheader("📨 Propuestas de Arquitectos / Compradores")
        proposals = db.get_proposals_for_owner(st.session_state["owner_email"])
        
        if proposals:
            for p in proposals:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**Arquitecto:** {p['architect_name']} ({p['architect_company'] or 'Independiente'})")
                        st.markdown(f"**Proyecto:** {p['project_title']}")
                        st.markdown(f"**Mensaje:** _{p['message']}_")
                        st.markdown(f"**Oferta:** {p['price']}€ | **Finca:** {p['plot_title']}")
                        
                        status_color = "orange" if p['status']=='pending' else "green" if p['status']=='accepted' else "red"
                        st.markdown(f"Estado: :{status_color}[{p['status'].upper()}]")

                    with c2:
                        if p['status'] == 'pending':
                            if st.button("✅ Aceptar", key=f"acc_{p['id']}"):
                                update_proposal_status(p['id'], "accepted")
                                st.success("Propuesta aceptada")
                                sleep(1)
                                st.rerun()
                                
                            if st.button("❌ Rechazar", key=f"rej_{p['id']}"):
                                update_proposal_status(p['id'], "rejected")
                                st.warning("Propuesta rechazada")
                                sleep(1)
                                st.rerun()
                        else:
                            st.write("Gestionado.")
        else:
            st.info("No tienes propuestas nuevas.")
