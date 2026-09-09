import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        index_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.wfile.write(b"<h1>Non-performing Loans in Bangladesh</h1><p>Digital Edition</p>")
