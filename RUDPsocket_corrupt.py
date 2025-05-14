import random
from RUDPsocket_base import RUDPsocket

class RUDPsocketCorrupt(RUDPsocket):
    def __init__(self):
        super().__init__()
        self.loss_probability = 0.0
        self.corrupt_probability = 0.3  # 30% corruption
        print("[Simulation: Packet Corruption] Simulating 30% packet corruption.")

    def _simulate_send(self, data, addr):
        if random.random() < self.corrupt_probability:
            print(f"Simulating packet corruption for data to {addr}")
            # Corrupt data by flipping random bits
            corrupted = bytearray(data)
            if len(corrupted) > 10:  # avoid corrupting tiny control messages
                corrupted[10] ^= 0xFF  # flip bits arbitrarily
            self.sock.sendto(bytes(corrupted), addr)
            return
        self.sock.sendto(data, addr)

    def send_data(self, data):
        return super().send_data(data)

    def recv_data(self):
        return super().recv_data()
