import random
from RUDPsocket_base import RUDPsocket

class RUDPsocketLoss(RUDPsocket):
    def __init__(self):
        super().__init__()
        self.loss_probability = 0.3  # 30% packet loss
        self.corrupt_probability = 0.0
        print("[Simulation: Packet Loss] Simulating 30% packet loss.")

    def _simulate_send(self, data, addr):
        if random.random() < self.loss_probability:
            print(f"Simulating packet loss for data to {addr}")
            return  # Drop the packet (simulate loss)
        self.sock.sendto(data, addr)

    def send_data(self, data):
        return super().send_data(data)

    def recv_data(self):
        return super().recv_data()
