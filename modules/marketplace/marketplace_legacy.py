# ARCHIRAPID - Marketplace Legacy Code
# ===================================
#
# Este archivo contiene código comentado/desactivado temporalmente del marketplace.
# Se mantiene por referencia histórica y futura implementación.
#
# CONTENIDO:
# - Modales de detalles de finca (desactivados por conflicto con múltiples dialogs en Streamlit)
# - Formularios de datos personales para transacciones (desactivados por el mismo motivo)
#
# MOTIVO DE DESACTIVACIÓN:
# Los modales @st.dialog() causaban conflictos cuando se abrían múltiples dialogs
# simultáneamente en Streamlit. Se desactivaron temporalmente hasta encontrar
# una solución que permita múltiples modales sin conflictos.
#
# FUTURA IMPLEMENTACIÓN:
# - Migrar a un sistema de navegación por páginas en lugar de modales
# - Usar st.navigation() o un sistema de routing personalizado
# - Implementar los detalles de finca en páginas separadas
#
# FECHA DE CREACIÓN: $(date)
# ARCHIVO ORIGINAL: marketplace.py

"""
Código legacy del marketplace - MODALES DESACTIVADOS TEMPORALMENTE
Para resolver conflicto de múltiples dialogs en Streamlit

# Detalles de finca seleccionada - MODAL DESACTIVADO TEMPORALMENTE
# Para resolver conflicto de múltiples dialogs en Streamlit
if selected_plot_local and not st.session_state.get("show_client_form", False):
    pid = selected_plot_local
    st.session_state["selected_plot"] = pid  # sync

    # Modal grande horizontal
    @st.dialog("Detalle de Finca Seleccionada", width="large")
    def show_plot_details(plots_data, plot_id):
        try:
            p = next((x for x in plots_data if x["id"]==plot_id), None)
            if p:
                cadastral_data = extract_cadastral_data(p)

                # Layout horizontal con columnas
                col_left, col_right = st.columns([1, 1])

                with col_left:
                    st.subheader("📋 Datos Catastrales")
                    img_path = get_plot_image_path(p)
                    if os.path.exists(img_path):
                        st.image(img_path, width=300, caption=p['title'])
                    else:
                        st.image("assets/fincas/image1.jpg", width=300, caption=p['title'])

                    st.markdown(f"**🏠 Título:** {p['title']}")
                    st.markdown(f"**📏 Superficie:** {cadastral_data.get('surface_m2', p.get('surface_m2', 'N/A'))} m²")
                    st.markdown(f"**🏗️ Máx. Construible:** {cadastral_data.get('buildable_m2', int(p.get('surface_m2', 0) * 0.33))} m²")
                    st.markdown(f"**💰 Precio:** €{p.get('price', 'N/A')}")
                    st.markdown(f"**📋 Ref. Catastral:** {cadastral_data.get('cadastral_ref', p.get('cadastral_ref', 'N/A'))}")
                    st.markdown(f"**📍 Ubicación:** {p.get('lat', 'N/A')}, {p.get('lon', 'N/A')}")

                    if cadastral_data.get('shape'):
                        st.markdown(f"**🔷 Forma:** {cadastral_data['shape']}")
                    if cadastral_data.get('dimensions'):
                        st.markdown(f"**📐 Dimensiones:** {cadastral_data['dimensions']}")

                with col_right:
                    # Acciones generales de la finca
                    st.subheader("🛠️ Acciones")

                    col_res_finca, col_comp_finca = st.columns(2)
                    with col_res_finca:
                        if st.button("💰 Reservar Finca (10%)", key=f"reserve_finca_10_{p['id']}", use_container_width=True, help="Reservar finca con 10% del precio"):
                            amount = (p.get("price") or 0) * 0.10
                            rid = reserve_plot(p['id'], "Cliente Demo", "cliente@demo.com", amount, kind="reservation")
                            st.success(f"✅ Reserva de finca simulada: {rid} — {amount}€")
                            st.session_state["show_client_form"] = True
                            st.session_state["transaction_type"] = "reservation"
                            st.session_state["transaction_id"] = rid
                            st.rerun()
                    with col_comp_finca:
                        if st.button("🏠 Comprar Finca (100%)", key=f"purchase_finca_100_{p['id']}", use_container_width=True, help="Comprar finca completa"):
                            amount = p.get("price") or 0
                            rid = reserve_plot(p['id'], "Cliente Demo", "cliente@demo.com", amount, kind="purchase")
                            st.success(f"✅ Compra de finca simulada: {rid} — {amount}€")
                            st.session_state["show_client_form"] = True
                            st.session_state["transaction_type"] = "purchase"
                            st.session_state["transaction_id"] = rid
                            st.rerun()

                    # Herramientas avanzadas
                    st.markdown("---")
                    col_analizar, col_informe = st.columns(2)
                    with col_analizar:
                        if st.button("🔍 Analizar Nota Castral", key=f"analyze_note_{p['id']}", use_container_width=True, help="Analizar documento catastral"):
                            st.info("🔄 Analizando nota catastral...")
                            # Aquí iría la lógica de análisis de nota
                            st.success("✅ Análisis completado - Datos extraídos de la nota")
                    with col_informe:
                        if st.button("📋 Generar Informe PDF", key=f"generate_report_{p['id']}", use_container_width=True, help="Generar informe completo en PDF"):
                            st.info("🔄 Generando informe PDF...")
                            # Aquí iría la lógica de generación de PDF
                            st.success("✅ Informe PDF generado y descargado")

                    # Edificabilidad
                    if st.button("🏗️ Examinar Edificabilidad", key=f"check_edificability_{p['id']}", use_container_width=True, help="Análisis detallado de edificabilidad"):
                        edificabilidad_detallada = calculate_edificability(cadastral_data.get('surface_m2', p.get('surface_m2', 0)))
                        st.info(f"🏗️ **Análisis de Edificabilidad:**\n\n"
                               f"- Superficie total: {cadastral_data.get('surface_m2', p.get('surface_m2', 0)):.0f} m²\n"
                               f"- Coeficiente de edificabilidad: 33%\n"
                               f"- Área máxima construible: {edificabilidad_detallada:.0f} m²\n"
                               f"- Área disponible: {edificabilidad_detallada:.0f} m²")

                    st.markdown("---")

                    # Proyectos compatibles (Design Matchmaker - Edificabilidad 33%)
                    try:
                        from src import db as _db
                        surface = cadastral_data.get('surface_m2', p.get('surface_m2', 0)) or 0
                        compatible_projects = _db.list_proyectos_compatibles(surface)
                    except Exception as e:
                        compatible_projects = []
                        st.warning(f"Error cargando proyectos compatibles: {e}")

                    st.subheader("🔍 Proyectos Arquitectónicos Compatibles (Edificabilidad 33%)")
                    max_built = int((cadastral_data.get('surface_m2', p.get('surface_m2', 0)) or 0) * 0.33)
                    if compatible_projects:
                        st.info(f"Edificabilidad máxima: {max_built:.0f} m² (33% de superficie)")
                        if st.button("Ver Proyectos", key=f"ver_proyectos_{p['id']}"):
                            st.session_state[f"show_compatible_{p['id']}"] = True
                        if st.session_state.get(f"show_compatible_{p['id']}", False):
                            for proj in compatible_projects:
                                with st.expander(f"🏗️ {proj.get('titulo', 'Sin título')} — {proj.get('m2_construidos', 'N/A')} m² — €{proj.get('presupuesto_ejecucion', 'N/A')}"):
                                    st.markdown(f"**Estilo:** {proj.get('estilo', 'N/A')}")
                                    st.markdown(f"**M² construidos:** {proj.get('m2_construidos', 'N/A')}")
                                    st.markdown(f"**Presupuesto estimado:** €{proj.get('presupuesto_ejecucion', 'N/A')}")
                                    pdf = proj.get('pdf_path')
                                    if pdf and os.path.exists(pdf):
                                        try:
                                            with open(pdf, 'rb') as fh:
                                                b64 = base64.b64encode(fh.read()).decode()
                                                href = f"data:application/pdf;base64,{b64}"
                                                st.markdown(f"[Descargar PDF del proyecto]({href})")
                                        except Exception:
                                            st.write("PDF no disponible para descarga")

                                    # Compra del proyecto (paquete ZIP) — pedir email comprador
                                    buyer_email = st.text_input("Email comprador (para facturación)", key=f"buy_email_{proj.get('id')}")
                                    if st.button("Comprar Proyecto (Paquete ZIP)", key=f"buy_proj_{proj.get('id')}"):
                                        if not buyer_email or '@' not in buyer_email:
                                            st.error('Introduce un email válido para completar la compra')
                                        else:
                                            precio_base = float(proj.get('presupuesto_ejecucion') or proj.get('m2_construidos') or 0)
                                            try:
                                                comision = db.registrar_venta_proyecto(proj.get('id'), buyer_email, 'Paquete ZIP', precio_base)
                                            except Exception:
                                                comision = 0.0

                                            try:
                                                from export_ops import generar_paquete_descarga
                                                paquete = generar_paquete_descarga(proj.get('titulo', proj.get('nombre', 'proyecto')))
                                                st.download_button('Descargar paquete ZIP', data=paquete, file_name=f"{proj.get('titulo', proj.get('nombre', 'proyecto'))}.zip", mime='application/zip', key=f"download_zip_{proj.get('id', 'unknown')}")
                                                st.success(f'Compra registrada. Comisión Archirapid: €{comision:.2f}')
                                            except Exception as e:
                                                st.error(f'Error generando paquete de descarga: {e}')
                    else:
                        st.info("No hay proyectos que encajen con la edificabilidad de esta finca.")

                    # Información adicional
                    if st.button("📊 Mostrar Información Adicional", key=f"info_{p['id']}", help="Ver datos técnicos completos"):
                        st.json({**p, **cadastral_data})
            else:
                st.error(f"No se encontró la finca con ID: {plot_id}")
        except Exception as e:
            st.error(f"Error al cargar detalles de la finca: {str(e)}")
            st.exception(e)

    show_plot_details(plots_all, pid)

# Formulario de datos personales después de reserva/compra - DESACTIVADO TEMPORALMENTE
# Para evitar conflicto de múltiples dialogs en Streamlit
if st.session_state.get("show_client_form", False):
    # Limpiar el estado de la modal de detalles para evitar conflictos
    if "selected_plot" in st.session_state:
        del st.session_state["selected_plot"]

    # @st.dialog("Complete sus datos personales")  # DESACTIVADO: Conflicto con múltiples dialogs
    def show_client_form():
        st.subheader("📝 Datos Personales")
        st.write("Por favor complete sus datos para finalizar la transacción:")

        with st.form("client_form"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre *", placeholder="Su nombre")
                apellidos = st.text_input("Apellidos *", placeholder="Sus apellidos")
                email = st.text_input("Email *", placeholder="+34 600 000 000")
            with col2:
                telefono = st.text_input("Teléfono *", placeholder="+34 600 000 000")
                direccion = st.text_area("Dirección completa *", placeholder="Calle, número, CP, ciudad, provincia")
                observaciones = st.text_area("Observaciones", placeholder="Comentarios adicionales (opcional)")

            submitted = st.form_submit_button("✅ Confirmar y Finalizar")

            if submitted:
                if not nombre or not apellidos or not email or not telefono or not direccion:
                    st.error("Por favor complete todos los campos obligatorios (*)")
                else:
                    # Procesar la transacción
                    transaction_type = st.session_state.get("transaction_type", "reservation")
                    transaction_id = st.session_state.get("transaction_id", "")

                    # Aquí iría la lógica para guardar los datos del cliente
                    st.success(f"✅ {transaction_type.title()} completada exitosamente!")
                    st.success(f"📧 Recibirás un email de confirmación en {email}")
                    st.success(f"🆔 ID de transacción: {transaction_id}")

                    # Limpiar estado
                    st.session_state["show_client_form"] = False
                    if "transaction_type" in st.session_state:
                        del st.session_state["transaction_type"]
                    if "transaction_id" in st.session_state:
                        del st.session_state["transaction_id"]

                    st.balloons()
                    st.rerun()

    # show_client_form()  # DESACTIVADO: Conflicto con múltiples dialogs
"""