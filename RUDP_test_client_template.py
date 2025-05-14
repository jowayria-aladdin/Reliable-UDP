# RUDP_test_client.py (generated from template)
from {{RUDP_MODULE}} import RUDPsocket as RUDPsocket

def main():
    client = RUDPsocket()
    client.connect(('127.0.0.1', 8080))
    print("Connected to server (simulated mode).")

    message = b"Hello from client!"
    client.send_data(message)

    response = client.recv_data()
    print("Received from server:", response.decode())

    client.close()

if __name__ == "__main__":
    main()
