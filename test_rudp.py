import subprocess
import threading
import time
import sys
from rudp_http_client import HTTPRUDPClient


def start_server():
    """Start the RUDP HTTP server in a separate process"""
    try:
        # Use Popen instead of run to keep the process alive
        server_process = subprocess.Popen(
            [sys.executable, "rudp_http_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Give it time to start
        time.sleep(2)
        return server_process
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)


def run_client_get():
    """Test GET request"""
    print("\n=== Testing GET Request ===")
    client = HTTPRUDPClient()
    response, success = client.send_http_request(method="GET", path="/")
    if success:
        print("GET Response:")
        print(response.decode('utf-8'))
    else:
        print("GET Request Failed")


def run_client_post():
    """Test POST request"""
    print("\n=== Testing POST Request ===")
    client = HTTPRUDPClient()
    response, success = client.send_http_request(
        method="POST",
        path="/submit",
        headers={"Content-Type": "text/plain"},
        body="Testing POST"
    )
    if success:
        print("POST Response:")
        print(response.decode('utf-8'))
    else:
        print("POST Request Failed")


def main():
    # Start the server in a separate process
    server_process = start_server()

    try:
        # Test GET request
        run_client_get()

        # Test POST request
        run_client_post()

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        # Clean up
        server_process.terminate()
        server_process.wait()
        print("\nTest completed. Server stopped.")


if __name__ == "__main__":
    main()