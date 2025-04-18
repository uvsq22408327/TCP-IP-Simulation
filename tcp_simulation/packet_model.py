# packet_model.py
# Defines the Packet class only (logic separated from constants)

class Packet:
    def __init__(self, packet_type, seq_num=None, data=None):
        self.packet_type = packet_type
        self.seq_num = seq_num
        self.data = data
        self.is_corrupt = False

    def __str__(self):
        if self.seq_num is not None:
            return f"{self.packet_type}({self.seq_num})"
        return self.packet_type
