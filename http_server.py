from RUDP_test_server import RUDPserver

def main():
    # Initialize the RUDP server
    server = RUDPserver()
    server.bind(('127.0.0.1', 8080))
    print("RUDP HTTP Server listening on 127.0.0.1:8080...")

    # Wait for a client connection
    client_socket = server.accept()
    print("Client connected.")

    while True:
        try:
            data = client_socket.receive_data()
            if not data:
                print("No data received. Closing connection.")
                break

            request_line = data.decode().split('\r\n')[0]
            print(f"Received request: {request_line}")

            if request_line.startswith("GET"):
                # Extract file path
                path = request_line.split()[1]
                if path == "/":
                    path = "/index.html"

                try:
                    with open("web_files" + path, "r") as f:
                        body = f.read()
                    response = (
                        "HTTP/1.0 200 OK\r\n"
                        "Content-Type: text/html\r\n"
                        f"Content-Length: {len(body)}\r\n\r\n"
                        + body
                    )
                except FileNotFoundError:
                    response = (
                        "HTTP/1.0 404 Not Found\r\n"
                        "Content-Type: text/plain\r\n\r\n"
                        "File not found"
                    )
            else:
                response = (
                    "HTTP/1.0 400 Bad Request\r\n"
                    "Content-Type: text/plain\r\n\r\n"
                    "Invalid request"
                )

            client_socket.send_data(response.encode())
        except Exception as e:
            print(f"Server error: {e}")
            break

    client_socket.close()
    server.close()

if __name__ == "__main__":
    main()
