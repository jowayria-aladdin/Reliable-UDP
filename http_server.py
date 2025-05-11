from RUDP_Socket import RUDPsocket
import os

# Create and bind the server to a local address
server = RUDPsocket()
server.bind(('localhost', 8080))

print("HTTP Server listening on port 8080...")

# Wait for the client to connect
client_socket = server.accept()
print("Connection established with client")

while True:
    # Receive data (HTTP request)
    data = client_socket.receive_data()

    if data:
        # Process the HTTP request
        request = data.decode().split('\r\n')[0]  # Extract request line (e.g., GET / HTTP/1.0)
        print(f"Received request: {request}")

        # Handle HTTP GET request for the root
        if request == "GET / HTTP/1.0":
            # Read the content of index.html
            try:
                with open('web_files/test.html', 'r') as file:
                    response_content = file.read()
                    # Send the HTTP response
                    response = "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n" + response_content
                    client_socket.send_data(response.encode())
            except FileNotFoundError:
                # Handle case when the file is not found
                response = "HTTP/1.0 404 Not Found\r\n\r\nFile not found"
                client_socket.send_data(response.encode())
        else:
            # Handle invalid request
            response = "HTTP/1.0 400 Bad Request\r\n\r\nInvalid request"
            client_socket.send_data(response.encode())
    else:
        break

server.close()
