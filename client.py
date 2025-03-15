import socket
import logging
from constants import SERVER_HOST, PORT, ACK, NAK, DATA, TIMEOUT, RCV_WINDOW, MAX_PACKETS
from packet import Packet  # Ensure Packet class is available

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Client:
    """
    TCP Simulation Client: Handles connection, data request, acknowledgment, and disconnection.
    """

    def __init__(self, server_ip=SERVER_HOST, port=PORT):
        self.server_ip = server_ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(TIMEOUT)

    def connect(self):
        """
        Establishes a connection with the server.
        """
        try:
            self.socket.connect((self.server_ip, self.port))
            logging.info("Connected to server.")
        except Exception as e:
            logging.error(f"Connection error: {e}")

    def request_data(self, num_packets):
        """
        Requests 'num_packets' from the server.
        """
        try:
            self.socket.send(str(num_packets).encode())  # Send packet count request
            logging.info(f"Requested {num_packets} packets from server.")

            for _ in range(num_packets):
                try:
                    response = self.socket.recv(1024).decode()
                    
                    if response.startswith(DATA):
                        seq_num = int(response.split(":")[1])  # Extract sequence number
                        
                        # Simulate possible packet loss
                        if Packet.simulate_packet_loss():
                            logging.warning(f"Packet {seq_num} lost! Sending NAK...")
                            self.socket.send(f"{NAK}:{seq_num}".encode())
                        else:
                            logging.info(f"Received packet {seq_num}, sending ACK...")
                            self.socket.send(f"{ACK}:{seq_num}".encode())

                except socket.timeout:
                    logging.error("Timeout waiting for server response.")
                    break

        except Exception as e:
            logging.error(f"Error during data transfer: {e}")

    def close(self):
        """
        Closes the connection.
        """
        self.socket.close()
        logging.info("Connection closed.")

# Test client
if __name__ == "__main__":
    client = Client()
    client.connect()
    client.request_data(5)
    client.close()
