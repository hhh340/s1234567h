#!/usr/bin/env python3
"""Static file server that avoids os.getcwd() (broken in this sandbox)."""
import functools
import http.server
import os
import socketserver

PORT = int(os.environ.get("PORT", 8000))
DIRECTORY = os.path.dirname(os.path.dirname(__file__))  # site/ — avoid abspath/getcwd (broken in this sandbox)

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIRECTORY)
Handler.extensions_map.setdefault(".webmanifest", "application/manifest+json")


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


with ReusableTCPServer(("", PORT), Handler) as httpd:
    print(f"Serving {DIRECTORY} on port {PORT}")
    httpd.serve_forever()
