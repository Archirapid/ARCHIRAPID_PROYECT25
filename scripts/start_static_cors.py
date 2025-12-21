import http.server
import socketserver
import functools
from pathlib import Path

ROOT = Path(r"C:/ARCHIRAPID_PROYECT25")
PORT = 8765

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

if __name__ == '__main__':
    Handler = functools.partial(CORSRequestHandler, directory=str(ROOT))
    with socketserver.ThreadingTCPServer(('127.0.0.1', PORT), Handler) as httpd:
        print(f"Serving {ROOT} at http://127.0.0.1:{PORT}")
        httpd.serve_forever()
