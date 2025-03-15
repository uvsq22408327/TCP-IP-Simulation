# packet.py
class Packet:
    def __init__(self, seq_num, ack_num, flags, data=""):
        self.seq_num = seq_num  # Sequence number
        self.ack_num = ack_num  # Acknowledgment number
        self.flags = flags  # Control flags (SYN, ACK, FIN)
        self.data = data  # Payload data

    def __repr__(self):
        return f"Packet(seq={self.seq_num}, ack={self.ack_num}, flags={self.flags}, data={self.data})"
