from RUDP_test_client import RUDPclient  # Assuming the class is still named RUDPclient inside RUDP_test_client

def main():
    # Create RUDP client with simulated loss and corruption (optional)
    client = RUDPclient(loss_rate=0.1, corruption_rate=0.05)

    # Connect to the RUDP server
    server_address = ('127.0.0.1', 8080)
    print(f"Connecting to server at {server_address}...")
    client.connect(server_address)

    # Send an HTTP GET request over RUDP
    http_request = b"GET /index.html HTTP/1.1\r\nHost: 127.0.0.1\r\nConnection: close\r\n\r\n"
    print("Sending HTTP request...")
    client.send_data(http_request)

    # Receive the HTTP response
    print("Waiting for response from server...")
    try:
        response = client.receive_data()
        print("Received HTTP response:\n")
        print(response.decode())
    except Exception as e:
        print(f"Error receiving response: {e}")

    # Close the RUDP connection
    client.close()

if __name__ == "__main__":
    main()
