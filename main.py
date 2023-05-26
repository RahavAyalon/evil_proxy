from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import http.client

class ProxyHandler(BaseHTTPRequestHandler):
    blocked_hosts = set()  # Set to store the blocked hostnames

    def load_blocked_hosts(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                self.blocked_hosts.add(line.strip())

    def is_host_blocked(self, host):
        return host in self.blocked_hosts

    def do_proxy_request(self, method, host, path):
        try:
            conn = http.client.HTTPSConnection(host)
            conn.request(method, path)
            response = conn.getresponse()
            response_body = response.read()

            # Send the response back to the client
            self.send_response(response.status)
            for header, value in response.getheaders():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response_body)
        except Exception as e:
            # Handle any errors that occurred during the request
            self.send_response(500)  # Internal Server Error
            self.end_headers()
            self.wfile.write(str(e).encode())

    def do_GET(self):
        parsed_url = urlparse(self.path)
        host = parsed_url.netloc
        path = parsed_url.path

        if self.is_host_blocked(host):
            self.send_response(403)  # Forbidden
            self.end_headers()
            self.wfile.write(b'Access to this hostname is blocked.')
        else:
            # Proxy the GET request to the target server
            self.do_proxy_request("GET", host, path)

    def do_POST(self):
        parsed_url = urlparse(self.path)
        host = parsed_url.netloc
        path = parsed_url.path

        if self.is_host_blocked(host):
            self.send_response(403)  # Forbidden
            self.end_headers()
            self.wfile.write(b'Access to this hostname is blocked.')
        else:
            # Proxy the POST request to the target server
            content_length = int(self.headers['Content-Length'])
            request_body = self.rfile.read(content_length)

            try:
                conn = http.client.HTTPSConnection(host)
                conn.request("POST", path, body=request_body, headers=self.headers)
                response = conn.getresponse()
                response_body = response.read()

                # Send the response back to the client
                self.send_response(response.status)
                for header, value in response.getheaders():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response_body)
            except Exception as e:
                # Handle any errors that occurred during the request
                self.send_response(500)  # Internal Server Error
                self.end_headers()
                self.wfile.write(str(e).encode())

    def do_PUT(self):
        parsed_url = urlparse(self.path)
        host = parsed_url.netloc
        path = parsed_url.path

        if self.is_host_blocked(host):
            self.send_response(403)  # Forbidden
            self.end_headers()
            self.wfile.write(b'Access to this hostname is blocked.')
        else:
            # Proxy the PUT request to the target server
            content_length = int(self.headers['Content-Length'])
            request_body = self.rfile.read(content_length)

            try:
                conn = http.client.HTTPSConnection(host)
                conn.request("PUT", path, body=request_body, headers=self.headers)
                response = conn.getresponse()
                response_body = response.read()

                # Send the response back to the client
                self.send_response(response.status)
                for header, value in response.getheaders():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response_body)
            except Exception as e:
                # Handle any errors that occurred during the request
                self.send_response(500)  # Internal Server Error
                self.end_headers()
                self.wfile.write(str(e).encode())

    def do_DELETE(self):
        parsed_url = urlparse(self.path)
        host = parsed_url.netloc
        path = parsed_url.path

        if self.is_host_blocked(host):
            self.send_response(403)  # Forbidden
            self.end_headers()
            self.wfile.write(b'Access to this hostname is blocked.')
        else:
            # Proxy the DELETE request to the target server
            try:
                conn = http.client.HTTPSConnection(host)
                conn.request("DELETE", path, headers=self.headers)
                response = conn.getresponse()
                response_body = response.read()

                # Send the response back to the client
                self.send_response(response.status)
                for header, value in response.getheaders():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response_body)
            except Exception as e:
                # Handle any errors that occurred during the request
                self.send_response(500)  # Internal Server Error
                self.end_headers()
                self.wfile.write(str(e).encode())

    def do_HEAD(self):
        parsed_url = urlparse(self.path)
        host = parsed_url.netloc
        path = parsed_url.path

        if self.is_host_blocked(host):
            self.send_response(403)  # Forbidden
            self.end_headers()
            self.wfile.write(b'Access to this hostname is blocked.')
        else:
            # Proxy the HEAD request to the target server
            self.do_proxy_request("HEAD", host, path)

    def do_CONNECT(self):
        self.send_response(501)  # Not Implemented
        self.end_headers()
        self.wfile.write(b'CONNECT method is not supported.')

def run_proxy_server():
    host = 'localhost'
    port = 8888
    blacklist_file_path = './blacklist.txt'

    server = HTTPServer((host, port), ProxyHandler)
    server.RequestHandlerClass.load_blocked_hosts(ProxyHandler, blacklist_file_path)
    print(f'Proxy server is running on {host}:{port}')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('Proxy server stopped.')

if __name__ == '__main__':
    run_proxy_server()
