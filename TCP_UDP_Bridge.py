import socket
from rudp_http_client import HTTPRUDPClient
import threading

BRIDGE_HOST = '127.0.0.1'
BRIDGE_PORT = 8888  # Browser connects here
RUDP_SERVER_HOST = '127.0.0.1'
RUDP_SERVER_PORT = 8080

def handle_browser_request(client_conn):
    try:
        # Receive HTTP request from browser
        request_data = client_conn.recv(4096)
        if not request_data:
            client_conn.close()
            return

        print("[BRIDGE] Received request from browser")
        request_text = request_data.decode(errors='replace')
        request_line = request_text.splitlines()[0]
        method, path, _ = request_line.split()
        
        # Initialize RUDP client
        rudp_client = HTTPRUDPClient(RUDP_SERVER_HOST, RUDP_SERVER_PORT)
        rudp_client.handshake()
        
        # Send to RUDP server
        rudp_client.send_packet(data=request_data, flags=0)
        seq, flags, payload, valid, addr = rudp_client.recv_packet()
        rudp_client.teardown()

        # Send back to browser
        if valid:
            client_conn.sendall(payload)
        else:
            client_conn.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\nCorrupted response")
    except Exception as e:
        print(f"[BRIDGE] Error: {e}")
        client_conn.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\nBridge Error")
    finally:
        client_conn.close()


def start_bridge():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as bridge_socket:
        bridge_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bridge_socket.bind((BRIDGE_HOST, BRIDGE_PORT))
        bridge_socket.listen(5)
        print(f"[BRIDGE] Listening on http://{BRIDGE_HOST}:{BRIDGE_PORT} for browser requests")

        while True:
            client_conn, _ = bridge_socket.accept()
            threading.Thread(target=handle_browser_request, args=(client_conn,), daemon=True).start()

if __name__ == "__main__":
    start_bridge()
