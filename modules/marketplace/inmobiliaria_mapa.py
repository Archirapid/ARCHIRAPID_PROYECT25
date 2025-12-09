# modules/marketplace/inmobiliaria_mapa.py

import streamlit as st
import folium
from streamlit_folium import st_folium
from modules.marketplace.data_access import list_fincas_publicadas, list_proyectos_compatibles, save_transaccion
from modules.marketplace.pago_simulado import render_paso_pago

# 🚨 STUB MVP: muestra fincas y proyectos en un mapa y permite reservar/pagar
# En producción se integrará con mapas reales (Leaflet, Mapbox, Google Maps)

def mostrar_mapa_inmobiliario():
    st.title("🗺️ Mapa Inmobiliario - ARCHIRAPID")
    st.markdown("### Encuentra tu terreno ideal y proyectos compatibles")

    # Estadísticas rápidas
    fincas = list_fincas_publicadas()
    # Para proyectos, usar compatibles con finca dummy o contar totales
    from modules.marketplace.data_access import _proyectos
    proyectos = _proyectos

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏠 Fincas Disponibles", len(fincas))
    with col2:
        st.metric("🏗️ Proyectos Totales", len(proyectos))
    with col3:
        proyectos_residenciales = [p for p in proyectos if "residencial" in p.get("etiquetas", [])]
        st.metric("🏘️ Residenciales", len(proyectos_residenciales))

    if not fincas:
        st.warning("No hay fincas disponibles en este momento.")
        return

    # Crear mapa centrado en primera finca
    primera_finca = fincas[0]
    m = folium.Map(
        location=[primera_finca["ubicacion_geo"]["lat"], primera_finca["ubicacion_geo"]["lng"]],
        zoom_start=12
    )

    # Agregar marcadores para cada finca
    for finca in fincas:
        lat = finca["ubicacion_geo"]["lat"]
        lng = finca["ubicacion_geo"]["lng"]

        # Foto miniatura (placeholder si no existe)
        foto_url = finca.get("foto_url", "https://via.placeholder.com/100x75/4CAF50/white?text=FINCA")

        # Crear popup HTML con miniatura y botón "Más detalles"
        popup_html = f"""
        <div style='width:200px; font-family: Arial, sans-serif;'>
            <img src='{foto_url}' width='100%' style='border-radius: 5px; margin-bottom: 8px;'><br>
            <b style='color: #2E7D32;'>{finca['titulo']}</b><br>
            <span style='font-size: 12px; color: #666;'>{finca['direccion']}</span><br>
            <span style='font-weight: bold;'>{finca['superficie_m2']:,} m²</span><br>
            <form action="" method="get" style='margin-top: 5px;'>
                <input type="hidden" name="detalles_finca_id" value="{finca['id']}"/>
                <input type="submit" value="Más detalles"
                       style='background: #4CAF50; color: white; border: none; padding: 5px 10px;
                              border-radius: 3px; cursor: pointer;'/>
            </form>
        </div>
        """

        # Agregar marcador con popup
        folium.Marker(
            [lat, lng],
            popup=popup_html,
            tooltip=f"{finca['titulo']} - {finca['superficie_m2']:,} m²"
        ).add_to(m)

    # Renderizar mapa
    st.subheader("🗺️ Mapa Interactivo")
    st.markdown("Haz clic en los marcadores para ver información básica, o pulsa 'Más detalles' para ver opciones completas.")

    # Usar st_folium para renderizar el mapa
    st_data = st_folium(m, width=700, height=500)

    # Verificar si se pulsó "Más detalles" desde un popup
    finca_id_param = st.query_params.get("detalles_finca_id")

    if finca_id_param:
        finca_id = int(finca_id_param)
        st.session_state["detalles_finca_id"] = finca_id
        # Limpiar query params para evitar re-ejecución
        st.query_params.clear()

    # Mostrar detalles completos si hay finca seleccionada
    if "detalles_finca_id" in st.session_state:
        finca_id = st.session_state["detalles_finca_id"]
        finca = next((f for f in fincas if f["id"] == finca_id), None)

        if finca:
            with st.expander(f"🏠 Detalles Completos: {finca['titulo']}", expanded=True):
                # Información básica de la finca
                col1, col2 = st.columns([1, 2])

                with col1:
                    foto_url = finca.get("foto_url", "https://via.placeholder.com/300x200/4CAF50/white?text=FINCA+DISPONIBLE")
                    st.image(foto_url, caption=f"📍 {finca['direccion']}", use_column_width=True)

                with col2:
                    st.markdown(f"## 🏠 {finca['titulo']}")
                    st.markdown(f"**📍 Ubicación:** {finca['direccion']}")
                    st.markdown(f"**📏 Superficie:** {finca['superficie_m2']:,} m²")
                    st.markdown(f"**🏗️ Máx. Construible:** {int(finca['superficie_m2'] * 0.33):,} m² (33%)")
                    st.markdown(f"**📋 Ref. Catastral:** {finca['ref_catastral']}")

                    # Información adicional
                    with st.expander("📊 Ver detalles técnicos"):
                        st.json(finca)

                # Proyectos compatibles
                proyectos_compatibles = list_proyectos_compatibles(finca)
                if proyectos_compatibles:
                    st.markdown("### 🏗️ Proyectos Arquitectónicos Compatibles")
                    st.success(f"✅ Encontrados {len(proyectos_compatibles)} proyectos compatibles para esta finca")

                    for proyecto in proyectos_compatibles:
                        with st.container():
                            st.markdown("---")
                            col1, col2, col3 = st.columns([2, 1, 1])

                            with col1:
                                st.markdown(f"#### 🏗️ {proyecto['titulo']}")
                                st.markdown(f"**👷 Autor:** {proyecto.get('autor_tipo', 'N/A').title()}")
                                st.markdown(f"**📝 Descripción:** {proyecto.get('descripcion', 'Sin descripción')}")
                                st.markdown(f"**🏷️ Etiquetas:** {', '.join(proyecto.get('etiquetas', []))}")

                            with col2:
                                st.metric("Superficie", f"{proyecto['total_m2']:,} m²")
                                precio = proyecto.get('precio', 0)
                                st.metric("Precio Estimado", f"€{precio:,.0f}")

                            with col3:
                                # Botón de reserva
                                if st.button(f"📋 Reservar {proyecto['titulo']}", key=f"reservar_{proyecto['id']}"):
                                    st.session_state[f'reserva_{proyecto["id"]}'] = True

                                # Información adicional
                                with st.expander("📄 Ver detalles"):
                                    st.json(proyecto)

                        # Sistema de pago si está reservado
                        if st.session_state.get(f'reserva_{proyecto["id"]}', False):
                            st.markdown("### 💳 Procesar Reserva")
                            render_paso_pago(proyecto["id"])

                            if st.session_state.get("pagado", False):
                                st.success("🎉 ¡Reserva completada exitosamente!")
                                st.balloons()

                                # Botones de descarga
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        "📄 Descargar Memoria PDF",
                                        f"Memoria constructiva para {proyecto['titulo']}\n\nProyecto: {proyecto.get('descripcion', '')}\nSuperficie: {proyecto['total_m2']} m²\nPrecio estimado: €{proyecto.get('precio', 0):,.0f}".encode("utf-8"),
                                        file_name=f"memoria_{proyecto['titulo'].lower().replace(' ', '_')}.pdf",
                                        mime="application/pdf",
                                        key=f"download_pdf_{proyecto['id']}"
                                    )

                                with col2:
                                    st.download_button(
                                        "📐 Descargar Plano CAD",
                                        f"Plano CAD para {proyecto['titulo']}\n\nProyecto generado automáticamente\nSuperficie: {proyecto['total_m2']} m²".encode("utf-8"),
                                        file_name=f"plano_{proyecto['titulo'].lower().replace(' ', '_')}.dxf",
                                        mime="application/octet-stream",
                                        key=f"download_cad_{proyecto['id']}"
                                    )

                                # Registrar transacción
                                transaccion = {
                                    "usuario_id": "cliente_demo",
                                    "proyecto_id": proyecto["id"],
                                    "finca_id": finca["id"],
                                    "tipo": "reserva_proyecto",
                                    "estado": "completada",
                                    "monto": proyecto.get("precio", 0)
                                }
                                save_transaccion(transaccion)
                                st.info("✅ Transacción registrada en el sistema")

                                # Botón para nueva reserva
                                if st.button("🔄 Hacer otra reserva", key=f"nueva_reserva_{proyecto['id']}"):
                                    for key in list(st.session_state.keys()):
                                        if key.startswith('reserva_') or key == 'pagado':
                                            del st.session_state[key]
                                    st.rerun()
                else:
                    st.info("No hay proyectos compatibles aún para esta finca.")

                # Botón para cerrar detalles
                if st.button("❌ Cerrar detalles", key=f"cerrar_detalles_{finca_id}"):
                    del st.session_state["detalles_finca_id"]
                    st.rerun()

    # Información adicional
    st.markdown("---")
    with st.expander("ℹ️ Información del Sistema"):
        st.markdown("""
        **🏗️ Sistema ARCHIRAPID MVP**

        - **Fincas:** Datos catastrales simulados
        - **Proyectos:** Arquitectónicos con IA y manuales
        - **Compatibilidad:** Basada en superficie (≤33%) y uso residencial
        - **Pagos:** Simulados para demostración
        - **Descargas:** Archivos generados dinámicamente

        **Próximas funcionalidades:**
        - Mapa interactivo real
        - Fotos reales de fincas
        - Sistema de favoritos
        - Notificaciones por email
        """)