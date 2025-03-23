from packet import Packet
from constants import *
import socket
import time
import threading
import random
import queue

class Client:
    def __init__(self, server_address, server_port, timeout=DEFAULT_TIMEOUT, window_size=DEFAULT_WINDOW_SIZE):
        self.server_address = server_address
        self.server_port = server_port
        self.socket = None
        self.timeout = timeout
        self.window_size = window_size
        self.connected = False
        self.log_queue = queue.Queue()
        
    def log(self, message):
        self.log_queue.put(f"[CLIENT] {message}")
        print(f"[CLIENT] {message}")
        
    def connect(self):
        try:
            # Création du socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            
            # Étape 1: Ouverture de la connexion
            self.log(f"Connexion au serveur {self.server_address}:{self.server_port}")
            self.socket.connect((self.server_address, self.server_port))
            
            # Envoi du paquet SYN
            syn_packet = Packet(SYN)
            self.socket.sendall(syn_packet.to_bytes())
            self.log(f"Envoi du paquet {syn_packet}")
            
            # Attente du SYN_ACK
            response = self.socket.recv(DEFAULT_PACKET_SIZE)
            syn_ack_packet = Packet.from_bytes(response)
            
            if syn_ack_packet and syn_ack_packet.packet_type == SYN_ACK:
                self.log(f"Reçu {syn_ack_packet}")
                self.connected = True
                return True
            else:
                self.log("Échec de la connexion: pas de SYN_ACK reçu")
                self.socket.close()
                return False
                
        except socket.timeout:
            self.log("Timeout lors de la tentative de connexion")
            if self.socket:
                self.socket.close()
            return False
        except Exception as e:
            self.log(f"Erreur lors de la connexion: {str(e)}")
            if self.socket:
                self.socket.close()
            return False
    
    def request_data(self, num_packets):
        if not self.connected or not self.socket:
            self.log("Pas de connexion active")
            return False
            
        try:
            # Étape 2: Transfert des données
            # Envoi de la demande de données avec la taille de fenêtre
            request_packet = Packet(DATA, seq_num=0, data=str(num_packets), window_size=self.window_size)
            self.socket.sendall(request_packet.to_bytes())
            self.log(f"Demande de {num_packets} paquets, fenêtre de taille {self.window_size}")
            
            packets_received = 0
            expected_seq = 1
            
            # Réception des données
            while packets_received < num_packets:
                self.log(f"En attente du paquet {expected_seq}/{num_packets}")
                data = self.socket.recv(DEFAULT_PACKET_SIZE)
                packet = Packet.from_bytes(data)
                
                if not packet:
                    self.log("Paquet invalide reçu")
                    continue
                    
                self.log(f"Reçu {packet}")
                
                # Simulation d'une erreur aléatoire (environ 10% de chance)
                if random.random() < 0.1:
                    self.log(f"Simulation d'une erreur pour le paquet {packet.seq_num}")
                    nack = Packet(NACK, seq_num=packet.seq_num)
                    self.socket.sendall(nack.to_bytes())
                    self.log(f"Envoi {nack}")
                else:
                    # Si le numéro de séquence est correct
                    if packet.seq_num == expected_seq:
                        ack = Packet(ACK, seq_num=packet.seq_num)
                        self.socket.sendall(ack.to_bytes())
                        self.log(f"Envoi {ack}")
                        expected_seq += 1
                        packets_received += 1
                    else:
                        # Si c'est une retransmission
                        if packet.seq_num < expected_seq:
                            ack = Packet(ACK, seq_num=packet.seq_num)
                            self.socket.sendall(ack.to_bytes())
                            self.log(f"Duplicate - Envoi {ack}")
                        else:
                            # Si on a reçu un paquet trop en avance
                            nack = Packet(NACK, seq_num=expected_seq)
                            self.socket.sendall(nack.to_bytes())
                            self.log(f"Out of order - Envoi {nack}")
            
            self.log("Tous les paquets ont été reçus")
            return True
            
        except socket.timeout:
            self.log("Timeout lors de la réception des données")
            return False
        except Exception as e:
            self.log(f"Erreur lors de la réception des données: {str(e)}")
            return False
    
    def close_connection(self):
        if not self.connected or not self.socket:
            self.log("Pas de connexion active à fermer")
            return
            
        try:
            # Étape 3: Fermeture de la connexion
            # Envoi du paquet FIN
            fin_packet = Packet(FIN)
            self.socket.sendall(fin_packet.to_bytes())
            self.log("Demande de fermeture de la connexion (FIN)")
            
            # Attente du FIN_ACK
            response = self.socket.recv(DEFAULT_PACKET_SIZE)
            fin_ack_packet = Packet.from_bytes(response)
            
            if fin_ack_packet and fin_ack_packet.packet_type == FIN_ACK:
                self.log(f"Reçu {fin_ack_packet}")
                
                # Envoi du ACK final
                ack_packet = Packet(ACK)
                self.socket.sendall(ack_packet.to_bytes())
                self.log("Envoi du ACK final")
                
                # Temporisateur de 30 secondes
                self.log(f"Attente de {CLOSE_WAIT_TIMEOUT} secondes avant fermeture complète")
                time.sleep(CLOSE_WAIT_TIMEOUT)
                
            self.log("Fermeture de la connexion")
            self.socket.close()
            self.connected = False
            
        except Exception as e:
            self.log(f"Erreur lors de la fermeture: {str(e)}")
            if self.socket:
                self.socket.close()
            self.connected = False