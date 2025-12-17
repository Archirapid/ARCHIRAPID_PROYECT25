import streamlit as st

st.set_page_config(page_title="ARCHIRAPID Test", layout="wide")
st.sidebar.title("ARCHIRAPID - Test Version")
page = st.sidebar.radio("Navegación", [
    "Home",
    "Test Marketplace"
])

if page == "Home":
    st.title("🏗️ ARCHIRAPID - Test Version")
    st.success("✅ Aplicación funcionando correctamente")
    st.info("Esta es una versión de prueba sin dialogs para verificar funcionalidad básica")

elif page == "Test Marketplace":
    st.title("🗺️ Marketplace Test")
    st.info("Marketplace básico sin dialogs")

    # Simple marketplace content without dialogs
    st.subheader("Fincas Disponibles")
    st.write("Aquí irían las fincas disponibles...")

    # Mock data
    fincas = [
        {"id": 1, "title": "Finca Centro", "price": 150000, "area": 500},
        {"id": 2, "title": "Finca Suburbio", "price": 120000, "area": 400},
        {"id": 3, "title": "Finca Rural", "price": 80000, "area": 800}
    ]

    for finca in fincas:
        with st.expander(f"🏠 {finca['title']}"):
            st.write(f"**Precio:** €{finca['price']}")
            st.write(f"**Área:** {finca['area']} m²")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"💰 Reservar {finca['title']}", key=f"reserve_{finca['id']}"):
                    st.success(f"✅ Reserva simulada para {finca['title']}")
            with col2:
                if st.button(f"🏠 Comprar {finca['title']}", key=f"buy_{finca['id']}"):
                    st.success(f"✅ Compra simulada para {finca['title']}")

st.sidebar.markdown("---")
st.sidebar.info("Versión de prueba - Sin dialogs")
