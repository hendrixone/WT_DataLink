import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler

# Change to the directory where your web page files are located
web_directory = os.getcwd()

# Specify the HTML file to be served
html_file = os.path.join(web_directory, "map.html")


class LocalServer:
    def __init__(self, service, db):
        self.server_service = service
        self.dashboard = db
        self.started = False

        self.page_port = 8222
        self.page_serve = HTTPServer(("", self.page_port), pageServe)

        self.map_port = 8223
        self.map_serve = HTTPServer(("", self.map_port), lambda *args, **kwargs: mapServe(self, *args, **kwargs))

    def start(self):
        self.dashboard.log('starting html page server')
        self.page_serve_thread = threading.Thread(target=self.page_serve.serve_forever)
        self.page_serve_thread.start()
        print(f"Server is running on port {self.page_port}")

        self.dashboard.log('starting map data server')
        self.map_serve_thread = threading.Thread(target=self.map_serve.serve_forever)
        self.map_serve_thread.start()

    def stop(self):
        self.dashboard.log('stopping local server')
        self.page_serve.shutdown()
        self.map_serve.shutdown()
        self.dashboard.log('stopping service')
        self.server_service.stop()
        self.page_serve_thread.join()
        self.map_serve_thread.join()
        self.dashboard.log('stopped')


# Create a custom request handler by subclassing SimpleHTTPRequestHandler
class pageServe(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve only the specified HTML file
        return html_file


class mapServe(BaseHTTPRequestHandler):
    # Create a custom request handler by subclassing BaseHTTPRequestHandler
    # add a constructor to store the local_server reference
    def __init__(self,local_server, *args, **kwargs):
        self.local_server = local_server
        # call super's init
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if not self.local_server.started:
            self.local_server.started = True
            self.local_server.dashboard.start_posting_data_thread()
        # Handle GET requests
        self.send_response(200)
        self.send_header("Content-type", "application/json")

        # Add CORS headers
        self.send_header("Access-Control-Allow-Origin", "*")  # Allow requests from any origin
        self.send_header("Access-Control-Allow-Methods", "*")

        self.end_headers()

        # Create the response data as a Python dictionary
        response_data = self.local_server.server_service.get_data()
        # print(response_data)

        # Convert the response data to JSON
        response_body = json.dumps(response_data).encode('utf-8')

        # Send the response body
        self.wfile.write(response_body)
