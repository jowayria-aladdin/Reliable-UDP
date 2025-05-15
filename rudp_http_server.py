import socket
import struct
from rudp_socket import rudp_socket

ACK_FORMAT = "!I"  # Format for ACK sequence numbers

class HTTPRUDPServer:
    def __init__(self, host='localhost', port=8080):
        self.rudp = rudp_socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.processed_seqs = set()  # Track SEQ numbers to avoid reprocessing duplicates

    def serve_loop(self, count=3):
        for _ in range(count):
            print("[SERVER] Waiting for HTTP request...")
            try:
                seq, data, valid, addr = self.rudp.recv(self.sock)
            except Exception as e:
                print("[SERVER] Error receiving packet:", e)
                continue

            if not valid:
                print("[SERVER] Packet corrupted — ignoring.")
                continue

            if seq in self.processed_seqs:
                print(f"[SERVER] Duplicate SEQ #{seq} received — resending ACK only.")
                ack_packet = b"ACK" + struct.pack(ACK_FORMAT, seq)
                self.sock.sendto(ack_packet, addr)
                continue

            try:
                request = data.decode("utf-8")
                print("[SERVER] Received HTTP request:\n", request)

                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/html\r\n"
                    "Content-Length: 38\r\n"
                    "\r\n"
                    "<h1>Hello from RUDP HTTP Server!</h1>"
                ).encode()

            except UnicodeDecodeError:
                print("[SERVER] Request could not be decoded — skipping HTTP response.")
                response = None

            ack_packet = b"ACK" + struct.pack(ACK_FORMAT, seq)
            self.sock.sendto(ack_packet, addr)
            print(f"[SERVER] ACK sent for SEQ #{seq}")

            if response:
                self.rudp.send(self.sock, response, addr, seq=seq)
                print("[SERVER] Response sent.")

            self.processed_seqs.add(seq)

if __name__ == "__main__":
    server = HTTPRUDPServer()
    server.serve_loop(count=10)
