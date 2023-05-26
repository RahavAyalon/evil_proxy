import subprocess
import time
import threading

def start_proxy_server():
    return subprocess.Popen(['python3', 'main.py'])

def wait_for_proxy_server():
    # Wait for the proxy server to start
    time.sleep(2)

def test_blocking_website(proxy_host, proxy_port):
    stackoverflow_cmd = f'curl -x {proxy_host}:{proxy_port} http://stackoverflow.com'
    stackoverflow_result = subprocess.run(stackoverflow_cmd, shell=True, capture_output=True, text=True)

    assert 'Access to this content is blocked' in stackoverflow_result.stdout or 'Access to this hostname is blocked' in stackoverflow_result.stdout, 'Proxy server failed to block stackoverflow.com'

def test_non_blocking_website(proxy_host, proxy_port):
    ipinfo_cmd = f'curl -x {proxy_host}:{proxy_port} http://ipinfo.io'
    ipinfo_result = subprocess.run(ipinfo_cmd, shell=True, capture_output=True, text=True)
    assert 'Access to this content is blocked' not in ipinfo_result.stdout, 'Proxy server blocked ipinfo.io'

def test_proxy_server():
    proxy_host = 'localhost'
    proxy_port = 8888

    proxy_process = start_proxy_server()

    # Execute the tests
    wait_for_proxy_server()
    test_blocking_website(proxy_host, proxy_port)
    test_non_blocking_website(proxy_host, proxy_port)

    # Wait for the proxy
    proxy_process.wait()

if __name__ == '__main__':
    test_proxy_server()