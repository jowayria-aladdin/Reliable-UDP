import socket  # For creating UDP sockets
import struct  # For packing/unpacking binary data
import time  # For managing timeouts and delays
import random  # To simulate packet loss and corruption

# Define packet structure: sequence, ack, flags, length, checksum
RUDP_HEADER_FORMAT = "!IIBHH"
RUDP_HEADER_SIZE = struct.calcsize(RUDP_HEADER_FORMAT)
PAYLOAD_MSS = 1024  # Max payload size
DEFAULT_TIMEOUT = 5  # Timeout before retransmission (in seconds)
MAX_RETRANSMISSIONS = 3  # Number of retransmission attempts

# Define flags
FLAG_SYN = 0x01  # SYN flag (start connection)
FLAG_ACK = 0x02  # ACK flag (acknowledgment)
FLAG_FIN = 0x04  # FIN flag (end connection)

# Go-Back-N Flow Control
WINDOW_SIZE = 4  # Window size for Go-Back-N flow control

class RUDPclient:
    def __init__(self, loss_rate=0.0, corruption_rate=0.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
        self.sock.settimeout(DEFAULT_TIMEOUT)  # Set socket timeout
        self.addr = None  # Remote address
        self.seq_num = random.randint(0, 10000)  # Start with a random sequence number
        self.ack_num = 0  # Expected acknowledgment number
        self.connected = False  # Connection status
        self.loss_rate = loss_rate  # Packet loss simulation
        self.corruption_rate = corruption_rate  # Packet corruption simulation
        self.window_start = 0  # Start of the Go-Back-N window
        self.window_end = 0  # End of the Go-Back-N window

    def connect(self, addr):
        self.addr = addr  # Store the destination address
        print(f"Connecting to {addr}...")

        # Perform the 3-way handshake (SYN, SYN+ACK, ACK)
        self._send_packet(b'', FLAG_SYN)  # Send SYN to initiate connection
        for _ in range(MAX_RETRANSMISSIONS):
            try:
                data, _ = self.sock.recvfrom(2048)  # Wait for SYN+ACK response
                recv_seq, ack, flags, _, _ = self._unpack_header(data)
                print(f"Received SYN+ACK: seq={recv_seq}, ack={ack}, flags={flags}")
                if flags & FLAG_SYN and flags & FLAG_ACK:
                    self.ack_num = recv_seq + 1  # Set the acknowledgment number
                    self.seq_num += 1  # Move the sequence number forward
                    self._send_packet(b'', FLAG_ACK)  # Send ACK
                    self.connected = True  # Connection established
                    print("Connection established.")
                    return
            except socket.timeout:
                print("Timeout occurred. Retrying SYN...")
                self._send_packet(b'', FLAG_SYN)  # Resend SYN if timeout
        raise Exception("Connection failed")  # Raise exception if connection fails

    def send_data(self, data):
        if not self.connected:
            raise Exception("Not connected")  # Ensure connection is established

        sent = False  # Flag to indicate if data is successfully sent
        retries = 0  # Retries for sending data
        print(f"Sending data of size {len(data)} bytes.")
        while not sent and retries < MAX_RETRANSMISSIONS:
            self._send_packet(data, 0)  # Send data packet
            try:
                recv, _ = self.sock.recvfrom(2048)  # Wait for acknowledgment
                _, ack, flags, _, _ = self._unpack_header(recv)
                if flags & FLAG_ACK and ack == self.seq_num:
                    self.seq_num += 1  # Increment sequence number
                    sent = True  # Successfully sent
                    print(f"Data sent successfully. Sequence number: {self.seq_num}")
            except socket.timeout:
                retries += 1  # Retry on timeout
                print("Timeout occurred. Retrying data send...")
        if not sent:
            raise Exception("Data send failed")  # Raise if failed to send

    def receive_data(self):
        print("Waiting for data...")
        while True:
            try:
                data, addr = self.sock.recvfrom(2048)  # Receive incoming packet
                self.addr = addr  # Store sender's address
                seq, _, flags, length, checksum = self._unpack_header(data)
                payload = data[RUDP_HEADER_SIZE:RUDP_HEADER_SIZE + length]
                print(f"Received packet: seq={seq}, ack={self.ack_num}, flags={flags}, length={length}")

                # Check for packet corruption via checksum
                if self._checksum(data[:RUDP_HEADER_SIZE] + payload) != 0:
                    print("Checksum failed. Dropping packet.")
                    continue

                # If packet is in order, send acknowledgment and return payload
                if seq == self.ack_num:
                    self.ack_num += 1  # Update the expected acknowledgment number
                    self._send_packet(b'', FLAG_ACK)  # Send ACK
                    print(f"ACK sent for seq={seq}")
                    return payload  # Return the payload data
                else:
                    self._send_packet(b'', FLAG_ACK)  # Send duplicate ACK for out-of-order
                    print("Out-of-order packet received. Duplicate ACK sent.")
            except socket.timeout:
                print("Timeout occurred while waiting for data.")
                continue

    def close(self):
        self._send_packet(b'', FLAG_FIN)  # Send FIN to close the connection
        for _ in range(MAX_RETRANSMISSIONS):
            try:
                recv, _ = self.sock.recvfrom(2048)  # Wait for ACK of FIN
                seq, ack, flags, _, _ = self._unpack_header(recv)
                if flags & FLAG_ACK:
                    print("Connection closed successfully.")
                    break
            except socket.timeout:
                print("Timeout while closing. Retrying FIN...")
                self._send_packet(b'', FLAG_FIN)  # Resend FIN if timeout occurs
        self.sock.close()  # Close socket
        self.connected = False  # Mark as disconnected

    def _send_packet(self, data, flags):
        length = len(data)
        header = struct.pack(RUDP_HEADER_FORMAT, self.seq_num, self.ack_num, flags, length, 0)
        checksum = self._checksum(header + data)  # Calculate checksum
        header = struct.pack(RUDP_HEADER_FORMAT, self.seq_num, self.ack_num, flags, length, checksum)
        packet = header + data  # Create the packet

        # Simulate packet loss
        if random.random() < self.loss_rate:
            print(f"Simulating packet loss for seq={self.seq_num}")
            return  # Simulate packet loss by not sending

        # Simulate packet corruption
        if random.random() < self.corruption_rate:
            print(f"Simulating packet corruption for seq={self.seq_num}")
            packet = packet[:10] + b'\x00\x00' + packet[12:]  # Corrupt the packet

        self.sock.sendto(packet, self.addr)  # Send the packet to the server

    def _unpack_header(self, data):
        return struct.unpack(RUDP_HEADER_FORMAT, data[:RUDP_HEADER_SIZE])  # Unpack the header

    def _checksum(self, data):
        # Calculate checksum using one's complement sum of 16-bit words
        if len(data) % 2 != 0:
            data += b'\x00'  # Pad with zero byte if data length is odd
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
            checksum = (checksum & 0xFFFF) + (checksum >> 16)  # Fold sum to 16 bits
        return ~checksum & 0xFFFF  # Return one's complement of checksum
