import subprocess
from pick_sim import pick_mode

def main():
    # Call the pick_mode() function to set up the simulation mode
    pick_mode()

    # The server will now use the selected RUDP socket class from pick_sim.py
    from RUDP_test_server import RUDPsocket  # This will import the RUDPsocket from the selected simulation module
    
    server = RUDPsocket()
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
