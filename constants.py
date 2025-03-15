# constants.py

# Network Configuration
SERVER_HOST = "127.0.0.1"  # Localhost for testing
PORT = 12345  # Default port for communication

# Packet Flags
SYN = "SYN"
ACK = "ACK"
SYN_ACK = "SYN-ACK"
FIN = "FIN"
FIN_ACK = "FIN-ACK"
DATA = "DATA"
NAK = "NAK"  # Negative acknowledgment for lost/corrupt packets

# Timeout & Flow Control
TIMEOUT = 5  # Client timeout in seconds
BUFFER_SIZE = 1024  # Packet buffer size in bytes
RCV_WINDOW = 3  # Receive window size (how many packets client can handle at once)
MAX_PACKETS = 10  # Maximum packets the server can send
PACKET_LOSS_PROBABILITY = 0.2  # 20% chance of packet loss for simulation
