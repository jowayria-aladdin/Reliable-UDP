import socket
import struct
import zlib
import random

ACK_FORMAT = "!I"  # Format for packing/unpacking sequence numbers
MAX_PACKET_SIZE = 4096
TIMEOUT = 10.0  # seconds

class RUDPServer:
    def __init__(self, host='localhost', port=8080, drop_rate=0.0, corrupt_rate=0.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.sock.settimeout(TIMEOUT)
        self.drop_rate = drop_rate
        self.corrupt_rate = corrupt_rate
        self.expected_seq = 0
        self.buffer = {}  # Buffer for out-of-order packets

    def simulate_loss_or_corruption(self, data):
        if random.random() < self.drop_rate:
            print("[SERVER] Simulating packet loss.")
            return None
        if random.random() < self.corrupt_rate:
            print("[SERVER] Simulating packet corruption.")
            # Corrupt the data by flipping a bit
            corrupted_data = bytearray(data)
            if len(corrupted_data) > 0:
                corrupted_data[0] ^= 0xFF
            return bytes(corrupted_data)
        return data

    def send_ack(self, addr, seq):
        ack_packet = b"ACK" + struct.pack(ACK_FORMAT, seq)
        self.sock.sendto(ack_packet, addr)
        print(f"[SERVER] ACK sent for SEQ #{seq}")

    def process_packet(self, seq, payload, addr):
        print(f"[SERVER] Processing packet with SEQ #{seq}")
        # Send ACK for the received packet
        self.send_ack(addr, seq)
        # Simulate sending HTTP response
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "Content-Length: 38\r\n"
            "\r\n"
            "<h1>Hello from RUDP HTTP Server!</h1>"
        ).encode()
        # Prepend SEQ and CRC to the response
        crc = zlib.crc32(response)
        header = struct.pack("!II", seq, crc)
        packet = header + response
        self.sock.sendto(packet, addr)
        print("[SERVER] Response sent.")

    def run(self):
        print("[SERVER] Waiting for HTTP request...")
        while True:
            try:
                packet, addr = self.sock.recvfrom(MAX_PACKET_SIZE)
                packet = self.simulate_loss_or_corruption(packet)
                if packet is None:
                    continue  # Simulated loss

                if len(packet) < 8:
                    print("[SERVER] Packet too short, ignoring.")
                    continue

                seq, crc = struct.unpack("!II", packet[:8])
                payload = packet[8:]
                if zlib.crc32(payload) != crc:
                    print(f"[SERVER] CRC mismatch for SEQ #{seq}, ignoring packet.")
                    continue

                if seq == self.expected_seq:
                    self.process_packet(seq, payload, addr)
                    self.expected_seq += 1
                    # Check buffer for the next expected packets
                    while self.expected_seq in self.buffer:
                        buffered_payload, buffered_addr = self.buffer.pop(self.expected_seq)
                        self.process_packet(self.expected_seq, buffered_payload, buffered_addr)
                        self.expected_seq += 1
                elif seq > self.expected_seq:
                    print(f"[SERVER] Out-of-order packet SEQ #{seq} received, buffering.")
                    self.buffer[seq] = (payload, addr)
                    # Send ACK for the received packet
                    self.send_ack(addr, seq)
                else:
                    print(f"[SERVER] Duplicate packet SEQ #{seq} received, resending ACK.")
                    self.send_ack(addr, seq)
            except socket.timeout:
                print("[SERVER] Timeout reached, no data received.")
                break
            except Exception as e:
                print(f"[SERVER] Error: {e}")
                break

if __name__ == "__main__":
    server = RUDPServer()
    server.run()
