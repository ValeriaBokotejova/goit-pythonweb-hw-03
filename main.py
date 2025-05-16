"""Web server for GoIT homework 03: simple message board using HTTP and Jinja2."""

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from jinja2 import Environment, FileSystemLoader, TemplateError

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR
STORAGE_DIR = BASE_DIR / "storage"
DATA_FILE = STORAGE_DIR / "data.json"

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Handles HTTP GET and POST requests for a basic web app with form and message display."""

    def do_GET(self):
        """Handles GET requests: routes to HTML pages or static files."""
        match self.path:
            case "/" | "/index" | "/index.html":
                self.render_template("index.html")
            case "/message":
                self.render_template("message.html")
            case "/read":
                self.render_messages()
            case "/style.css":
                self.serve_static_file("style.css", content_type="text/css")
            case "/logo.png":
                self.serve_static_file("logo.png", content_type="image/png")
            case _:
                self.send_error_page()

    def do_POST(self):
        """Handles POST request from the message form."""
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length).decode("utf-8")
            data = parse_qs(body)
            username = data.get("username", [""])[0]
            message = data.get("message", [""])[0]

            self.save_message(username, message)

            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_error_page()

    def render_template(self, template_name, context=None):
        """Renders a Jinja2 HTML template with optional context data."""
        try:
            template = env.get_template(template_name)
            html = template.render(context or {})
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        except TemplateError:
            self.send_error_page()

    def render_messages(self):
        """Reads stored messages from JSON and renders them on the /read page."""
        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        context = {"messages": data}
        self.render_template("read.html", context)

    def serve_static_file(self, filename, content_type):
        """Serves static files like CSS or images."""
        file_path = BASE_DIR / filename
        if file_path.exists():
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error_page()

    def save_message(self, username, message):
        """Saves a form-submitted message to storage/data.json with a timestamp."""
        timestamp = str(datetime.now())
        data = {}

        if DATA_FILE.exists():
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}

        data[timestamp] = {"username": username, "message": message}

        STORAGE_DIR.mkdir(exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def send_error_page(self):
        """Sends a 404 error page if the requested resource is not found."""
        try:
            with open(BASE_DIR / "error.html", "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(404)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    """Runs the HTTP server on port 3000."""
    server_address = ("", 3000)
    httpd = server_class(server_address, handler_class)
    print("Server running on port 3000...")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
