# modules/marketplace/owners.py
import streamlit as st
from modules.marketplace.utils import save_upload, create_plot_record, get_user_by_email, update_proposal_status
from src import db
import uuid
import json
import geopy.geocoders
from time import sleep
from datetime import datetime


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
                    from modules.marketplace import ai_engine
                    
                    # Enhanced prompt to extract plot dimensions from diagrams
                    prompt_vision = """
                    Eres un experto en análisis de documentos catastrales españoles.
                    Analiza CUIDADOSAMENTE este documento (Nota Simple/Certificación Catastral).
                    
                    IMPORTANTE: Si hay un PLANO o CROQUIS de la parcela, extrae las medidas de largo y ancho.
                    
                    Extrae TODOS los datos que encuentres y devuelve ÚNICAMENTE un JSON válido (sin markdown, sin explicaciones):
                    {
                       "referencia_catastral": "código de 20 caracteres",
                       "superficie_m2": número entero,
                       "titular": "nombre del propietario",
                       "clasificacion": "Urbano/Rústico/Industrial",
                       "municipio": "nombre del municipio",
                       "provincia": "nombre de la provincia",
                       "coordenadas_lat": número decimal o null,
                       "coordenadas_lon": número decimal o null,
                       "largo_m": número decimal extraído del plano o null,
                       "ancho_m": número decimal extraído del plano o null,
                       "lindes": {
                          "norte": "descripción",
                          "sur": "descripción",
                          "este": "descripción",
                          "oeste": "descripción"
                       }
                    }
                    
                    Si no encuentras algún dato, pon null (no strings vacíos).
                    RESPONDE SOLO CON EL JSON, SIN TEXTO ADICIONAL.
                    """
                    
                    if uploaded_nota.type == "application/pdf":
                        # For PDFs, convert to images and use Vision API
                        resp = ai_engine.generate_from_pdf(prompt_vision, uploaded_nota.getvalue())
                    else:
                        # For images, use vision directly
                        resp = ai_engine.generate_from_image(prompt_vision, uploaded_nota.getvalue())
                    
                    # Parse JSON
                    import json
                    try:
                        # Clean code blocks
                        clean_json = resp.replace("```json", "").replace("```", "").strip()
                        data_extracted = json.loads(clean_json)
                        
                        st.success("✅ Datos extraídos correctamente del documento.")
                        
                        # Display extracted data in organized columns
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.markdown("**📋 Datos Catastrales:**")
                            st.json({
                                "referencia_catastral": data_extracted.get("referencia_catastral"),
                                "superficie_m2": data_extracted.get("superficie_m2"),
                                "clasificacion": data_extracted.get("clasificacion"),
                                "municipio": data_extracted.get("municipio"),
                                "provincia": data_extracted.get("provincia")
                            })
                        
                        with col_b:
                            st.markdown("**📐 Dimensiones de la Parcela:**")
                            if data_extracted.get("largo_m") or data_extracted.get("ancho_m"):
                                st.success(f"🎯 Largo: {data_extracted.get('largo_m', 'N/A')} m")
                                st.success(f"🎯 Ancho: {data_extracted.get('ancho_m', 'N/A')} m")
                                if data_extracted.get("largo_m") and data_extracted.get("ancho_m"):
                                    area_calc = float(data_extracted["largo_m"]) * float(data_extracted["ancho_m"])
                                    st.info(f"📊 Área calculada: {area_calc:.2f} m²")
                            else:
                                st.warning("⚠️ No se encontraron dimensiones en el plano")
                            
                            if data_extracted.get("lindes"):
                                st.markdown("**🧭 Linderos:**")
                                st.caption(f"N: {data_extracted['lindes'].get('norte', 'N/A')}")
                                st.caption(f"S: {data_extracted['lindes'].get('sur', 'N/A')}")
                                st.caption(f"E: {data_extracted['lindes'].get('este', 'N/A')}")
                                st.caption(f"O: {data_extracted['lindes'].get('oeste', 'N/A')}")
                        
                        # Auto-fill session state variables if found
                        if data_extracted.get("referencia_catastral"):
                            st.session_state["auto_ref"] = data_extracted["referencia_catastral"]
                        if data_extracted.get("superficie_m2"):
                            st.session_state["auto_m2"] = data_extracted["superficie_m2"]
                        if data_extracted.get("coordenadas_lat"):
                            st.session_state["auto_lat"] = data_extracted["coordenadas_lat"]
                        if data_extracted.get("coordenadas_lon"):
                            st.session_state["auto_lon"] = data_extracted["coordenadas_lon"]
                        if data_extracted.get("largo_m"):
                            st.session_state["auto_largo"] = data_extracted["largo_m"]
                        if data_extracted.get("ancho_m"):
                            st.session_state["auto_ancho"] = data_extracted["ancho_m"]
                        if data_extracted.get("provincia"):
                            st.session_state["auto_provincia"] = data_extracted["provincia"]
                        if data_extracted.get("lindes"):
                            st.session_state["auto_lindes"] = data_extracted["lindes"]
                        
                    except Exception as e:
                        st.error(f"No se pudo interpretar el JSON de la IA: {resp}")
                except Exception as e:
                    st.error(f"Error procesando documento: {e}")

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
                            st.download_button("Descargar Nota Registro", "Nota dummy content", file_name="nota_simple.pdf")
                    
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
