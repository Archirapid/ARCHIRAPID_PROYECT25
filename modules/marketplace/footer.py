# modules/marketplace/footer.py
import streamlit as st

def show_footer():
    """Footer profesional para ARCHIRAPID - MVP"""
    st.markdown("---")

    # Container para el footer
    with st.container():
        col1, col2, col3, col4 = st.columns([1, 2, 2, 2])

        with col1:
            # Logo
            try:
                st.image("assets/branding/logo.png", width=80)
            except:
                st.markdown("🏗️ **ARCHIRAPID**")

        with col2:
            st.markdown("""
            **🏢 ARCHIRAPID**  
            *Equipo liderado por Raúl Villar*  
            Pozuelo de Alarcón, Madrid (Spain)  
            📞 +34 623 172 704
            """)

        with col3:
            st.markdown("""
            **🚀 Tecnologías:**  
            IA • RV • RAV • Gemelos Digitales • Blockchain
            """)

        with col4:
            st.markdown("""
            **💡 Solución integral** para la problemática de la vivienda:  
            *Rápida • Económica • Sostenible*

            **💰 INVIERTE CON NOSOTROS**  
            ✉️ moskovia@me.com
            """)

    # Línea final sutil
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 12px; margin-top: 10px;'>
    ARCHIRAPID MVP - Transformando el sector inmobiliario con tecnología avanzada
    </div>
    """, unsafe_allow_html=True)