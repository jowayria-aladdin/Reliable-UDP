from pick_sim import get_simulated_socket_class

def main():
    ServerSocketClass = get_simulated_socket_class()
    server = ServerSocketClass()
    server.bind(('0.0.0.0', 8080))
    print("HTTP server listening on port 8080...")

    while True:
        try:
            print("Waiting for a connection...")
            data = server.recv_data()
            if not data:
                continue

            request = data.decode()
            print("Received HTTP request:\n", request)

            if request.startswith("GET"):
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain\r\n"
                    "Content-Length: 13\r\n"
                    "\r\n"
                    "Hello, world!"
                )
            else:
                response = (
                    "HTTP/1.1 400 Bad Request\r\n"
                    "Content-Length: 0\r\n"
                    "\r\n"
                )

            server.send_data(response.encode())
        except Exception as e:
            print(f"Error: {e}")
            break

    server.close()

if __name__ == "__main__":
    main()
