import socket
import logging
from constants import SERVER_HOST, PORT, ACK, NAK, DATA, RCV_WINDOW, MAX_PACKETS, BUFFER_SIZE

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Server:
    """
    TCP Simulation Server: Handles data transmission, acknowledgment, and retransmissions.
    """

    def __init__(self, host=SERVER_HOST, port=PORT):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        logging.info(f"Server listening on {self.host}:{self.port}...")

    def start(self):
        """
        Starts the server and listens for incoming connections.
        """
        try:
            while True:
                client_socket, client_address = self.socket.accept()
                logging.info(f"Client {client_address} connected.")

                try:
                    num_packets = int(client_socket.recv(BUFFER_SIZE).decode())  # Get requested packet count
                    logging.info(f"Client requested {num_packets} packets.")

                    for seq_num in range(1, num_packets + 1):
                        if seq_num % RCV_WINDOW == 0:
                            logging.info("Server waiting for ACK before sending more data...")

                        # Send data packet
                        client_socket.send(f"{DATA}:{seq_num}".encode())
                        logging.info(f"Sent packet {seq_num}")

                        try:
                            # Wait for ACK or NAK (with timeout)
                            client_socket.settimeout(3)
                            response = client_socket.recv(BUFFER_SIZE).decode()
                            
                            if response.startswith(NAK):
                                logging.warning(f"Retransmitting lost packet {seq_num}...")
                                client_socket.send(f"{DATA}:{seq_num}".encode())
                            elif response.startswith(ACK):
                                logging.info(f"Packet {seq_num} acknowledged.")

                        except socket.timeout:
                            logging.warning(f"No response for packet {seq_num}. Assuming client disconnected.")
                            break

                except (ConnectionAbortedError, ConnectionResetError):
                    logging.error("Client disconnected unexpectedly.")
                
                finally:
                    client_socket.close()
                    logging.info("Closed client connection.")

        except KeyboardInterrupt:
            logging.info("Server shutting down...")
            self.stop()

    def stop(self):
        """
        Stops the server and releases resources.
        """
        self.socket.close()
        logging.info("Server stopped.")

# Start the server
if __name__ == "__main__":
    server = Server()
    server.start()
