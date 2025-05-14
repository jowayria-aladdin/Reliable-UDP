<<<<<<< HEAD
# RUDP_test_client.py (generated from template)
from RUDPsocket_clean import RUDPsocket as RUDPsocket

def main():
    client = RUDPsocket()
    client.connect(('127.0.0.1', 8080))
    print("Connected to server (simulated mode).")

    message = b"Hello from client!"
=======
from pick_sim import get_simulated_socket_class

def main():
    ClientSocketClass = get_simulated_socket_class()
    client = ClientSocketClass()
    client.connect(('127.0.0.1', 8080))
    print("Connected to server.")

    message = b"Hello from test client!"
>>>>>>> 5769476e6de81352437d135cd3542c6bcdc73308
    client.send_data(message)

    response = client.recv_data()
    print("Received from server:", response.decode())

    client.close()

if __name__ == "__main__":
    main()
