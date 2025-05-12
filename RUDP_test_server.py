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

if __name__ == "__main__":
    main()
