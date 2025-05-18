import socket
from rudp_socket import rudp_socket, SYN, ACK, FIN

class HTTPRUDPServer:
    def __init__(self, host='localhost', port=8080):
        self.rudp = rudp_socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        # Track sessions: addr -> state info
        self.sessions = {}

    def send_packet(self, data, addr, seq=0, flags=0):
        try:
            self.rudp.send(self.sock, data, addr, seq=seq, flags=flags)
        except Exception as e:
            print(f"[SERVER] Error sending packet to {addr}: {e}")

    def parse_http_request(self, data):
        try:
            text = data.decode('utf-8')
            lines = text.split('\r\n')
            request_line = lines[0].split()
            method = request_line[0]
            path = request_line[1]
            headers = {}
            i = 1
            while i < len(lines) and lines[i]:
                if ':' in lines[i]:
                    key, val = lines[i].split(':', 1)
                    headers[key.strip().lower()] = val.strip()
                i += 1
            body = '\r\n'.join(lines[i+1:]) if i+1 < len(lines) else ""
            return method, path, headers, body
        except Exception:
            return None, None, {}, ""

    def build_http_response(self, status_code=200, body="", headers=None):
        reason = {200: "OK", 404: "Not Found"}.get(status_code, "OK")
        if headers is None:
            headers = {}
        headers_text = "".join(f"{k}: {v}\r\n" for k,v in headers.items())
        response = f"HTTP/1.0 {status_code} {reason}\r\n{headers_text}\r\n{body}"
        return response.encode('utf-8')

    def serve_loop(self):
        print("[SERVER] Listening for connections...")
        while True:
            try:
                seq, flags, payload, valid, addr = self.rudp.recv(self.sock)
            except Exception as e:
                print("[SERVER] Error receiving packet:", e)
                continue

            if not valid:
                print(f"[SERVER] Dropped corrupted packet from {addr}")
                continue

            session = self.sessions.get(addr, {"state": "CLOSED", "expected_seq": 0})

            # Handle connection states
            if flags & SYN:
                # Start handshake
                print(f"[SERVER] SYN received from {addr}")
                self.send_packet(b"", addr, seq=0, flags=SYN | ACK)
                session["state"] = "SYN_RECEIVED"
                session["expected_seq"] = seq + 1
                self.sessions[addr] = session
                continue

            if session["state"] == "SYN_RECEIVED" and flags & ACK:
                print(f"[SERVER] Connection established with {addr}")
                session["state"] = "ESTABLISHED"
                self.sessions[addr] = session
                continue

            if session["state"] == "ESTABLISHED":
                # Handle FIN for teardown first
                if flags & FIN:
                    print(f"[SERVER] FIN received from {addr}")
                    # ACK client's FIN
                    self.send_packet(b"", addr, seq=session["expected_seq"], flags=ACK)
                    session["expected_seq"] += 1
                    session["state"] = "CLOSE_WAIT"
                    self.sessions[addr] = session

                    # Send server's FIN
                    self.send_packet(b"", addr, seq=session["expected_seq"], flags=FIN)
                    session["state"] = "LAST_ACK"
                    self.sessions[addr] = session
                    continue

                # Check expected sequence number for regular data packets
                if seq != session["expected_seq"]:
                    print(f"[SERVER] Unexpected SEQ {seq} from {addr}, expected {session['expected_seq']}")
                    ack_seq = max(session["expected_seq"] - 1, 0)
                    self.send_packet(b"", addr, seq=ack_seq, flags=ACK)
                    continue

                # Process HTTP request if sequence number matches
                method, path, headers, body = self.parse_http_request(payload)
                if not method:
                    response = self.build_http_response(404, "Not Found")
                else:
                    print(f"[SERVER] {method} request for {path} from {addr}")
                    if method.upper() == "GET":
                        if path == "/":
                            response_body = "<h1>Hello from RUDP HTTP Server!</h1>"
                            headers_resp = {
                                "Content-Type": "text/html",
                                "Content-Length": str(len(response_body))
                            }
                            response = self.build_http_response(200, response_body, headers_resp)
                        else:
                            response = self.build_http_response(404, "Not Found")
                    elif method.upper() == "POST":
                        response_body = f"Received POST data: {body}"
                        headers_resp = {
                            "Content-Type": "text/plain",
                            "Content-Length": str(len(response_body))
                        }
                        response = self.build_http_response(200, response_body, headers_resp)
                    else:
                        response = self.build_http_response(404, "Not Found")

                self.send_packet(response, addr, seq=session["expected_seq"], flags=ACK)
                session["expected_seq"] += 1
                self.sessions[addr] = session
                continue

            if session["state"] == "LAST_ACK":
                if flags & ACK:
                    print(f"[SERVER] Final ACK received from {addr}. Connection fully closed.")
                    del self.sessions[addr]
                    continue

            # If no session and no SYN, ignore packet
            print(f"[SERVER] Ignoring packet from {addr} in state {session['state']}")

if __name__ == "__main__":
    server = HTTPRUDPServer()
    try:
        server.serve_loop()
    except KeyboardInterrupt:
        print("\n[SERVER] Server stopped manually.")
