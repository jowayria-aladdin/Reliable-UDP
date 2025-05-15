import socket
import zlib
import struct
from rudp_socket import rudp_socket

ACK_FORMAT = "!I"  # Format for unpacking the sequence number from ACK
MAX_RETRIES = 3
TIMEOUT = 2.0

class HTTPRUDPClient:
    def __init__(self, host='localhost', port=8080):
        self.rudp = rudp_socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (host, port)
        self.sock.settimeout(TIMEOUT)

    def send_request(self, count=3):
        request = (
            "GET / HTTP/1.1\r\n"
            "Host: localhost\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode()

        for seq in range(count):
            success = False
            for attempt in range(1, MAX_RETRIES + 1):
                print(f"[CLIENT] Sending request #{seq + 1}, attempt {attempt}")
                self.rudp.send(self.sock, request, self.server_address, seq=seq)

                try:
                    ack_data, _ = self.sock.recvfrom(1024)

                    if ack_data.startswith(b"ACK") and len(ack_data) >= 7:
                        ack_seq = struct.unpack(ACK_FORMAT, ack_data[3:7])[0]
                        if ack_seq == seq:
                            print(f"[CLIENT] ACK received for request #{seq + 1}")
                            success = True
                            break
                        else:
                            print(f"[CLIENT] Wrong ACK SEQ: got {ack_seq}, expected {seq}")
                    else:
                        print(f"[CLIENT] Received non-ACK or malformed message (ignored)")

                except socket.timeout:
                    print(f"[CLIENT] Timeout waiting for ACK (request #{seq + 1})")
                except ConnectionResetError:
                    print(f"[CLIENT] Connection reset by server on request #{seq + 1}")
                except Exception as e:
                    print(f"[CLIENT] Unexpected error on request #{seq + 1}: {e}")

            if not success:
                print(f"[CLIENT] Failed to deliver request #{seq + 1} after {MAX_RETRIES} attempts")
                continue

            try:
                response_data, _ = self.sock.recvfrom(4096)
                if len(response_data) >= 8:
                    seq_recv = int.from_bytes(response_data[:4], 'big')
                    recv_checksum = int.from_bytes(response_data[4:8], 'big')
                    payload = response_data[8:]
                    calc_checksum = zlib.crc32(payload)

                    if recv_checksum != calc_checksum:
                        print(f"[CLIENT] Corrupted HTTP response detected for request #{seq + 1} (SEQ {seq_recv})")
                    else:
                        print(f"[CLIENT] HTTP Response #{seq + 1}:\n{payload.decode('utf-8', errors='replace')}")
                else:
                    print(f"[CLIENT] HTTP Response #{seq + 1}: [invalid or too short]")
            except socket.timeout:
                print(f"[CLIENT] Timeout waiting for HTTP response for request #{seq + 1}")
            except Exception as e:
                print(f"[CLIENT] Error receiving HTTP response for request #{seq + 1}: {e}")

if __name__ == "__main__":
    client = HTTPRUDPClient()
    client.send_request(count=3)
