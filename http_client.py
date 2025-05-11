from RUDP_Socket import RUDPsocket

# Create the client socket and connect to the server
client = RUDPsocket()
client.connect(('localhost', 8080))

# Send a simple HTTP GET request to the server
client.send_data(b"GET / HTTP/1.0")

# Receive the server's response (HTTP response)
response = client.receive_data()

# Print the HTTP response
print(f"Server response:\n{response.decode()}")

client.close()
