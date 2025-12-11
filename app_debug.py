#!/usr/bin/env python3
"""
Panel Cliente Integrado ARCHIRAPID - Versión Simplificada para Debug
"""

import streamlit as st

st.set_page_config(
    page_title="ARCHIRAPID - Debug",
    layout="wide",
    page_icon="🏗️"
)

st.title("🏗️ ARCHIRAPID - Debug Mode")
st.write("Testing basic functionality...")

# Test expander
with st.expander("Test Expander"):
    st.write("This is a test expander")

if __name__ == "__main__":
    pass