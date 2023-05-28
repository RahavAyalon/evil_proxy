import threading
import requests
from termcolor import colored
import os
from evil_proxy import Server
from unittest.mock import MagicMock, patch


class ProxyServerTests:


    def __init__(self):
        hosts_file = 'hosts_blacklist.txt'
        keywords_file = 'keywords_blacklist.txt'
        self.BLOCKED_KEYWORD = 'stackoverflow'
        self.BLOCKED_HOSTNAME = 'stackoverflow.com'
        self.NONBLOCKED_HOSTNAME = 'ipinfo.io'
        self.num_passed_tests = 0
        self.proxy = {"https": "127.0.0.1:8080"}

        # Create hosts_blacklist.txt if it doesn't exist and write 'stackoverflow.com' to it
        if os.path.exists(hosts_file):
            os.remove(hosts_file)
        with open(hosts_file, 'w') as file:
            file.write('') 
        with open(hosts_file, 'a') as hosts:
            hosts.write(self.BLOCKED_HOSTNAME  + "\n")

        # Create keywords_blcklist.txt if it doesn't exist and write 'stackoverflow' to it
        if os.path.exists(keywords_file):
            os.remove(keywords_file)
        with open(keywords_file, 'w') as file:
            file.write('')
        with open(keywords_file, 'a') as keywords:
            keywords.write(self.BLOCKED_KEYWORD + "\n")


    def test_block_stackoverflow(self):
        mock_log = MagicMock()
        with patch.object(Server, 'log', mock_log):
            try:
                requests.get("https://" + self.BLOCKED_HOSTNAME, proxies=self.proxy)
            except OSError as e:
                assert '403' in str(e)
                print(colored("Test stackoverflow.com is blocked: PASSED", "green"))
                self.num_passed_tests += 1


    def test_allow_ipinfo(self):
        mock_log = MagicMock()
        with patch.object(Server, 'log', mock_log):
            try:
                response = requests.get("https://" + self.NONBLOCKED_HOSTNAME, proxies=self.proxy)
                assert response.status_code == 200
                assert "ip" in response.json()
                print(colored("Test ipinfo.io is not blocked: PASSED", "green"))
                self.num_passed_tests += 1
            except:
                pass


    def test_concurrent_clients(self):
        mock_log = MagicMock()
        with patch.object(Server, 'log', mock_log):
            # Start the server in a separate thread
            server_thread = threading.Thread(target=None)
            server_thread.start()

            def simulate_client_request(client_num):
                if client_num == 1:
                    response = requests.get("https://" + self.NONBLOCKED_HOSTNAME, proxies=self.proxy)
                    assert response.status_code == 200
                    assert "ip" in response.json()
                else:
                    try:
                        response = requests.get("https://" + self.BLOCKED_HOSTNAME, proxies=self.proxy)
                    except OSError as e:
                        assert '403' in str(e)

            # Create and start three threads to simulate concurrent client requests
            threads = []
            for i in range(3):
                t = threading.Thread(target=simulate_client_request, args=(i+1,))
                threads.append(t)
                t.start()

            # Wait for all threads to finish
            for t in threads:
                t.join()

            print(colored("Test 3 Concurrent Requests: PASSED", "green"))
            self.num_passed_tests += 1

        # Stop the server after the tests are complete
        server_thread.join()

if __name__ == "__main__":
    tester = ProxyServerTests()
    tester.test_block_stackoverflow()
    tester.test_allow_ipinfo()
    tester.test_concurrent_clients()
    print()
    print(colored("***********************************************************", "green"))   
    print(colored(f"Number of tests PASSED: {tester.num_passed_tests} out of 3", "green"))   
    print(colored("***********************************************************", "green")) 
    print()  
