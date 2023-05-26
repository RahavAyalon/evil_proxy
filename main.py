import socket, sys, datetime, time
from _thread import start_new_thread
from bs4 import BeautifulSoup


class Server:
    # Constructors initializing basic architecture
    BLOCKED_KEYWORDS_FILE_PATH = './keywords.txt'
    BLOCKED_HOSTS_FILE_PATH = './hosts.txt'

    def __init__(self):
        self.blocked_keywords = set()
        self.blocked_hosts = set()

        self.load_blocked_keywords(self.BLOCKED_KEYWORDS_FILE_PATH)
        self.load_blocked_hosts(self.BLOCKED_HOSTS_FILE_PATH)

    def load_blocked_keywords(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                self.blocked_keywords.add(line.strip())

    def load_blocked_hosts(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                self.blocked_hosts.add(line.strip())

    def is_host_blocked(self, host):
        return host in self.blocked_hosts

    def is_content_blocked(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text()

        for keyword in self.blocked_keywords:
            if keyword in text:
                return True
        return False

    # Helper Function to get Time Stamp
    def getTimeStampp(self):
        return "[" + str(datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')) + "]"

    # Function which triggers the server
    def start_server(self, conn=3, buffer=4096, port=8080):
        try:
            print(self.getTimeStampp() + "   \n\nStarting Server\n\n")

            self.listen(conn, buffer, port)

        except KeyboardInterrupt:
            print(self.getTimeStampp() + "   Interrupting Server.")
            time.sleep(.5)

        finally:
            print(self.getTimeStampp() + "   Stopping Server")
            sys.exit()

    # Listener for incoming connections
    def listen(self, max_connections_num, buffer, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(('', port))
            s.listen(max_connections_num)
            print(self.getTimeStampp() + "   Listening...")
            print(self.getTimeStampp() + "   Initializing Sockets [ready] Binding Sockets [ready] Listening...")
        except:
            print(self.getTimeStampp() + "   Error: Cannot start listening...")
            sys.exit(1)

        while True:
            # Try to accept new connections and read the connection data in another thread
            try:
                conn, addr = s.accept()
                print(self.getTimeStampp() + "   Request received from: " + addr[0] + " at port: " + str(addr[1]))
                start_new_thread(self.connection_read_request, (conn, addr, buffer))

            except Exception as e:
                print(self.getTimeStampp() + "  Error: Cannot establish connection..." + str(e))
                sys.exit(1)


    # Function to read request data
    def connection_read_request(self, conn, addr, buffer):
        # Try to split necessary info from the header
        try:
            request = conn.recv(buffer)
            header = request.split(b'\n')[0]
            requested_file = request
            requested_file = requested_file.split(b' ')
            url = header.split(b' ')[1]

            # Stripping Port and Domain
            hostIndex = url.find(b"://")
            if hostIndex == -1:
                temp = url
            else:
                temp = url[(hostIndex + 3):]

            portIndex = temp.find(b":")

            serverIndex = temp.find(b"/")
            if serverIndex == -1:
                serverIndex = len(temp)

            # Use the port in header
            port = int((temp[portIndex + 1:])[:serverIndex - portIndex - 1])
            webserver = temp[:portIndex]

            try:
                if self.is_host_blocked(webserver.decode()):
                        print(self.getTimeStampp() + "   Website Blacklisted")
                        response = "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n"
                        conn.sendall(response.encode())
                        conn.close()
                else:
                     # If method is CONNECT (HTTPS)
                    print(self.getTimeStampp() + "   CONNECT Request")
                    print(self.getTimeStampp() + "   HTTPS Connection request")
                    # Stripping requested file
                    requested_file = requested_file[1]
                    print("Requested File ", requested_file)
                    self.https_proxy(webserver, port, conn, request, addr, buffer, requested_file)
            except:
                pass

        except Exception as e:
            print(self.getTimeStampp() + "  Error: Cannot read connection request..." + str(e))
            return
        

    def https_proxy(self, webserver, port, conn, request, addr, buffer_size, requested_file):
        # Stripping filename
        requested_file = requested_file.replace(b".", b"_").replace(b"http://", b"_").replace(b"/", b"")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # If successful, send 200 code response
            s.connect((webserver, port))
            reply = "HTTP/1.0 200 Connection established\r\n"
            reply += "Proxy-agent: Jarvis\r\n"
            reply += "\r\n"
            conn.sendall(reply.encode())
        except socket.error as err:
            pass

        conn.setblocking(0)
        s.setblocking(0)
        print(self.getTimeStampp() + "  HTTPS Connection Established")

        # Initialize a variable to store the website's content
        website_content = b""
        
        while True:
            try:
                request = conn.recv(buffer_size)
                s.sendall(request)
            except socket.error as err:
                pass

            try:
                reply = s.recv(buffer_size)
                
                # Append the received data to the website_content variable
                website_content += reply
                
                conn.sendall(reply)
            except socket.error as e:
                pass

            # Check if the desired keywords are present in the website's content
            for blocked_keyword in self.blocked_keywords:
                if blocked_keyword.encode() in website_content:
                    print(self.getTimeStampp() + "   Website Blacklisted")
                    response = "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\n\r\n"
                    conn.sendall(response.encode())
                    conn.close()

            # If the response from the server is empty
            if not reply:
                break



if __name__ == "__main__":
    server = Server()
    server.start_server()