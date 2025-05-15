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
        self.rudp.send(self.sock, data, addr, seq=seq, flags=flags)

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
                if seq != session["expected_seq"]:
                    print(f"[SERVER] Unexpected SEQ {seq} from {addr}, expected {session['expected_seq']}")
                    # Ignore or resend ACK for last received seq to prompt resend
                    self.send_packet(b"", addr, seq=0, flags=ACK)
                    continue

                session["expected_seq"] += 1
                self.sessions[addr] = session

                # Handle FIN for teardown
                if flags & FIN:
                    print(f"[SERVER] FIN received from {addr}")
                    self.send_packet(b"", addr, seq=seq+1, flags=ACK)
                    print(f"[SERVER] Connection closed with {addr}")
                    del self.sessions[addr]
                    continue

                # Process HTTP request
                method, path, headers, body = self.parse_http_request(payload)
                if not method:
                    # Bad request; respond 404
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
                        # Echo body for demo
                        response_body = f"Received POST data: {body}"
                        headers_resp = {
                            "Content-Type": "text/plain",
                            "Content-Length": str(len(response_body))
                        }
                        response = self.build_http_response(200, response_body, headers_resp)
                    else:
                        response = self.build_http_response(404, "Not Found")

                self.send_packet(response, addr, seq=seq+1, flags=ACK)
                continue

            # If no session and no SYN, ignore packet
            print(f"[SERVER] Ignoring packet from {addr} in state {session['state']}")

if __name__ == "__main__":
    server = HTTPRUDPServer()
    server.serve_loop()
