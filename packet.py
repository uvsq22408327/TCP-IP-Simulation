from constants import *

class Packet:
    def __init__(self, packet_type, seq_num=0, data=None, window_size=None):
        self.packet_type = packet_type
        self.seq_num = seq_num
        self.data = data if data else ""
        self.window_size = window_size
        
    def __str__(self):
        return f"Packet({self.packet_type}, seq={self.seq_num}, window={self.window_size}, data={self.data})"
        
    def to_bytes(self):
        # Formatage simple du paquet pour la transmission
        packet_str = f"{self.packet_type}|{self.seq_num}|{self.window_size}|{self.data}"
        return packet_str.encode('utf-8')
    
    @staticmethod
    def from_bytes(byte_data):
        try:
            packet_str = byte_data.decode('utf-8')
            parts = packet_str.split('|', 3)
            if len(parts) < 4:
                parts.extend([None] * (4 - len(parts)))
            
            packet_type, seq_num, window_size, data = parts
            seq_num = int(seq_num) if seq_num and seq_num != "None" else 0
            window_size = int(window_size) if window_size and window_size != "None" else None
            
            return Packet(packet_type, seq_num, data, window_size)
        except Exception as e:
            print(f"Error decoding packet: {e}")
            return None