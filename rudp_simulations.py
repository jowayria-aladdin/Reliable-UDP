import random
import zlib
import struct

class BaseRUDP:
    HEADER_FORMAT = "!I"  # Unsigned int for SEQ number

    def pack(self, seq, payload):
        checksum = zlib.crc32(payload)
        return struct.pack(self.HEADER_FORMAT, seq) + checksum.to_bytes(4, 'big') + payload

    def unpack(self, packet):
        if len(packet) < 8:
            return None, None, None
        seq = struct.unpack(self.HEADER_FORMAT, packet[:4])[0]
        recv_checksum = int.from_bytes(packet[4:8], 'big')
        payload = packet[8:]
        calc_checksum = zlib.crc32(payload)
        if recv_checksum != calc_checksum:
            return seq, payload, False
        return seq, payload, True

# -- CLEAN --

class CleanRUDPSocket(BaseRUDP):
    def send(self, sock, data, address, seq=0):
        packet = self.pack(seq, data)
        sock.sendto(packet, address)

    def recv(self, sock):
        packet, addr = sock.recvfrom(4096)
        return self.unpack(packet) + (addr,)

# -- LOSS --

class LossRUDPSocket(CleanRUDPSocket):
    def __init__(self, drop_rate=0.3):
        self.drop_rate = drop_rate

    def maybe_drop(self):
        return random.random() < self.drop_rate

    def send(self, sock, data, address, seq=0):
        if self.maybe_drop():
            print("[LOSS] Packet dropped")
            return
        super().send(sock, data, address, seq)

# -- CORRUPT --

class CorruptRUDPSocket(CleanRUDPSocket):
    def __init__(self, corrupt_rate=0.3):
        self.corrupt_rate = corrupt_rate

    def maybe_corrupt(self, data):
        if random.random() < self.corrupt_rate:
            return bytes([b ^ 0xFF for b in data])
        return data

    def send(self, sock, data, address, seq=0):
        packet = self.pack(seq, data)
        header, payload = packet[:8], packet[8:]
        corrupted_payload = self.maybe_corrupt(payload)
        corrupted_packet = header + corrupted_payload
        sock.sendto(corrupted_packet, address)


# -- LOSS + CORRUPT --

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

    def send(self, sock, data, address, seq=0):
        if self.maybe_drop():
            print("[LOSS+CORRUPT] Packet dropped")
            return
        packet = self.pack(seq, data)
        packet = self.maybe_corrupt(packet)
        sock.sendto(packet, address)

    def recv(self, sock):
        packet, addr = sock.recvfrom(4096)
        return self.unpack(packet) + (addr,)
