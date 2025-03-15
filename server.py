import socket
import logging
import time
from constants import SERVER_HOST, PORT, SYN, ACK, SYN_ACK, BUFFER_SIZE

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Server:
    """
    TCP Simulation Server: Accepts connections and handles handshake process.
    """

    def __init__(self, host=SERVER_HOST, port=PORT):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a TCP socket
        self.socket.bind((self.host, self.port))  # Bind to address
        self.socket.listen(5)  # Listen for incoming connections
        self.socket.settimeout(1.0)  # Set a timeout to allow graceful shutdown
        logging.info(f"Server started. Listening on {self.host}:{self.port}...")

    def start(self):
        """
        Starts the server and listens for clients. Press Ctrl+C to stop.
        """
        try:
            while True:
                try:
                    client_socket, client_address = self.socket.accept()
                    logging.info(f"Connection attempt from {client_address}")

                    # Step 1: Receive SYN
                    syn_request = client_socket.recv(BUFFER_SIZE).decode()
                    if syn_request == SYN:
                        logging.info("Received SYN. Sending SYN-ACK...")

                        # Step 2: Send SYN-ACK
                        client_socket.send(SYN_ACK.encode())

                        # Step 3: Receive final ACK
                        final_ack = client_socket.recv(BUFFER_SIZE).decode()
                        if final_ack == ACK:
                            logging.info("Received ACK. Connection established successfully!")
                        else:
                            logging.warning("Did not receive expected ACK. Closing connection.")

                    client_socket.close()
                
                except socket.timeout:
                    continue  # Timeout reached, continue checking for shutdown

        except KeyboardInterrupt:
            logging.info("\nServer is shutting down gracefully...")
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
