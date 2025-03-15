import socket
import time
import logging
from constants import SERVER_HOST, PORT, SYN, ACK, SYN_ACK, TIMEOUT

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Client:
    """
    TCP Simulation Client: Handles connection establishment, data requests, and disconnection.
    """

    def __init__(self, server_ip=SERVER_HOST, port=PORT):
        self.server_ip = server_ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
        self.socket.settimeout(TIMEOUT)  # Set timeout for responses

    def connect(self):
        """
        Implements the TCP 3-way handshake (SYN, SYN-ACK, ACK).
        """
        try:
            logging.info(f"Attempting to connect to {self.server_ip}:{self.port}...")
            self.socket.connect((self.server_ip, self.port))  # Connect to the server
            
            # Step 1: Send SYN
            logging.info("Sending SYN request...")
            self.socket.send(SYN.encode())

            # Step 2: Receive SYN-ACK
            response = self.socket.recv(1024).decode()
            if response == SYN_ACK:
                logging.info("Received SYN-ACK from server. Sending ACK...")

                # Step 3: Send ACK
                self.socket.send(ACK.encode())
                logging.info("Connection established successfully!")

            else:
                logging.warning("Unexpected response from server. Connection failed.")

        except socket.timeout:
            logging.error("Connection attempt timed out.")
        except Exception as e:
            logging.error(f"An error occurred: {e}")

    def close(self):
        """
        Close the client socket.
        """
        self.socket.close()
        logging.info("Client socket closed.")

# Test the connection
if __name__ == "__main__":
    client = Client()
    client.connect()
    client.close()
