import http.server
import socketserver
import json
import re
import os
from data_manager import DatabaseManager, get_epa_category
from dataclasses import asdict

PORT = 8000
db = DatabaseManager()

# Helper to strip ANSI codes from string
def strip_ansi(text: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    # also strip rich markup tags like [green] or [aqi_good]
    rich_escape = re.compile(r'\[.*?\]')
    return rich_escape.sub('', text)

class APIRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            records = db.get_all_records()
            records_dict = [asdict(r) for r in records]
            # Optionally add raw EPA category text
            for r in records_dict:
                raw_epa = strip_ansi(get_epa_category(r['aqi_value']))
                r['epa_category'] = raw_epa

            response = json.dumps(records_dict)
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            avg_aqi = db.get_average_aqi()
            highest = db.get_city_with_highest_aqi()

            stats = {
                "average_aqi": avg_aqi,
                "average_epa": strip_ansi(get_epa_category(avg_aqi)) if avg_aqi else "N/A",
                "highest_city": highest[0] if highest else None,
                "highest_aqi": highest[1] if highest else None,
                "highest_epa": strip_ansi(get_epa_category(highest[1])) if highest else "N/A"
            }

            response = json.dumps(stats)
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()

            # Use absolute path resolving to ensure index.html is found regardless of cwd
            base_dir = os.path.dirname(os.path.abspath(__file__))
            index_path = os.path.join(base_dir, 'index.html')

            try:
                with open(index_path, 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.wfile.write(b"<h1>index.html not found. Please create it.</h1>")

        else:
            # Fallback to default file serving (useful if there are local assets, though we only have index.html)
            super().do_GET()

def start_server():
    with socketserver.TCPServer(("", PORT), APIRequestHandler) as httpd:
        print(f"Server started at http://localhost:{PORT}")
        print("Endpoints:")
        print("  - Web Dashboard: http://localhost:8000/")
        print("  - Data API:      http://localhost:8000/api/data")
        print("  - Stats API:     http://localhost:8000/api/stats")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.server_close()

if __name__ == "__main__":
    start_server()
