from pick_sim import get_simulated_socket_class

def main():
    ClientSocketClass = get_simulated_socket_class()
    client = ClientSocketClass()
    client.connect(('127.0.0.1', 8080))
    print("Connected to server.")

    message = b"Hello from test client!"
    client.send_data(message)

    response = client.recv_data()
    print("Received from server:", response.decode())

    client.close()

if __name__ == "__main__":
    main()
