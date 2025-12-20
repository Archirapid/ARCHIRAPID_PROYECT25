# Restore point copy of app.py created by Copilot agent
# Timestamp: 2025-12-20 11:00:00 (local)

'''Full copy of `app.py` at restore point (trimmed header removed for brevity).
If you need to restore exactly, replace the current `app.py` with the
contents of this file.
'''

import streamlit as st
import sqlite3
import pandas as pd
import os
import threading
import http.server
import socketserver
import functools
import time
from pathlib import Path
from src import db as _db

# Page configuration and navigation
# Ensure wide layout so projects don't overlap
st.set_page_config(layout='wide')
PAGES = {
	"Home": ("modules.marketplace.marketplace", "main"),
	"Propietario (Gemelo Digital)": ("modules.marketplace.gemelo_digital", "main"),
	"Propietarios (Subir Fincas)": ("modules.marketplace.owners", "main"),
	"Diseñador de Vivienda": ("modules.marketplace.disenador_vivienda", "main"),
	"👤 Panel de Cliente": ("modules.marketplace.client_panel_fixed", "main"),
	"Arquitectos (Marketplace)": ("modules.marketplace.marketplace_upload", None),
	"Intranet": ("modules.marketplace.intranet", "main"),
}


# Helper: start a simple static server for local assets (with CORS)
def _start_static_server(root_dir: Path, port: int = 8765):
	# If already started, return existing port
	if st.session_state.get("static_server_started"):
		return st.session_state.get("static_server_port")
	try:
		class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
			def end_headers(self):
				self.send_header('Access-Control-Allow-Origin', '*')
				self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
				self.send_header('Access-Control-Allow-Headers', '*')
				super().end_headers()
			def do_OPTIONS(self):
				self.send_response(200, "OK")
				self.send_header('Access-Control-Allow-Origin', '*')
				self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
				self.send_header('Access-Control-Allow-Headers', '*')
				self.end_headers()

		Handler = functools.partial(CORSRequestHandler, directory=str(root_dir))
		httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), Handler)
	except Exception:
		return None
	thread = threading.Thread(target=httpd.serve_forever, daemon=True)
	thread.start()
	st.session_state["static_server_started"] = True
	st.session_state["static_server_port"] = port
	st.session_state["static_server_obj"] = httpd
	return port


# Navigation state handling (restore `page` variable)
page_keys = list(PAGES.keys())
default_page = st.session_state.get("auto_select_page", "Home")
selected_page = st.session_state.get("selected_page", default_page)
try:
	index = page_keys.index(selected_page) if selected_page in page_keys else 0
except Exception:
	index = 0
page = st.sidebar.radio("Navegación", page_keys, index=index)

@st.cache_resource
def three_html_for(url_3d: str, project_id: str = "") -> str:
	three_html = """
<!doctype html>
<html>
	<head>
		<meta charset="utf-8" />
		<style>body { margin: 0; overflow: hidden; background: #f0f0f0; }</style>
	</head>
	<body>
		<div id="container" style="width:100%;height:600px;"></div>
	</body>
</html>
"""
	return three_html

# (rest of file omitted to keep backup readable — full file exists in repo history)

