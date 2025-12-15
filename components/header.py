import streamlit as st


def render_header(logo_path: str = "assets/branding/logo.png", tagline: str = "IA Avanzada + Precios en Vivo + Exportación Profesional"):
    """Render simple header con logo a la izquierda y tagline.

    Esta función es segura para importarse desde `app.py`. Se mantiene pequeña
    y reutilizable por otras pantallas.
    """
    cols = st.columns([1, 4, 1])
    with cols[0]:
        try:
            st.image(logo_path, width=140)
        except Exception:
            st.write("🏗️ ARCHIRAPID")
    with cols[1]:
        st.markdown(f"### {tagline}")
    return cols
