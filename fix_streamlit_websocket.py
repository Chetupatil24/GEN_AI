#!/usr/bin/env python3
"""
Fix Streamlit WebSocket issue by ensuring localhost is used.
This script modifies the browser's behavior to force localhost.
"""
import http.server
import socketserver
import urllib.request
import re

PORT = 8508

class StreamlitProxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Serve a redirect page that forces localhost
            html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Streamlit - Redirecting...</title>
    <script>
        // Force redirect to localhost
        const currentHost = window.location.hostname;
        if (currentHost === '0.0.0.0' || currentHost === '127.0.0.1') {
            window.location.replace('http://localhost:8503');
        } else {
            window.location.replace('http://localhost:8503');
        }
    </script>
</head>
<body>
    <h1>Redirecting to Streamlit...</h1>
    <p>If you are not redirected, <a href="http://localhost:8503">click here</a>.</p>
</body>
</html>'''
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            # Proxy to Streamlit
            try:
                url = f'http://localhost:8503{self.path}'
                with urllib.request.urlopen(url) as response:
                    content = response.read()
                    self.send_response(200)
                    for header, value in response.headers.items():
                        if header.lower() not in ['content-encoding', 'transfer-encoding']:
                            self.send_header(header, value)
                    self.end_headers()
                    self.wfile.write(content)
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), StreamlitProxy) as httpd:
        print(f"✅ Proxy server started on http://localhost:{PORT}")
        print(f"   This will redirect to http://localhost:8503")
        print(f"   Access: http://localhost:{PORT}")
        httpd.serve_forever()
