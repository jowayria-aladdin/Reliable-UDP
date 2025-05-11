import socket  # Import socket module for UDP
import struct  # For binary packing/unpacking
import time  # For timeouts
import random  # To simulate packet loss and corruption

# Define packet structure: sequence, ack, flags, length, checksum
RUDP_HEADER_FORMAT = "!IIBHH"
# I: 4 byte unsigned int, B: 1 byte unsigned char
#  H:2 byte unsigned short
RUDP_HEADER_SIZE = struct.calcsize(RUDP_HEADER_FORMAT)
PAYLOAD_MSS = 1024  # Max payload size (Maximum segment size)
DEFAULT_TIMEOUT = 5  # Seconds before resending a packet
MAX_RETRANSMISSIONS = 3 # Max retry count

# Define flag constants for control flags
FLAG_SYN = 0x01  # Flag used to start the connection
FLAG_ACK = 0x02  # Flag used to acknowledge a packet
FLAG_FIN = 0x04  # Flag used to close the connection

# Go-Back-N Flow Control
WINDOW_SIZE = 4  # Number of unacknowledged packets allowed in the window

class RUDPsocket:
    def __init__(self, loss_rate=0.0, corruption_rate=0.0):
        # Initialize the RUDP socket with packet loss and corruption rates
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP socket that communicates over IPv4 (AF_INET).
        self.sock.settimeout(DEFAULT_TIMEOUT)  
        self.addr = None  # Store remote address to communicate with
        self.seq_num = 0  # Our current sequence number (for sending packets)
        self.ack_num = 0  # Expected sequence number from the peer (for acknowledgment)
        self.connected = False  # Track connection status
        self.loss_rate = loss_rate  # Simulate packet loss with this probability
        self.corruption_rate = corruption_rate  # Simulate packet corruption with this probability
        self.window_start = 0  # Go-Back-N window start sequence number
        self.window_end = 0  # Go-Back-N window end sequence number

    def bind(self, addr):
        # Bind the socket to a local address for listening
        self.sock.bind(addr)

    def connect(self, addr):
        # Connect to a remote address using a 3-way handshake (SYN, ACK)
        self.addr = addr  # Store destination address
        self.seq_num = random.randint(0, 10000)  # Generate a random start sequence number

        self._send_packet(b'', FLAG_SYN)  # Send SYN packet to start the handshake
        for _ in range(MAX_RETRANSMISSIONS):
            try:
                data, _ = self.sock.recvfrom(2048)  # Wait for a response (SYN+ACK)
                recv_seq, ack, flags, _, _ = self._unpack_header(data)
                if flags & FLAG_SYN and flags & FLAG_ACK:
                    self.ack_num = recv_seq + 1  # Expected acknowledgment number is one ahead
                    self.seq_num += 1  # Move our sequence number forward
                    self._send_packet(b'', FLAG_ACK)  # Send ACK to confirm the connection
                    self.connected = True  # Mark as connected
                    return
            except socket.timeout:
                self._send_packet(b'', FLAG_SYN)  # Retry sending SYN if timeout occurs
        raise Exception("Connection failed")  # Raise exception if handshake fails

    def accept(self):
        # Wait for incoming connections and handle the handshake
        while True:
            data, addr = self.sock.recvfrom(2048)  # Wait for SYN packet
            recv_seq, _, flags, _, _ = self._unpack_header(data)
            if flags & FLAG_SYN:
                self.addr = addr  # Store remote address (peer)
                self.ack_num = recv_seq + 1  # Expected acknowledgment number is one ahead
                self.seq_num = random.randint(0, 10000)  # Generate random sequence number
                self._send_packet(b'', FLAG_SYN | FLAG_ACK)  # Send SYN+ACK to acknowledge
                data, _ = self.sock.recvfrom(2048)  # Wait for final ACK
                recv_seq, ack, flags, _, _ = self._unpack_header(data)
                if flags & FLAG_ACK:
                    self.connected = True  # Connection is successful
                    return self

    def send_data(self, data):
        # Send data to the connected peer
        if not self.connected:
            raise Exception("Not connected")  # Raise error if not connected

        sent = False  # Flag to check if data is sent successfully
        retries = 0  # Retry count for retransmission
        while not sent and retries < MAX_RETRANSMISSIONS:
            self._send_packet(data, 0)  # Send data packet
            try:
                recv, _ = self.sock.recvfrom(2048)  # Wait for acknowledgment (ACK)
                _, ack, flags, _, _ = self._unpack_header(recv)
                if flags & FLAG_ACK and ack == self.seq_num:
                    self.seq_num += 1  # Move sequence number forward after successful acknowledgment
                    sent = True
            except socket.timeout:
                retries += 1  # Retry if ACK is not received in time
        if not sent:
            raise Exception("Send failed")  # Raise error if data couldn't be sent after retries

    def receive_data(self):
        # Receive data from the peer
        while True:
            try:
                data, addr = self.sock.recvfrom(2048)  # Receive incoming packet
                self.addr = addr  # Save sender's address
                seq, _, flags, length, checksum = self._unpack_header(data)
                payload = data[RUDP_HEADER_SIZE:RUDP_HEADER_SIZE + length]  # Extract payload

                # Drop the packet if checksum fails (corrupted packet)
                if self._checksum(data[:RUDP_HEADER_SIZE] + payload) != 0:
                    continue

                # If the sequence number is as expected, acknowledge and accept the packet
                if seq == self.ack_num:
                    self.ack_num += 1  # Increment expected acknowledgment number
                    self._send_packet(b'', FLAG_ACK)  # Send acknowledgment (ACK) to the sender
                    return payload  # Return the received payload
                else:
                    self._send_packet(b'', FLAG_ACK)  # Send duplicate ACK for out-of-order packets
            except socket.timeout:
                continue

    def close(self):
        # Gracefully close the connection
        self._send_packet(b'', FLAG_FIN)  # Send FIN to start the connection termination
        for _ in range(MAX_RETRANSMISSIONS):
            try:
                recv, _ = self.sock.recvfrom(2048)  # Wait for final acknowledgment (ACK)
                seq, ack, flags, _, _ = self._unpack_header(recv)
                if flags & FLAG_ACK:
                    break  # Successfully closed the connection
            except socket.timeout:
                self._send_packet(b'', FLAG_FIN)  # Retry sending FIN if timeout occurs
        self.sock.close()  # Close the socket
        self.connected = False  # Mark connection as closed

    def _send_packet(self, data, flags):
        # Send a packet with data and the specified flags
        length = len(data)
        header = struct.pack(RUDP_HEADER_FORMAT, self.seq_num, self.ack_num, flags, length, 0)
        checksum = self._checksum(header + data)  # Calculate checksum
        header = struct.pack(RUDP_HEADER_FORMAT, self.seq_num, self.ack_num, flags, length, checksum)
        packet = header + data

        # Simulate packet loss and corruption based on configured rates
        if random.random() < self.loss_rate:
            return  # Drop the packet (simulate packet loss)
        if random.random() < self.corruption_rate:
            packet = packet[:10] + b'\x00\x00' + packet[12:]  # Corrupt the packet (simulate corruption)

        self.sock.sendto(packet, self.addr)  # Send the packet to the remote address

    def _unpack_header(self, data):
        # Unpack the packet header into sequence number, acknowledgment number, flags, etc.
        return struct.unpack(RUDP_HEADER_FORMAT, data[:RUDP_HEADER_SIZE])

    def _checksum(self, data):
        # Calculate the checksum using one's complement sum of 16-bit words
        if len(data) % 2 != 0:
            data += b'\x00'  # Pad with a zero byte if data length is odd
        checksum = 0
        for i in range(0, len(data), 2):
            word = (data[i] << 8) + data[i + 1]
            checksum += word
            checksum = (checksum & 0xFFFF) + (checksum >> 16)  # Fold the sum to 16 bits
        return ~checksum & 0xFFFF  # Return the one's complement of the sum

