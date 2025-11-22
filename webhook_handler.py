# Webhook Handler para Stripe
# Ejecutar con: python webhook_handler.py

import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from src.subscription_manager import handle_stripe_webhook

class StripeWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/webhook':
            self.send_response(404)
            self.end_headers()
            return

        # Leer el body
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        # Obtener signature header
        sig_header = self.headers.get('Stripe-Signature', '')

        # Procesar webhook
        if handle_stripe_webhook(post_data, sig_header):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'ERROR')

    def log_message(self, format, *args):
        # Suprimir logs del servidor HTTP
        pass

def run_webhook_server(port=4242):
    """Ejecutar servidor de webhooks en el puerto especificado"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, StripeWebhookHandler)
    print(f"🚀 Webhook server running on port {port}")
    print("Configure this URL in your Stripe dashboard:")
    print(f"http://your-domain.com:{port}/webhook")
    httpd.serve_forever()

if __name__ == '__main__':
    port = int(os.getenv('WEBHOOK_PORT', 4242))
    run_webhook_server(port)