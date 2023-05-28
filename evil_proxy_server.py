
from _thread import start_new_thread
from bs4 import BeautifulSoup
import datetime
import socket
import time
import sys

class EvilProxyServer:
    BLOCKED_KEYWORDS_FILE_PATH = './keywords_blacklist.txt'
    BLOCKED_HOSTS_FILE_PATH = './hosts_blacklist.txt'

    def __init__(self):
        self.blocked_keywords = []
        self.blocked_hosts = []
        self.is_content_blacklisted = False

        self.load_blocked_keywords(self.BLOCKED_KEYWORDS_FILE_PATH)
        self.load_blocked_hosts(self.BLOCKED_HOSTS_FILE_PATH)

    def log(self, message):
        timestamp = self.get_timestamp()
        print(f"{timestamp} {message}")

    def load_blocked_keywords(self, file_path):
        with open(file_path, 'r') as file:
            self.blocked_keywords = [line.strip() for line in file]

    def load_blocked_hosts(self, file_path):
        with open(file_path, 'r') as file:
            self.blocked_hosts = [line.strip() for line in file]

    def is_host_blocked(self, host):
        return host in self.blocked_hosts

    def is_content_blocked(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()

        for keyword in self.blocked_keywords:
            if keyword in text:
                return True
        return False

    @staticmethod
    def get_timestamp():
        return "[" + str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + "]"

    def start_server(self, conn=3, buffer=4096, port=8080):
        try:
            self.log("Starting Server")
            self.listen(conn, buffer, port)
        except KeyboardInterrupt:
            self.log("Interrupting Server")
            time.sleep(.5)
        finally:
            self.log("Stopping Server")
            sys.exit()

    def listen(self, max_connections_num, buffer, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = "127.0.0.1"
            s.bind(('', port))
            s.listen(max_connections_num)
            self.log(f"Listening to {host}:{port}")
        except Exception as e:
            self.log(f"Error: Cannot start listening: {str(e)}")
            sys.exit(1)

        while True:
            try:
                conn, addr = s.accept()
                self.log(f"Request received from {addr[0]}:{str(addr[1])}")
                start_new_thread(self.handle_connection, (conn, addr, buffer))

            except Exception as e:
                self.log(f"Error: Cannot establish connection: {str(e)}")
                sys.exit(1)

    def handle_connection(self, conn, addr, buffer):
        try:
            request = conn.recv(buffer)
            header = request.split(b'\n')[0]
            requested_file = request.split(b' ')[1]

            url = header.split(b' ')[1]
            port, webserver = self.get_host_and_port(url)

            if self.is_host_blocked(webserver.decode()):
                self.log("Website Blacklisted")
                response = "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n"
                conn.sendall(response.encode(encoding='utf-8'))
                conn.close()
            else:
                self.log("CONNECT Request")
                self.log("HTTPS Connection request")
                self.log(f"Requested File: {requested_file}")
                self.https_proxy(webserver, port, conn, request, buffer, requested_file)

                if self.is_content_blacklisted:
                    self.log("Website Blacklisted")
                    response = "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n"
                    conn.sendall(response.encode())
                    self.is_content_blacklisted = False

        except Exception as e:
            self.log(f"Error: Cannot read connection request: {str(e)}")
            return

    @staticmethod
    def get_host_and_port(url):
        host_index = url.find(b"://")
        if host_index == -1:
            temp = url
        else:
            temp = url[(host_index + 3):]
        port_index = temp.find(b":")
        server_index = temp.find(b"/")
        if server_index == -1:
            server_index = len(temp)
        if port_index == -1 or server_index < port_index:
            port = 80
            webserver = temp[:server_index]
        else:
            port = int((temp[port_index + 1:])[:server_index - port_index - 1])
            webserver = temp[:port_index]
        return port, webserver

    def https_proxy(self, webserver, port, conn, request, buffer_size, requested_file):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.current_url = webserver.decode() + requested_file.decode()
        try:
            s.connect((webserver, port))
            reply = "HTTP/1.0 200 Connection established\r\n"
            reply += "Proxy-agent: EvilProxy\r\n"
            reply += "\r\n"
            conn.sendall(reply.encode(encoding='utf-8'))
        except socket.error:
            pass

        self.log("HTTPS Connection Established")
        website_content = b""

        while True:
            try:
                request = conn.recv(buffer_size)
                s.sendall(request)
            except socket.error:
                pass

            try:
                reply = s.recv(buffer_size)
                website_content += reply
                conn.sendall(reply)
            except socket.error as e:
                pass

            conn.setblocking(0)
            s.setblocking(0)

            for blocked_keyword in self.blocked_keywords:
                if blocked_keyword.encode(encoding='latin-1') in website_content:
                    self.log("Website Blacklisted")
                    response = "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n"
                    conn.sendall(response.encode(encoding='utf-8'))

            if not reply:
                break

if __name__ == "__main__":
    evil_proxy_server = EvilProxyServer()
    evil_proxy_server.start_server()

