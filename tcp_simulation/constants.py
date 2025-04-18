# constants.py
# Contains protocol constants, packet types, and connection states

# Packet types
SYN = "SYN"
SYN_ACK = "SYN+ACK"
ACK = "ACK"
DATA = "DATA"
NACK = "NACK"
FIN = "FIN"
FIN_ACK = "FIN+ACK"
CLOSED = "CLOSED"

# Connection states
DISCONNECTED = "DISCONNECTED"
CONNECTING = "CONNECTING"
CONNECTED = "CONNECTED"
CLOSING = "CLOSING"

# Packet colors for UI
PACKET_COLORS = {
    SYN: "blue",
    SYN_ACK: "green",
    ACK: "cyan",
    DATA: "orange",
    NACK: "red",
    FIN: "purple",
    FIN_ACK: "magenta",
    CLOSED: "gray"
}
