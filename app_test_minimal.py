#!/usr/bin/env python3
"""
ARCHIRAPID - Minimal Test Version
"""

import streamlit as st

st.set_page_config(
    page_title="ARCHIRAPID - Test",
    layout="wide",
    page_icon="🏗️"
)

# Minimal header
st.title("🏗️ ARCHIRAPID - Test Mode")

# Sidebar with expander
with st.sidebar:
    st.title("🎯 Test Panel")

    with st.expander("ℹ️ Test Info"):
        st.write("Testing expander nesting...")

st.write("Basic app working!")

if __name__ == "__main__":
    pass