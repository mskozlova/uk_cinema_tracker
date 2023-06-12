import json
import sqlite3
import dataclasses
import gzip

from http import HTTPStatus
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
from urllib.parse import parse_qs

import compare
import logging
import model

import html_generators

from vendor import jinja2
from vendor.jinja2 import Environment, PackageLoader, select_autoescape
env = Environment(
    loader=PackageLoader("server"),
    autoescape=select_autoescape(),
    undefined=jinja2.StrictUndefined,
)


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

    def send_bytes(self, payload: bytes):
        self.send_header("Content-Type", f"application/octet-stream")
        self.end_headers()
        self.wfile.write(payload)

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

        if self.path.startswith('/venues.json'):
            with sqlite3.connect('movies.db') as con:
                all_revisions = model.get_all_revisions(con)
                rev = all_revisions[-1] if all_revisions else 1
                venues = model.get_venues(con, rev)
            venues_dicts = [dataclasses.asdict(venue) for venue in venues if venue.available]
            text = json.dumps(venues_dicts)
            self.send_response(HTTPStatus.OK)
            self.send_text(text, "application/json")
            return

        if self.path.startswith('/movies.json'):
            with sqlite3.connect('movies.db') as con:
                all_revisions = model.get_all_revisions(con)
                rev = all_revisions[-1] if all_revisions else 1
                movies = model.get_movies(con, rev)
            movies_dicts = [dataclasses.asdict(movie) for movie in movies if movie.available]
            text = json.dumps(movies_dicts)
            self.send_response(HTTPStatus.OK)
            self.send_text(text, "application/json")
            return

        if self.path.startswith('/showings.json.gz'):
            with sqlite3.connect('movies.db') as con:
                all_revisions = model.get_all_revisions(con)
                rev = all_revisions[-1] if all_revisions else 1
                showings = model.get_showings(con, rev)
            showings_dicts = [dataclasses.asdict(showing) for showing in showings]
            text = json.dumps(showings_dicts)
            gzipped = gzip.compress(text.encode(), 5)
            self.send_response(HTTPStatus.OK)
            self.send_bytes(gzipped)
            return
        
        if self.path.startswith('/showings.json'):
            with sqlite3.connect('movies.db') as con:
                all_revisions = model.get_all_revisions(con)
                rev = all_revisions[-1] if all_revisions else 1
                showings = model.get_showings(con, rev)
            showings_dicts = [dataclasses.asdict(showing) for showing in showings]
            text = json.dumps(showings_dicts)
            self.send_response(HTTPStatus.OK)
            self.send_text(text, "application/json")
            return

        if self.path.startswith('/venues'):
            template = env.get_template("venues.html")
            #print(template.render(the="variables", go="here"))
            #text = html_generators.generate_venues_page(self.path, logger)
            with sqlite3.connect('movies.db') as con:
                all_revisions = model.get_all_revisions(con)
                rev = all_revisions[-1] if all_revisions else 1
                venues = model.get_venues(con, rev)
            venues_dicts = [dataclasses.asdict(venue) for venue in venues if venue.available]
            for venue in venues:
                print(venue.network_name, venue.name, venue.lat, venue.lon)
            text = template.render(the="variables", go="here", venues = venues_dicts)
            self.send_response(HTTPStatus.ACCEPTED)
            self.send_text(text, "text/html")
            return

        if self.path.startswith('/movies'):
            template = env.get_template("movies.html")
            text = template.render()
            self.send_response(HTTPStatus.OK)
            self.send_text(text, "text/html")
            return

        if self.path.startswith('/showings'):
            template = env.get_template("showings.html")
            #print(template.render(the="variables", go="here"))
            #text = html_generators.generate_venues_page(self.path, logger)
            with sqlite3.connect('movies.db') as con:
                all_revisions = model.get_all_revisions(con)
                rev = all_revisions[-1] if all_revisions else 1
                venues = model.get_venues(con, rev)
            venues_dicts = [dataclasses.asdict(venue) for venue in venues if venue.available]
            text = template.render()
            self.send_response(HTTPStatus.ACCEPTED)
            self.send_text(text, "text/html")
            return
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
