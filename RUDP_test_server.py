<<<<<<< HEAD
# RUDP_test_server.py (generated from template)
from RUDPsocket_clean import RUDPsocket as RUDPsocket

def main():
    server = RUDPsocket()
    server.bind(('127.0.0.1', 8080))
    print("Server is listening (simulated mode).")

    data = server.recv_data()
    print("Received from client:", data.decode())

    response = b"Hello from server!"
    server.send_data(response)
    server.close()
=======
from pick_sim import get_simulated_socket_class

def main():
    ServerSocketClass = get_simulated_socket_class()
    server = ServerSocketClass()
    server.bind(('0.0.0.0', 8080))
    print("Server is listening...")

    try:
        data = server.recv_data()
        print("Received from client:", data.decode())

        response = b"Hello from server!"
        server.send_data(response)
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server.close()
>>>>>>> 5769476e6de81352437d135cd3542c6bcdc73308

if __name__ == "__main__":
    main()
