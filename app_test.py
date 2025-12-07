# app_test.py - Test inmobiliaria only
import streamlit as st

st.set_page_config(page_title="ARCHIRAPID Test", layout="wide")

from modules.marketplace import inmobiliaria_mapa
inmobiliaria_mapa.mostrar_mapa_inmobiliario()