import socket
import time
from rudp_socket import rudp_socket, SYN, ACK, FIN

MAX_RETRIES = 5
TIMEOUT = 2.0

class HTTPRUDPClient:
    def __init__(self, host='localhost', port=8080):
        self.rudp = rudp_socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)
        self.server_address = (host, port)
        self.seq = 0
        self.connected = False

    def send_packet(self, data=b"", flags=0):
        self.rudp.send(self.sock, data, self.server_address, seq=self.seq, flags=flags)

    def recv_packet(self):
        return self.rudp.recv(self.sock)

    def handshake(self):
        print("[CLIENT] Starting handshake")
        for attempt in range(MAX_RETRIES):
            self.send_packet(flags=SYN)
            try:
                seq, flags, payload, valid, addr = self.recv_packet()
                if valid and (flags & SYN) and (flags & ACK):
                    print("[CLIENT] Received SYN+ACK")
                    self.seq += 1
                    self.send_packet(flags=ACK)
                    self.connected = True
                    return True
            except socket.timeout:
                print(f"[CLIENT] Handshake attempt {attempt + 1} timed out.")
        print("[CLIENT] Handshake failed")
        return False

    def teardown(self):
        if not self.connected:
            return

        print("[CLIENT] Sending FIN")
        self.send_packet(flags=FIN)

        ack_received = False
        for attempt in range(MAX_RETRIES):
            try:
                seq, flags, payload, valid, addr = self.recv_packet()
                if not valid:
                    print("[CLIENT] Received invalid packet. Ignoring.")
                    continue

                if (flags & ACK) and not ack_received:
                    print("[CLIENT] Received ACK for our FIN")
                    ack_received = True
                    continue  # Now wait for server's FIN

                if (flags & FIN) and ack_received:
                    print("[CLIENT] Received FIN from server")
                    self.send_packet(flags=ACK)
                    print("[CLIENT] Sent final ACK. Connection closed.")
                    self.connected = False
                    return

            except socket.timeout:
                print(f"[CLIENT] Timeout during teardown (attempt {attempt + 1}), resending FIN")
                self.send_packet(flags=FIN)

        print("[CLIENT] Teardown failed after retries.")

    def send_http_request(self, method="GET", path="/", headers=None, body=""):
        if not self.connected:
            if not self.handshake():
                return None, False

        if headers is None:
            headers = {}
        headers["Connection"] = "close"

        # Build HTTP request text
        request_line = f"{method} {path} HTTP/1.0\r\n"
        headers_lines = "".join(f"{k}: {v}\r\n" for k, v in headers.items())
        http_request = request_line + headers_lines + "\r\n" + body
        http_data = http_request.encode('utf-8')

        print(f"[CLIENT] Sending HTTP {method} request with retransmission")

        for attempt in range(MAX_RETRIES):
            self.send_packet(data=http_data, flags=0)
            try:
                seq, flags, payload, valid, addr = self.recv_packet()
                if valid:
                    response_text = payload.decode('utf-8', errors='replace')
                    print("[CLIENT] HTTP Response received:\n" + response_text)
                    self.teardown()
                    return payload, True
                else:
                    print(f"[CLIENT] Received corrupted HTTP response. Retrying...")
            except socket.timeout:
                print(f"[CLIENT] Timeout waiting for response (attempt {attempt + 1})")

        self.teardown()
        return None, False

if __name__ == "__main__":
    client = HTTPRUDPClient()

    # Example: send GET request
    client.send_http_request(method="GET", path="/")

    # Example: send POST request
    # client.send_http_request(method="POST", path="/submit", headers={"Content-Type": "text/plain"}, body="Hello Server")
