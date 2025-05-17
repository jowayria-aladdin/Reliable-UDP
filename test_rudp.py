import subprocess
import multiprocessing
import time
import os
import random

CONFIG_PATH = "rudp_config.py"

def write_config(sim_type, drop_rate=0.3, corrupt_rate=0.3):
    config = {"type": sim_type}
    if sim_type == "2":
        config["drop_rate"] = drop_rate
    elif sim_type == "3":
        config["corrupt_rate"] = corrupt_rate
    elif sim_type == "4":
        config["drop_rate"] = drop_rate
        config["corrupt_rate"] = corrupt_rate
    with open(CONFIG_PATH, "w") as f:
        f.write(f"config = {repr(config)}\n")

def start_server_on_port(port):
    subprocess.run(["python", "rudp_http_server.py", str(port)])

def run_client_get(port):
    subprocess.run(["python", "rudp_http_client.py", str(port)])

def run_client_post(port):
    subprocess.run([
        "python", "-c",
        (
            "import sys; "
            "from rudp_http_client import HTTPRUDPClient; "
            "client = HTTPRUDPClient(port=int(sys.argv[1])); "
            "client.send_http_request(method='POST', path='/submit', "
            "headers={'Content-Type': 'text/plain'}, body='Testing POST')"
        ),
        str(port)
    ])

def run_test(sim_type, sim_name):
    print(f"\n========== Running Test: {sim_name} ==========")
    write_config(sim_type)

    port = random.randint(8000, 8999)
    print(f"[INFO] Using port {port}")

    server_process = multiprocessing.Process(target=start_server_on_port, args=(port,))
    server_process.start()
    time.sleep(3)

    print(f"[TEST] GET request in {sim_name} mode")
    run_client_get(port)

    print(f"[TEST] POST request in {sim_name} mode")
    run_client_post(port)

    server_process.terminate()
    server_process.join()
    time.sleep(1)

if __name__ == "__main__":
    simulations = [
        ("1", "Clean (No loss or corruption)"),
        ("2", "Loss only"),
        ("3", "Corruption only"),
        ("4", "Loss + Corruption"),
    ]

    for sim_type, sim_name in simulations:
        run_test(sim_type, sim_name)

    print("\n All simulation tests completed.")
