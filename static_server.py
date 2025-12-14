#!/usr/bin/env python3
"""
Servidor HTTP simple para archivos estáticos de ARCHIRAPID
"""

import http.server
import socketserver
import os
import threading
import time

class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silenciar logs del servidor
        pass

def start_static_server(port=8502, directory="static"):
    """Inicia servidor HTTP para archivos estáticos"""
    if not os.path.exists(directory):
        print(f"Directorio {directory} no existe")
        return None

    os.chdir(directory)

    try:
        with socketserver.TCPServer(("", port), QuietHTTPRequestHandler) as httpd:
            print(f"🚀 Servidor estático corriendo en puerto {port}")
            httpd.serve_forever()
    except Exception as e:
        print(f"Error iniciando servidor estático: {e}")
        return None

if __name__ == "__main__":
    # Iniciar servidor en background
    server_thread = threading.Thread(target=start_static_server, daemon=True)
    server_thread.start()

    # Mantener vivo indefinidamente
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Servidor detenido")