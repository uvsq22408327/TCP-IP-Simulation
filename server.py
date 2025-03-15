import socket
import threading
import logging
from constants import SERVER_HOST, PORT, SYN, ACK, SYN_ACK, FIN, FIN_ACK, DATA, NAK, RCV_WINDOW, BUFFER_SIZE
from packet import Packet

# Configure logging (UTF-8 to avoid Windows console encoding issues)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

class Server:
    """
    Multi-Client TCP Simulation Server: Handles data transmission, acknowledgment, retransmissions, and connection termination.
    """

    def __init__(self, host=SERVER_HOST, port=PORT):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)  # Allow multiple clients
        logging.info(f"Server listening on {self.host}:{self.port}...")

    def start(self):
        """
        Starts the server and listens for multiple clients.
        """
        try:
            while True:
                client_socket, client_address = self.socket.accept()
                logging.info(f"Client {client_address} connected.")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()

        except KeyboardInterrupt:
            logging.info("Server shutting down...")
            self.stop()

    def handle_client(self, client_socket, client_address):
        """
        Handles a single client's request in a separate thread.
        """
        try:
            # Perform TCP 3-Way Handshake
            if not self.perform_handshake(client_socket, client_address):
                return

            num_packets = int(client_socket.recv(BUFFER_SIZE).decode())
            logging.info(f"Client {client_address} requested {num_packets} packets.")

            for seq_num in range(1, num_packets + 1):
                if seq_num % RCV_WINDOW == 0:
                    logging.info("Server waiting for ACK before sending more data...")

                packet = Packet(seq_num, 0, DATA)
                packet.mark_sent()
                client_socket.send(f"{DATA}:{seq_num}".encode())
                logging.info(f"Sent packet {seq_num}")

                try:
                    client_socket.settimeout(3)
                    response = client_socket.recv(BUFFER_SIZE).decode()

                    if response.startswith(NAK):
                        logging.warning(f"Retransmitting lost packet {seq_num}...")
                        Packet.total_retransmissions += 1
                        packet.mark_sent()
                        client_socket.send(f"{DATA}:{seq_num}".encode())

                    elif response.startswith(ACK):
                        packet.mark_received()
                        logging.info(f"Packet {seq_num} acknowledged.")

                except socket.timeout:
                    logging.warning(f"No response for packet {seq_num}. Assuming client disconnected.")
                    break

            # Handle FIN handshake
            self.terminate_connection(client_socket, client_address)

        except Exception as e:
            logging.error(f"Error during communication with {client_address}: {e}")

        finally:
            client_socket.close()
            logging.info(f"Closed connection with {client_address}.")

    def perform_handshake(self, client_socket, client_address):
        """
        Implements the TCP 3-Way Handshake (SYN, SYN-ACK, ACK) before communication.
        """
        try:
            syn_request = client_socket.recv(BUFFER_SIZE).decode()
            if syn_request == SYN:
                logging.info(f"Received SYN from {client_address}. Sending SYN-ACK...")
                client_socket.send(SYN_ACK.encode())

                ack_response = client_socket.recv(BUFFER_SIZE).decode()
                if ack_response == ACK:
                    logging.info(f"Handshake successful with {client_address}. Connection established.")
                    return True
                else:
                    logging.warning(f"Unexpected ACK response from {client_address}. Terminating connection.")
                    return False
            else:
                logging.warning(f"Invalid handshake request from {client_address}. Connection denied.")
                return False

        except Exception as e:
            logging.error(f"Error during handshake with {client_address}: {e}")
            return False

    def terminate_connection(self, client_socket, client_address):
        """
        Implements the TCP connection termination process (FIN, FIN-ACK, ACK).
        """
        try:
            fin_request = client_socket.recv(BUFFER_SIZE).decode()
            if fin_request == FIN:
                logging.info(f"Received FIN from {client_address}. Sending FIN-ACK...")
                client_socket.send(FIN_ACK.encode())

                final_ack = client_socket.recv(BUFFER_SIZE).decode()
                if final_ack == ACK:
                    logging.info(f"Received final ACK. Connection with {client_address} successfully closed.")

        except Exception as e:
            logging.error(f"Error during connection termination with {client_address}: {e}")

    def stop(self):
        """
        Stops the server and releases resources.
        """
        self.socket.close()
        self.display_metrics()
        logging.info("Server stopped.")

    def display_metrics(self):
        """
        Displays performance metrics.
        """
        if Packet.total_packets_sent > 0:
            loss_percentage = (Packet.total_lost_packets / Packet.total_packets_sent) * 100
            avg_rtt = Packet.total_transmission_time / max(1, Packet.total_packets_sent)
            logging.info("\n📊 **Server Performance Metrics:**")
            logging.info(f"➡️ Total Packets Sent: {Packet.total_packets_sent}")
            logging.info(f"➡️ Total Retransmissions: {Packet.total_retransmissions}")
            logging.info(f"➡️ Packet Loss Rate: {loss_percentage:.2f}%")
            logging.info(f"➡️ Average RTT: {avg_rtt:.4f} seconds")
        else:
            logging.info("\n📊 No packets were sent.")

# Start the server
if __name__ == "__main__":
    server = Server()
    server.start()
