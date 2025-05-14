import random
from RUDPsocket_base import RUDPsocket

class RUDPsocketLossCorrupt(RUDPsocket):
    def __init__(self):
        super().__init__()
        self.loss_probability = 0.2       # 20% chance of loss
        self.corrupt_probability = 0.2    # 20% chance of corruption
        print("[Simulation: Loss + Corruption] Simulating 20% loss and 20% corruption.")

    def _simulate_send(self, data, addr):
        if random.random() < self.loss_probability:
            print(f"Simulating packet loss for data to {addr}")
            return  # Drop packet

        if random.random() < self.corrupt_probability:
            print(f"Simulating packet corruption for data to {addr}")
            # Corrupt the packet (flip bits)
            corrupted = bytearray(data)
            if len(corrupted) > 10:
                corrupted[10] ^= 0xAA
            self.sock.sendto(bytes(corrupted), addr)
            return

        self.sock.sendto(data, addr)

    def send_data(self, data):
        return super().send_data(data)

    def recv_data(self):
        return super().recv_data()
