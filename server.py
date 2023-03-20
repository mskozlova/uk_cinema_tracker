import json
import sqlite3

from http import HTTPStatus
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.parse import parse_qs

import compare
import logging

import html_generators

logger = logging.getLogger()

ALLOWED_ORIGINS = ["http://localhost:8081"]

class CliServiceRequestHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_cors_headers()
        BaseHTTPRequestHandler.end_headers(self)

    def send_cors_headers(self):
        origin = self.headers.get("origin")
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)

    def send_json(self, obj):
        self.send_header("Content-Type", "application/json;charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode("UTF-8", "replace"))

    def send_text(self, text: str, content_type: str = "text/plain"):
        self.send_header("Content-Type", f"{content_type};charset=utf-8")
        self.end_headers()
        self.wfile.write(text.encode("UTF-8", "replace"))

    def send_error(self, code: int, message: str = None, explain: str = None):
        try:
            shortmsg, longmsg = self.responses[code]
        except KeyError:
            shortmsg, longmsg = "???", "???"
        if message is None:
            message = shortmsg
        if explain is None:
            explain = longmsg
        self.log_error("code %d, message %s", code, message)
        self.send_response(code, message)
        return self.send_json({"error": message, "explain": explain})

    def handle_request(self) -> None:
        self.send_cors_headers()

        if self.path == '/favicon.ico':
            self.send_response(HTTPStatus.NOT_FOUND)
            return

        if self.path.startswith('/compare'):
            text = html_generators.generate_diff_page(self.path, logger)
            self.send_response(HTTPStatus.ACCEPTED)
            self.send_text(text, "text/html")
            return
        
        if self.path.startswith('/venues'):
            text = html_generators.generate_venues_page(self.path, logger)
            self.send_response(HTTPStatus.ACCEPTED)
            self.send_text(text, "text/html")
            return

        if self.path.startswith('/movies'):
            text = html_generators.generate_movies_page(self.path, logger)
            self.send_response(HTTPStatus.ACCEPTED)
            self.send_text(text, "text/html")
            return

        if self.path.startswith('/showings'):
            text = html_generators.generate_search_showings_page(self.path, logger)
            self.send_response(HTTPStatus.ACCEPTED)
            self.send_text(text, "text/html")
            return

        self.send_response(HTTPStatus.NOT_FOUND)

    def do_HEAD(self):
        self.handle_request()

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

server_address = ('', 8000)
httpd = HTTPServer(server_address, CliServiceRequestHandler)
httpd.serve_forever()