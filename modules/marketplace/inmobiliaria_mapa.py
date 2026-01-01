# modules/marketplace/inmobiliaria_mapa.py

import streamlit as st
from modules.marketplace.data_access import list_fincas, list_proyectos, save_transaccion
from modules.marketplace.pago_simulado import render_paso_pago
from modules.marketplace.compatibilidad import list_proyectos_compatibles

# 🚨 STUB MVP: muestra fincas y proyectos en un mapa y permite reservar/pagar
# En producción se integrará con mapas reales (Leaflet, Mapbox, Google Maps)

def mostrar_mapa_inmobiliario():
    st.title("🗺️ Mapa Inmobiliario - ARCHIRAPID")
    st.markdown("### Encuentra tu terreno ideal y proyectos compatibles")

    # Estadísticas rápidas
    fincas = list_fincas()
    proyectos = list_proyectos()

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

    st.subheader("📋 Fincas Disponibles")

    for finca in fincas:
        # Tarjeta de finca mejorada
        with st.container():
            col1, col2 = st.columns([1, 2])

            with col1:
                # Imagen placeholder
                st.image("https://via.placeholder.com/300x200/4CAF50/white?text=FINCA+DISPONIBLE",
                        caption=f"📍 {finca['direccion']}",
                        width=250)

            with col2:
                st.markdown(f"## 🏠 {finca['titulo']}")
                st.markdown(f"**📍 Ubicación:** {finca['direccion']}")
                st.markdown(f"**📏 Superficie:** {finca['superficie_m2']:,} m²")
                st.markdown(f"**🏗️ Máx. Construible:** {int(finca['superficie_m2'] * 0.33):,} m² (33%)")
                st.markdown(f"**📋 Ref. Catastral:** {finca['ref_catastral']}")

                # Información adicional
                with st.expander("📊 Ver detalles completos"):
                    st.json(finca)

        # Proyectos compatibles
        proyectos = list_proyectos_compatibles(finca)
        if proyectos:
            st.markdown("### 🏗️ Proyectos Arquitectónicos Compatibles")
            st.success(f"✅ Encontrados {len(proyectos)} proyectos compatibles para esta finca")

            for proyecto in proyectos:
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