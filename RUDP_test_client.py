from RUDP_Socket import RUDPsocket

# Connect to the server
client = RUDPsocket()
client.connect(('localhost', 8080))

# Send a simple HTTP GET request
client.send_data(b"GET / HTTP/1.0")

# Receive the server's response
response = client.receive_data()
print(f"Server response: {response.decode()}")

client.close()
