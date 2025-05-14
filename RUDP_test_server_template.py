# RUDP_test_server.py (generated from template)
from {{RUDP_MODULE}} import RUDPsocket as RUDPsocket

def main():
    server = RUDPsocket()
    server.bind(('127.0.0.1', 8080))
    print("Server is listening (simulated mode).")

    data = server.recv_data()
    print("Received from client:", data.decode())

    response = b"Hello from server!"
    server.send_data(response)
    server.close()

if __name__ == "__main__":
    main()
