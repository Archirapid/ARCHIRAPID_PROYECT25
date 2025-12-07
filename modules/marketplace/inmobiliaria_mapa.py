# modules/marketplace/inmobiliaria_mapa.py

import streamlit as st
from modules.marketplace.data_access import list_fincas, list_proyectos, save_transaccion
from modules.marketplace.pago_simulado import render_paso_pago
from modules.marketplace.compatibilidad import list_proyectos_compatibles

# 🚨 STUB MVP: muestra fincas y proyectos en un mapa y permite reservar/pagar
# En producción se integrará con mapas reales (Leaflet, Mapbox, Google Maps)

def mostrar_mapa_inmobiliario():
    st.title("🗺️ Mapa inmobiliario (MVP)")

    # Listar fincas disponibles
    fincas = list_fincas()
    if not fincas:
        st.warning("No hay fincas disponibles en este momento.")
        return

    st.subheader("📋 Fincas disponibles")
    for finca in fincas:
        st.markdown(f"**{finca['titulo']}** — {finca['direccion']} ({finca['superficie_m2']} m²)")
        st.json(finca)

        # Proyectos compatibles
        proyectos = list_proyectos_compatibles(finca)
        if proyectos:
            st.markdown("### 🏗️ Proyectos compatibles")
            for proyecto in proyectos:
                st.markdown(f"- {proyecto['titulo']} ({proyecto['total_m2']} m²)")
                st.json(proyecto)

                # Pago simulado y descarga
                render_paso_pago()
                if st.session_state.get("pagado", False):
                    st.success("Descargas habilitadas (MVP).")
                    st.download_button("Descargar Memoria PDF",
                                       str(proyecto.get("pdf_memoria_url", "Memoria simulada")).encode("utf-8"),
                                       file_name="memoria_constructiva.pdf")
                    st.download_button("Descargar Plano CAD",
                                       str(proyecto.get("cad_url", "Plano CAD simulado")).encode("utf-8"),
                                       file_name="plano.dxf")

                    # Registrar transacción
                    save_transaccion({
                        "usuario_id": "cliente_demo",
                        "proyecto_id": proyecto["id"],
                        "tipo": "reserva",
                        "estado": "ok"
                    })
        else:
            st.info("No hay proyectos compatibles aún para esta finca.")