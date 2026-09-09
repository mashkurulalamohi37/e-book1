import os
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        raw_path = self.path.split("?")[0].lstrip("/")
        
        if raw_path == "" or raw_path == "index.html":
            target_file = os.path.join(root_dir, "index.html")
            content_type = "text/html; charset=utf-8"
        elif raw_path == "read":
            target_file = os.path.join(root_dir, "output", "ebook", "Non-performing-Loans-in-Bangladesh.html")
            content_type = "text/html; charset=utf-8"
        elif raw_path == "pdf":
            target_file = os.path.join(root_dir, "output", "ebook", "Non-performing-Loans-in-Bangladesh.pdf")
            content_type = "application/pdf"
        elif raw_path == "epub":
            target_file = os.path.join(root_dir, "output", "ebook", "Non-performing-Loans-in-Bangladesh.epub")
            content_type = "application/epub+zip"
        else:
            target_file = os.path.join(root_dir, raw_path.replace("/", os.sep))
            if raw_path.endswith(".png"):
                content_type = "image/png"
            elif raw_path.endswith(".jpg") or raw_path.endswith(".jpeg"):
                content_type = "image/jpeg"
            elif raw_path.endswith(".html"):
                content_type = "text/html; charset=utf-8"
            elif raw_path.endswith(".css"):
                content_type = "text/css"
            elif raw_path.endswith(".pdf"):
                content_type = "application/pdf"
            elif raw_path.endswith(".epub"):
                content_type = "application/epub+zip"
            else:
                content_type = "application/octet-stream"

        if os.path.exists(target_file) and os.path.isfile(target_file):
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.end_headers()
            with open(target_file, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Not Found")
