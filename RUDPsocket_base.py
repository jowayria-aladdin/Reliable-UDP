import socket
import struct
import time

# Constants for packet structure
HEADER_FORMAT = '!IIBB'  # Sequence number (I), Acknowledgment number (I), Flags (B), Payload length (B)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# Flag Constants
FLAG_SYN = 0x01
FLAG_ACK = 0x02
FLAG_FIN = 0x04

class RUDPsocket:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = None

    def connect(self, address):
        self.address = address
        print(f"Connecting to server at {self.address}...")
        
    def send_data(self, data):
        seq_num = 0
        ack_num = 0
        flags = FLAG_SYN
        packet = self._pack_header(seq_num, ack_num, flags, data)
        self.sock.sendto(packet, self.address)
        print(f"Sent data with seq_num={seq_num}, ack_num={ack_num}")
    
    def recv_data(self):
        data, _ = self.sock.recvfrom(2048)
        seq, ack, flags, payload_len, _ = self._unpack_header(data)
        return data[HEADER_SIZE:]  # Return the payload data

    def _pack_header(self, seq_num, ack_num, flags, payload):
        payload_len = len(payload)
        return struct.pack(HEADER_FORMAT, seq_num, ack_num, flags, payload_len) + payload

    def _unpack_header(self, data):
        header = data[:HEADER_SIZE]
        seq_num, ack_num, flags, payload_len = struct.unpack(HEADER_FORMAT, header)
        return seq_num, ack_num, flags, payload_len, header

    def close(self):
        self.sock.close()
        print("Socket closed.")
