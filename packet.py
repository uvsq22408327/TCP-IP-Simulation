import random
import time

class Packet:
    """
    Represents a TCP-like packet with sequence number, acknowledgment number, flags, and optional data.
    """

    total_packets_sent = 0
    total_retransmissions = 0
    total_lost_packets = 0
    total_transmission_time = 0  # Stores sum of all RTTs

    def __init__(self, seq_num, ack_num, flags, data=""):
        self.seq_num = seq_num  # Sequence number
        self.ack_num = ack_num  # Acknowledgment number
        self.flags = flags  # Flags (SYN, ACK, DATA, FIN, etc.)
        self.data = data  # Packet payload
        self.sent_time = None  # Store timestamp for RTT measurement

    def __repr__(self):
        return f"Packet(seq={self.seq_num}, ack={self.ack_num}, flags={self.flags}, data={self.data})"

    @staticmethod
    def simulate_packet_loss():
        """
        Simulate packet loss based on predefined probability.
        """
        lost = random.random() < PACKET_LOSS_PROBABILITY  # 20% chance of packet loss
        if lost:
            Packet.total_lost_packets += 1
        return lost

    def mark_sent(self):
        """
        Record the timestamp when a packet is sent.
        """
        self.sent_time = time.time()
        Packet.total_packets_sent += 1

    def mark_received(self):
        """
        Calculate and store the Round Trip Time (RTT) for this packet.
        """
        if self.sent_time:
            rtt = time.time() - self.sent_time
            Packet.total_transmission_time += rtt
