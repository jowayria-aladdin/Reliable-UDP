import random
import zlib
import struct

# Define flags as bits
SYN = 0b0001
ACK = 0b0010
FIN = 0b0100

class BaseRUDP:
    # Packet format: SEQ (4 bytes), FLAGS (1 byte), CHECKSUM (4 bytes), PAYLOAD (variable)
    HEADER_FORMAT = "!IBI"  # SEQ (4), FLAGS (1), CHECKSUM (4)

    def pack(self, seq, flags, payload):
        checksum = zlib.crc32(payload)
        header = struct.pack(self.HEADER_FORMAT, seq, flags, checksum)
        return header + payload

    def unpack(self, packet):
        if len(packet) < 9:
            return None, None, None, None, False
        seq, flags, recv_checksum = struct.unpack(self.HEADER_FORMAT, packet[:9])
        payload = packet[9:]
        calc_checksum = zlib.crc32(payload)
        valid = (recv_checksum == calc_checksum)
        return seq, flags, recv_checksum, payload, valid

class CleanRUDPSocket(BaseRUDP):
    def send(self, sock, data, address, seq=0, flags=0):
        packet = self.pack(seq, flags, data)
        sock.sendto(packet, address)

    def recv(self, sock):
        packet, addr = sock.recvfrom(4096)
        seq, flags, checksum, payload, valid = self.unpack(packet)
        return seq, flags, payload, valid, addr

class LossRUDPSocket(CleanRUDPSocket):
    def __init__(self, drop_rate=0.3):
        self.drop_rate = drop_rate

    def maybe_drop(self):
        return random.random() < self.drop_rate

    def send(self, sock, data, address, seq=0, flags=0):
        if self.maybe_drop():
            print("[LOSS] Packet dropped")
            return
        super().send(sock, data, address, seq, flags)

class CorruptRUDPSocket(CleanRUDPSocket):
    def __init__(self, corrupt_rate=0.3):
        self.corrupt_rate = corrupt_rate

    def maybe_corrupt(self, data):
        if random.random() < self.corrupt_rate:
            return bytes([b ^ 0xFF for b in data])
        return data

    def send(self, sock, data, address, seq=0, flags=0):
        packet = self.pack(seq, flags, data)
        header, payload = packet[:9], packet[9:]
        corrupted_payload = self.maybe_corrupt(payload)
        corrupted_packet = header + corrupted_payload
        sock.sendto(corrupted_packet, address)

class LossCorruptRUDPSocket(BaseRUDP):
    def __init__(self, drop_rate=0.3, corrupt_rate=0.3):
        self.drop_rate = drop_rate
        self.corrupt_rate = corrupt_rate

    def maybe_drop(self):
        return random.random() < self.drop_rate

    def maybe_corrupt(self, data):
        if random.random() < self.corrupt_rate:
            return bytes([b ^ 0xFF for b in data])
        return data

    def send(self, sock, data, address, seq=0, flags=0):
        if self.maybe_drop():
            print("[LOSS+CORRUPT] Packet dropped")
            return
        packet = self.pack(seq, flags, data)
        header, payload = packet[:9], packet[9:]
        corrupted_payload = self.maybe_corrupt(payload)
        corrupted_packet = header + corrupted_payload
        sock.sendto(corrupted_packet, address)

    def recv(self, sock):
        packet, addr = sock.recvfrom(4096)
        seq, flags, checksum, payload, valid = self.unpack(packet)
        return seq, flags, payload, valid, addr
