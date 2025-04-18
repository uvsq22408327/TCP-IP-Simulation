# connection_manager.py
# Manages the TCP connection simulation logic

import threading
import time
import random
from constants import *
import network_ui
import tkinter as tk
from packet_model import Packet  # Ensure Packet is imported from the correct module

class ConnectionManager:
    # Shared state for received packets
    received_packets = {}
    expected_seq = 1

    def __init__(self, client_ui, server_ui, animation_manager, event_manager, network_ui=None):
        self.client_ui = client_ui
        self.server_ui = server_ui
        self.animation_manager = animation_manager
        self.event_manager = event_manager
        self.network_ui = network_ui

        # Ensure these are properly connected
        self.client_ui.connection_handler = self.start_connection
        self.client_ui.close_handler = self.close_connection
        self.client_ui.reset_handler = self.reset_client
        self.server_ui.reset_handler = self.reset_server

        self.timeout = 5.0
        self.packet_error_rate = 0.1
        self.connection_timeout = None

        self.reset_connection_state()

    def reset_connection_state(self):
        """Complete connection state reset"""
        # Reset packet state
        with self.event_manager.packet_processing_lock:
            ConnectionManager.received_packets = {}
            ConnectionManager.expected_seq = 1
        
        # Reset event flags
        self.event_manager.reset()
        
        # Reset UI states
        self.client_ui.set_state(DISCONNECTED)
        self.server_ui.set_state(DISCONNECTED)
        
        # Clear animations
        if hasattr(self, 'network_ui'):
            self.event_manager.queue_event(self.network_ui.clear_animations)
        
        print("Connection state fully reset")

    def start_connection(self):
        """Safe connection starter with state verification"""
        print(f"Connection attempt. Client state: {self.client_ui.state}")
        
        # Verify clean state
        if self.client_ui.state != DISCONNECTED:
            self.client_ui.log_message("Cannot start: Client not ready")
            self.reset_client()  # Force full reset
            return
        
        # Ensure clean slate
        self.reset_connection_state()
        
        # Start connection thread
        try:
            thread = threading.Thread(target=self.client_connection_process, daemon=True)
            thread.start()
            print("New connection thread started successfully")
        except Exception as e:
            self.client_ui.log_message(f"Connection failed: {str(e)}")
            self.reset_client()

    def client_connection_process(self):
        if self.client_ui.state != DISCONNECTED:
            self.client_ui.log_message("Cannot start connection: Client not in disconnected state")
            return
        print("client_connection_process started")
        self.client_ui.set_state(CONNECTING)
        self.client_ui.log_message("Initiating connection to server...")
        syn_packet = Packet(SYN)
        self.client_ui.log_message(f"Sending {syn_packet}")
        self.send_packet_from_client(syn_packet)

        self.connection_timeout = threading.Timer(15.0, self.handle_syn_timeout)
        self.connection_timeout.start()

        if not self.event_manager.wait_for_packet(timeout=15.0):
            self.client_ui.log_message("Timeout waiting for server to receive SYN")
            return

        self.server_ui.set_state(CONNECTING)
        self.server_ui.log_message(f"Received {syn_packet}")
        self.sim_sleep(0.5)

        if self.event_manager.stop_flag:
            return

        syn_ack = Packet(SYN_ACK)
        self.server_ui.log_message("Sending SYN+ACK")
        self.send_packet_from_server(syn_ack)

        if not self.event_manager.wait_for_packet(timeout=15.0):
            self.server_ui.log_message("Timeout waiting for client to receive SYN-ACK")
            return

        self.client_ui.log_message(f"Received {syn_ack}")
        self.sim_sleep(0.5)
        if self.event_manager.stop_flag:
            return

        ack = Packet(ACK)
        self.client_ui.log_message("Sending ACK")
        self.send_packet_from_client(ack)

        if self.connection_timeout:
            self.connection_timeout.cancel()

        if not self.event_manager.wait_for_packet(timeout=15.0):
            self.client_ui.log_message("Timeout waiting for server to receive ACK")
            return

        self.server_ui.log_message(f"Received {ack}")
        self.sim_sleep(0.5)

        self.client_ui.set_state(CONNECTED)
        self.server_ui.set_state(CONNECTED)
        self.client_ui.log_message("Connection established!")
        self.server_ui.log_message("Connection established!")

        self.data_transfer_process()

    def handle_syn_timeout(self):
        if self.client_ui.state == CONNECTING:
            self.client_ui.log_message("Connection timeout: No SYN-ACK received")
            self.client_ui.set_state(DISCONNECTED)
            self.event_manager.stop_flag = True

    def data_transfer_process(self):
        num_packets = self.client_ui.get_packet_count()
        window_size = self.client_ui.get_window_size()
        self.client_ui.log_message(f"Requesting {num_packets} packets with window size {window_size}")

        window_packet = Packet(ACK, 0, f"WINDOW:{window_size}")
        self.send_packet_from_client(window_packet)

        if not self.event_manager.wait_for_packet(timeout=15.0):
            self.client_ui.log_message("Timeout waiting for server to receive window info")
            return

        self.server_ui.log_message(f"Received window size: {window_size}")
        self.sim_sleep(0.5)

        delivered = 0
        seq = 1

        while delivered < num_packets and not self.event_manager.stop_flag:
            batch = min(window_size, num_packets - delivered)
            self.server_ui.log_message(f"Sending window of {batch} packets")
            window_packets = {}

            # Send window of packets
            for i in range(batch):
                p_seq = seq + i
                packet = Packet(DATA, p_seq, f"Data packet {p_seq}")
                if random.random() < self.packet_error_rate:
                    packet.is_corrupt = True
                    self.server_ui.log_message(f"Packet {p_seq} is corrupt!")
                window_packets[p_seq] = packet

            with self.event_manager.packet_processing_lock:
                for p_seq in window_packets:
                    if p_seq in ConnectionManager.received_packets:
                        del ConnectionManager.received_packets[p_seq]

            for packet in window_packets.values():
                self.server_ui.log_message(f"Queueing {packet}")
                self.animation_manager.queue_packet("server_to_client", packet)

            self.event_manager.packet_sent.set()

            # Wait for window with timeout handling
            if not self.wait_for_window(seq, batch):
                self.client_ui.log_message("Timeout waiting for window")
                return

            # Check for corrupted packets
            corrupt = []
            with self.event_manager.packet_processing_lock:
                for p_seq in range(seq, seq + batch):
                    if p_seq in ConnectionManager.received_packets and ConnectionManager.received_packets[p_seq].is_corrupt:
                        corrupt.append(p_seq)

            if corrupt:
                # Handle corrupted packets
                self.client_ui.log_message(f"Detected corrupt packets: {corrupt}")
                nack = Packet(NACK, seq, f"NACK:{','.join(map(str, corrupt))}")
                self.client_ui.log_message(f"Sending NACK for packets: {corrupt}")
                self.send_packet_from_client(nack)

                if not self.event_manager.wait_for_packet(timeout=15.0):
                    self.client_ui.log_message("Timeout waiting for NACK handling")
                    return

                # Resend only corrupted packets
                for p_seq in corrupt:
                    if p_seq in ConnectionManager.received_packets:
                        del ConnectionManager.received_packets[p_seq]
                    resend = Packet(DATA, p_seq, f"Data packet {p_seq} (resend)")
                    self.server_ui.log_message(f"Queueing resend for packet {p_seq}")
                    self.animation_manager.queue_packet("server_to_client", resend)

                self.event_manager.packet_sent.set()

                # Wait for resend with timeout handling
                if not self.wait_for_window(min(corrupt), len(corrupt)):
                    self.client_ui.log_message("Timeout waiting for resend")
                    return

            # Send ACK for the window
            ack = Packet(ACK, seq + batch - 1)
            self.client_ui.log_message(f"Sending {ack}")
            self.send_packet_from_client(ack)

            if not self.event_manager.wait_for_packet(timeout=15.0):
                self.client_ui.log_message("Timeout waiting for server to receive ACK")
                return

            self.server_ui.log_message(f"Received {ack}")
            seq += batch
            delivered += batch

        self.client_ui.log_message("All packets received successfully")
        self.server_ui.log_message("All packets delivered successfully")

    def wait_for_window(self, start_seq, count):
        """Wait for all packets in window to be received"""
        deadline = time.time() + 15.0
        while time.time() < deadline and not self.event_manager.stop_flag:
            with self.event_manager.packet_processing_lock:
                # Check if we've received all packets in window
                received_all = True
                for seq in range(start_seq, start_seq + count):
                    if seq not in ConnectionManager.received_packets:
                        received_all = False
                        break
                
                if received_all:
                    return True
                
            self.event_manager.packet_received.wait(0.2)
            self.event_manager.packet_received.clear()
        
        return False

    def close_connection(self):
        if self.client_ui.state != CONNECTED:
            return
        thread = threading.Thread(target=self.connection_closing_process, daemon=True)
        thread.start()

    def connection_closing_process(self):
        self.client_ui.set_state(CLOSING)
        self.client_ui.log_message("Initiating connection termination...")

        fin = Packet(FIN)
        self.client_ui.log_message(f"Sending {fin}")
        self.send_packet_from_client(fin)

        if not self.event_manager.wait_for_packet(timeout=15.0):
            self.client_ui.log_message("Timeout waiting for server to receive FIN")
            return

        self.server_ui.set_state(CLOSING)
        self.server_ui.log_message(f"Received {fin}")
        self.sim_sleep(0.5)

        fin_ack = Packet(FIN_ACK)
        self.server_ui.log_message(f"Sending {fin_ack}")
        self.send_packet_from_server(fin_ack)

        if not self.event_manager.wait_for_packet(timeout=15.0):
            self.server_ui.log_message("Timeout waiting for client to receive FIN-ACK")
            return

        self.client_ui.log_message(f"Received {fin_ack}")
        self.sim_sleep(0.5)

        final_ack = Packet(ACK)
        self.client_ui.log_message(f"Sending final {final_ack}")
        self.send_packet_from_client(final_ack)

        if not self.event_manager.wait_for_packet(timeout=15.0):
            self.client_ui.log_message("Timeout waiting for server to receive final ACK")
            return

        self.server_ui.log_message(f"Received final {final_ack}")
        self.sim_sleep(0.5)
        self.server_ui.log_message("Closing connection")
        self.server_ui.set_state(DISCONNECTED)

    def reset_client(self):
        """Proper client reset implementation"""
        print("Performing complete client reset...")
        
        # Stop all ongoing operations
        self.event_manager.stop_flag = True
        
        # Clear all packet state
        with self.event_manager.packet_processing_lock:
            ConnectionManager.received_packets.clear()
            ConnectionManager.expected_seq = 1
        
        # Reset UI components
        self.client_ui.set_state(DISCONNECTED)
        self.client_ui.clear_log()
        self.client_ui.log_message("Client ready for new connection")
        
        # Clear animations safely
        if hasattr(self, 'animation_manager'):
            self.animation_manager.stop_animations()
        
        # Reset connection manager state
        self.event_manager.stop_flag = False
        print("Client reset completed successfully")

    def reset_server(self):
        """Proper server reset implementation"""
        print("Performing complete server reset...")
        
        # Stop all ongoing operations
        self.event_manager.stop_flag = True
        
        # Clear all packet state
        with self.event_manager.packet_processing_lock:
            ConnectionManager.received_packets.clear()
            ConnectionManager.expected_seq = 1
        
        # Reset UI components
        self.server_ui.set_state(DISCONNECTED)
        self.server_ui.clear_log()
        self.server_ui.log_message("Server ready for new connection")
        
        # Clear animations safely
        if hasattr(self, 'animation_manager'):
            self.animation_manager.stop_animations()
        
        # Reset connection manager state
        self.event_manager.stop_flag = False
        print("Server reset completed successfully")

    def send_packet_from_client(self, packet):
        self.event_manager.packet_sent.clear()
        self.event_manager.packet_received.clear()
        self.animation_manager.queue_packet("client_to_server", packet)
        self.event_manager.packet_sent.wait(timeout=5.0)
        self.event_manager.packet_received.wait(timeout=10.0)
        

    def send_packet_from_server(self, packet):
        self.event_manager.packet_sent.clear()
        self.event_manager.packet_received.clear()
        self.animation_manager.queue_packet("server_to_client", packet)
        self.event_manager.packet_sent.wait(timeout=5.0)
        self.event_manager.packet_received.wait(timeout=10.0)

    def sim_sleep(self, seconds):
        end = time.time() + seconds
        while time.time() < end and not self.event_manager.stop_flag:
            if not self.event_manager.paused:
                time.sleep(0.05)
            else:
                time.sleep(0.1)


    def update_client_ui_state(self):
        """Force synchronization between logic and UI state"""
        def _update():
            self.client_ui.status_label.config(text=self.client_ui.state)
            if self.client_ui.state == DISCONNECTED:
                self.client_ui.connect_button.config(state=tk.NORMAL)
                self.client_ui.close_button.config(state=tk.DISABLED)
            else:
                self.client_ui.connect_button.config(state=tk.DISABLED)
                self.client_ui.close_button.config(state=tk.NORMAL)
        
        self.event_manager.queue_event(_update)