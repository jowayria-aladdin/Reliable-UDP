from pick_sim import get_simulated_socket_class

def main():
    ClientSocketClass = get_simulated_socket_class()
    client = ClientSocketClass()
    client.connect(('127.0.0.1', 8080))
    print("Connected to HTTP server.")

    http_request = (
        "GET / HTTP/1.1\r\n"
        "Host: 127.0.0.1\r\n"
        "Connection: close\r\n"
        "\r\n"
    )
    print("Sending HTTP request...")
    client.send_data(http_request.encode())

    print("Waiting for HTTP response...")
    response = client.recv_data()
    print("Received response:\n", response.decode())

    client.close()

if __name__ == "__main__":
    main()
