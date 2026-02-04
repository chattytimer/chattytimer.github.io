#!/usr/bin/env python3
import http.server
import socketserver
import os
from urllib.parse import unquote

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

PORT = 5001

class SecureHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that prevents directory traversal and restricts to BASE_DIR"""
    
    def translate_path(self, path):
        """Override to prevent directory traversal attacks"""
        # Decode the URL path
        path = unquote(path)
        
        # Remove query string
        if '?' in path:
            path = path.split('?')[0]
        
        # Get the file path relative to BASE_DIR
        words = path.split('/')
        words = [w for w in words if w]
        path = BASE_DIR
        
        for word in words:
            # Prevent directory traversal
            if word == '..':
                continue
            # Prevent access to hidden files/folders starting with dot
            if word.startswith('.'):
                continue
            path = os.path.join(path, word)
        
        # Ensure the resolved path is within BASE_DIR
        real_path = os.path.realpath(path)
        real_base = os.path.realpath(BASE_DIR)
        
        if not real_path.startswith(real_base):
            # Path is outside BASE_DIR, return a safe fallback
            return os.path.join(real_base, 'index.html')
        
        return path
    
    def end_headers(self):
        """Add security headers"""
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'SAMEORIGIN')
        self.send_header('X-XSS-Protection', '1; mode=block')
        super().end_headers()

with socketserver.TCPServer(("", PORT), SecureHTTPRequestHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    print(f"Serving files from: {BASE_DIR}")
    print("Directory traversal protection: ENABLED")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()
