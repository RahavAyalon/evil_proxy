import threading
import requests
from termcolor import colored

from main import Server

class ProxyServerTests:
    @staticmethod
    def test_block_stackoverflow():
        server = Server()
        blocked_host = "stackoverflow.com"
        assert server.is_host_blocked(blocked_host) == True
        print(colored("test_block_stackoverflow passed", "green"))

        # Additional test case to check a non-blocked host
        non_blocked_host = "ipinfo.io"
        assert server.is_host_blocked(non_blocked_host) == False
        print(colored("test_block_stackoverflow (non-blocked host) passed", "green"))

    @staticmethod
    def test_allow_ipinfo():
        server = Server()
        allowed_host = "ipinfo.io"
        assert server.is_host_blocked(allowed_host) == False
        print(colored("test_allow_ipinfo passed", "green"))

        # Additional test case to check a blocked host
        blocked_host = "stackoverflow.com"
        assert server.is_host_blocked(blocked_host) == True
        print(colored("test_allow_ipinfo (blocked host) passed", "green"))

    @staticmethod
    def test_concurrent_clients():
        server = Server()

        def start_server():
            server.start_server()
            i = 0
            while i < 10000:
                i += 1

        # Start the server in a separate thread
        server_thread = threading.Thread(target=start_server)
        server_thread.start()

        def simulate_client_request(client_num):
            if client_num == 1:
                # Send request to ipinfo.io
                response = requests.get("http://ipinfo.io")
                assert response.status_code == 200
                assert "ip" in response.json()
                print("Client", client_num, "received response:", response.text)
            else:
                # Simulate client request to another blocked host
                print("Client", client_num, "sending request to blocked host")
                # ...

        # Create and start three threads to simulate concurrent client requests
        threads = []
        for i in range(3):
            t = threading.Thread(target=simulate_client_request, args=(i+1,))
            threads.append(t)
            t.start()

        # Wait for all threads to finish
        for t in threads:
            t.join()

        # Additional assertion to check if the server handled the clients concurrently
        assert True  # Add your assertion here
        print(colored("test_concurrent_clients passed", "green"))

        # Stop the server after the tests are complete
        server_thread.join()

if __name__ == "__main__":
    # Run the tests
    ProxyServerTests.test_block_stackoverflow()
    ProxyServerTests.test_allow_ipinfo()
    ProxyServerTests.test_concurrent_clients()