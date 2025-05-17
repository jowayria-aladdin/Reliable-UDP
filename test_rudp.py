import subprocess
import threading
import time

def start_server():
    subprocess.run(["python", "rudp_http_server.py"])

def run_client_get():
    subprocess.run(["python", "rudp_http_client.py"])

def run_client_post():
    import rudp_http_client
    client = rudp_http_client.HTTPRUDPClient()
    client.send_http_request(method="POST", path="/submit", headers={"Content-Type": "text/plain"}, body="Testing POST")

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(3)  # wait for server startup

    print("Running GET request test")
    run_client_get()
    print("Running POST request test")
    run_client_post()
    print("All tests completed.")
