#!/usr/bin/env python3
"""Simple SPA server that serves static files and rewrites all routes to index.html"""

import os
import socketserver
import http.server

PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(__file__), 'dist')


class SPARequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        # Check if the path exists in the filesystem
        path = self.translate_path(self.path)
        if os.path.exists(path):
            # If it's a directory, check for index.html
            if os.path.isdir(path):
                index_path = os.path.join(path, 'index.html')
                if os.path.exists(index_path):
                    self.path = self.path.rstrip('/') + '/index.html'
            # Serve the file as-is
            return super().do_GET()
        else:
            # Rewrite to index.html for SPA routing
            self.path = '/index.html'
            return super().do_GET()


def main():
    with socketserver.TCPServer(('0.0.0.0', PORT), SPARequestHandler) as httpd:
        print(f"SPA server running on http://0.0.0.0:{PORT}")
        print(f"Serving directory: {DIRECTORY}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
