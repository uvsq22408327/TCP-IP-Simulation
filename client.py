import socket
import time
import logging
from constants import SERVER_HOST, PORT, SYN, ACK, SYN_ACK, FIN, FIN_ACK, TIME_WAIT, TIMEOUT, DATA, NAK, RCV_WINDOW
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

class Client:
    """
    TCP Simulation Client: Handles connection, data request, acknowledgment, retransmissions, and disconnection.
    """

    def __init__(self, server_ip=SERVER_HOST, port=PORT):
        self.server_ip = server_ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(TIMEOUT)

    def connect(self):
        """
        Establishes a connection with the server using the TCP 3-way handshake (SYN, SYN-ACK, ACK).
        """
        try:
            self.socket.connect((self.server_ip, self.port))
            logging.info(f"Attempting to connect to {self.server_ip}:{self.port}...")

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

    def request_data(self):
        """
        Dynamically requests a number of packets from the server and handles retransmissions.
        """
        try:
            num_packets = int(input("Enter the number of packets to request: "))  # User input
            if num_packets <= 0:
                logging.error("Number of packets must be greater than 0.")
                return

            self.socket.send(str(num_packets).encode())  # Send packet request
            logging.info(f"Requested {num_packets} packets from server.")

            for _ in range(num_packets):
                try:
                    response = self.socket.recv(1024).decode()
                    
                    if response.startswith(DATA):
                        seq_num = int(response.split(":")[1])  # Extract sequence number
                        
                        packet = Packet(seq_num, 0, DATA)
                        packet.mark_sent()  # Track when the packet was sent

                        # Simulate possible packet loss
                        if Packet.simulate_packet_loss():
                            logging.warning(f"Packet {seq_num} lost! Sending NAK...")
                            self.socket.send(f"{NAK}:{seq_num}".encode())
                        else:
                            logging.info(f"Received packet {seq_num}, sending ACK...")
                            self.socket.send(f"{ACK}:{seq_num}".encode())
                            packet.mark_received()  # Calculate RTT

                except socket.timeout:
                    logging.error("Timeout waiting for server response.")
                    break

        except ValueError:
            logging.error("Invalid input. Please enter a valid number.")

        except Exception as e:
            logging.error(f"Error during data transfer: {e}")

    def close_connection(self):
        """
        Gracefully terminates the connection using the TCP FIN handshake.
        """
        try:
            logging.info("Sending FIN to close connection...")
            self.socket.send(FIN.encode())

            response = self.socket.recv(1024).decode()
            if response == FIN_ACK:
                logging.info("Received FIN-ACK from server. Sending final ACK...")
                self.socket.send(ACK.encode())

                logging.info(f"Entering TIME_WAIT state for {TIME_WAIT} seconds before closing connection...")
                for i in range(TIME_WAIT, 0, -1):
                    logging.info(f"Closing in {i} seconds...")
                    time.sleep(1)  # Wait for 1 second and log countdown

        except Exception as e:
            logging.error(f"Error during connection termination: {e}")

        finally:
            self.socket.close()
            logging.info("Client connection closed.")

    def display_metrics(self):
        """
        Displays performance metrics.
        """
        if Packet.total_packets_sent > 0:
            loss_percentage = (Packet.total_lost_packets / Packet.total_packets_sent) * 100
            avg_rtt = Packet.total_transmission_time / max(1, Packet.total_packets_sent)
            logging.info("\n📊 Client Performance Metrics:")
            logging.info(f"Total Packets Sent: {Packet.total_packets_sent}")
            logging.info(f"Total Retransmissions: {Packet.total_retransmissions}")
            logging.info(f"Packet Loss Rate: {loss_percentage:.2f}%")
            logging.info(f"Average RTT: {avg_rtt:.4f} seconds")

# Run the client
if __name__ == "__main__":
    ip = input("Enter server IP (press Enter for default 127.0.0.1): ") or SERVER_HOST
    port = int(input(f"Enter server port (press Enter for default {PORT}): ") or PORT)

    client = Client(ip, port)
    client.connect()
    client.request_data()
    client.close_connection()
    client.display_metrics()
