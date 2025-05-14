from RUDPsocket_base import RUDPsocket

class RUDPsocketClean(RUDPsocket):
    def __init__(self):
        super().__init__()
        self.loss_probability = 0.0
        self.corrupt_probability = 0.0
        print("[Simulation: Clean] No packet loss or corruption.")

    def send_data(self, data):
        # No simulation, just call the base class method
        return super().send_data(data)

    def recv_data(self):
        # No simulation, just call the base class method
        return super().recv_data()
