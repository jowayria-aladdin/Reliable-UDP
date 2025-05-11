from RUDP_Socket import RUDPsocket

class RUDPserver:
    def __init__(self, loss_rate=0.0, corruption_rate=0.0):
        self.server_socket = RUDPsocket(loss_rate=loss_rate, corruption_rate=corruption_rate)

    def bind(self, address):
        self.server_socket.bind(address)

    def accept(self):
        return self.server_socket.accept()

    def close(self):
        self.server_socket.close()
