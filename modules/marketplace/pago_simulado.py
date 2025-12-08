# modules/marketplace/pago_simulado.py

import streamlit as st

def init_pago_state():
    """
    Inicializa el estado de pago en session_state si no existe.
    Se llama al inicio de cada vista que use pagos para evitar estados no inicializados.
    """
    if "pagado" not in st.session_state:
        st.session_state.pagado = False

def render_paso_pago(proyecto_id=None):
    """
    Renderiza el paso de pago simulado con un botón único.
    Marca el pago como validado al pulsar el botón.
    """
    init_pago_state()

    st.subheader("💳 Pago (MVP)")

    if not st.session_state.pagado:
        # Botón único de pago simulado con key único
        key = f"pagar_{proyecto_id}" if proyecto_id else "pagar_mvp"
        if st.button("💳 Pagar (MVP)", type="primary", use_container_width=True, key=key):
            st.session_state.pagado = True
            st.success("✅ Pago verificado (MVP). Descargas habilitadas.")
            st.balloons()  # Celebración visual
    else:
        st.info("✅ Pago ya verificado (MVP).")

def verificar_pago():
    """
    Verifica si el pago ha sido realizado.

    Returns:
        bool: True si el pago está validado, False en caso contrario
    """
    init_pago_state()
    return st.session_state.pagado

def reset_pago():
    """
    Resetea el estado de pago (útil para testing o nuevas sesiones).
    """
    st.session_state.pagado = False