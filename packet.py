import random

class Packet:
    """
    Represents a TCP-like packet with sequence number, acknowledgment number, flags, and optional data.
    """

    def __init__(self, seq_num, ack_num, flags, data=""):
        self.seq_num = seq_num  # Sequence number
        self.ack_num = ack_num  # Acknowledgment number
        self.flags = flags  # Flags (SYN, ACK, DATA, FIN, etc.)
        self.data = data  # Packet payload

    def __repr__(self):
        return f"Packet(seq={self.seq_num}, ack={self.ack_num}, flags={self.flags}, data={self.data})"

    @staticmethod
    def simulate_packet_loss():
        """
        Simulate packet loss based on predefined probability.
        """
        return random.random() < 0.2  # 20% chance of packet loss
