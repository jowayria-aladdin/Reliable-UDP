from RUDP_Socket import RUDPsocket

# Create and bind the server to a local address
server = RUDPsocket()
server.bind(('localhost', 8080))

print("Server listening on port 8080...")

# Wait for connection and receive data
client_socket = server.accept()
print("Connection established with client")

while True:
    data = client_socket.receive_data()  # Receive data
    if data:
        print(f"Received: {data.decode()}")
        if data.decode() == "GET / HTTP/1.0":
            with open('web_files/test.html', 'r') as file:
                response = file.read()
                client_socket.send_data(response.encode())  # Send HTTP response
        else:
            client_socket.send_data(b"Invalid request")
    else:
        break

server.close()
