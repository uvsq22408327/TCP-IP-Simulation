from packet import Packet
from constants import *
import socket
import time
import threading
import queue

class Server:
    def __init__(self, host=LOCALHOST, port=SERVER_PORT):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.client_socket = None
        self.client_address = None
        self.log_queue = queue.Queue()
        
    def log(self, message):
        self.log_queue.put(f"[SERVER] {message}")
        print(f"[SERVER] {message}")
        
    def start(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            self.running = True
            
            self.log(f"Serveur démarré sur {self.host}:{self.port}")
            
            # Lancement du thread d'écoute
            self.listen_thread = threading.Thread(target=self.listen_for_connections)
            self.listen_thread.daemon = True
            self.listen_thread.start()
            
            return True
            
        except Exception as e:
            self.log(f"Erreur lors du démarrage du serveur: {str(e)}")
            return False
    
    def listen_for_connections(self):
        while self.running:
            try:
                self.log("En attente de connexions...")
                client_socket, client_address = self.socket.accept()
                self.log(f"Nouvelle connexion de {client_address}")
                
                # Traitement de la connexion dans un thread séparé
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    self.log(f"Erreur d'acceptation de connexion: {str(e)}")
                    time.sleep(1)  # Évite une boucle trop rapide en cas d'erreur
    
    def handle_client(self, client_socket, client_address):
        self.client_socket = client_socket
        self.client_address = client_address
        
        try:
            # Étape 1: Ouverture de la connexion
            # Attente du SYN
            data = client_socket.recv(DEFAULT_PACKET_SIZE)
            packet = Packet.from_bytes(data)
            
            if packet and packet.packet_type == SYN:
                self.log(f"Reçu {packet} de {client_address}")
                
                # Envoi du SYN_ACK
                syn_ack_packet = Packet(SYN_ACK)
                client_socket.sendall(syn_ack_packet.to_bytes())
                self.log(f"Envoi {syn_ack_packet} à {client_address}")
                
                # Étape 2: Transfert des données
                # Attente de la demande de données
                while True:
                    data = client_socket.recv(DEFAULT_PACKET_SIZE)
                    if not data:
                        break
                        
                    packet = Packet.from_bytes(data)
                    if not packet:
                        continue
                        
                    self.log(f"Reçu {packet} de {client_address}")
                    
                    # Si c'est une demande de données
                    if packet.packet_type == DATA and packet.seq_num == 0:
                        try:
                            num_packets = int(packet.data)
                            window_size = packet.window_size or DEFAULT_WINDOW_SIZE
                            self.log(f"Demande de {num_packets} paquets, fenêtre de taille {window_size}")
                            
                            self.send_data_packets(client_socket, num_packets, window_size)
                        except ValueError:
                            self.log(f"Valeur invalide pour num_packets: {packet.data}")
                    
                    # Si c'est une demande de fermeture
                    elif packet.packet_type == FIN:
                        self.log("Demande de fermeture de connexion reçue")
                        
                        # Envoi du FIN_ACK
                        fin_ack_packet = Packet(FIN_ACK)
                        client_socket.sendall(fin_ack_packet.to_bytes())
                        self.log(f"Envoi {fin_ack_packet} à {client_address}")
                        
                        # Attente du ACK final
                        try:
                            data = client_socket.recv(DEFAULT_PACKET_SIZE)
                            ack_packet = Packet.from_bytes(data)
                            
                            if ack_packet and ack_packet.packet_type == ACK:
                                self.log(f"Reçu ACK final de {client_address}")
                            else:
                                self.log(f"Reçu paquet inattendu au lieu de ACK: {ack_packet}")
                        except:
                            self.log("Pas reçu de ACK final, fermeture quand même")
                        
                        break
            else:
                self.log(f"Paquet inattendu reçu au lieu de SYN: {packet}")
                
        except Exception as e:
            self.log(f"Erreur de traitement du client {client_address}: {str(e)}")
        finally:
            self.log(f"Fermeture de la connexion avec {client_address}")
            client_socket.close()
            self.client_socket = None
            self.client_address = None
    
    def send_data_packets(self, client_socket, num_packets, window_size):
        seq_num = 1
        packets_sent = 0
        window_base = 1
        window_next = 1
        in_flight = {}  # Paquets envoyés mais pas encore acquittés
        
        while packets_sent < num_packets:
            # Envoi des paquets dans la fenêtre actuelle
            while window_next < window_base + window_size and window_next <= num_packets:
                # Création d'un paquet de données avec un numéro de séquence
                data_packet = Packet(DATA, seq_num=window_next, data=f"Data-{window_next}")
                client_socket.sendall(data_packet.to_bytes())
                self.log(f"Envoi {data_packet} à {self.client_address}")
                
                # Ajout à la liste des paquets en vol
                in_flight[window_next] = data_packet
                window_next += 1
            
            # Attente des ACK/NACK
            try:
                data = client_socket.recv(DEFAULT_PACKET_SIZE)
                response = Packet.from_bytes(data)
                
                if not response:
                    continue
                    
                self.log(f"Reçu {response} de {self.client_address}")
                
                if response.packet_type == ACK:
                    # Mise à jour de la fenêtre
                    acked_seq = response.seq_num
                    if acked_seq in in_flight:
                        del in_flight[acked_seq]
                        packets_sent += 1
                        
                        # Avance de la fenêtre si possible
                        if acked_seq == window_base:
                            # Trouve le prochain numéro de séquence non acquitté
                            while window_base not in in_flight and window_base < window_next:
                                window_base += 1
                            
                    self.log(f"Fenêtre: base={window_base}, next={window_next}, in_flight={len(in_flight)}")
                
                elif response.packet_type == NACK:
                    # Retransmission du paquet demandé
                    nacked_seq = response.seq_num
                    if nacked_seq in in_flight:
                        retransmit_packet = in_flight[nacked_seq]
                        client_socket.sendall(retransmit_packet.to_bytes())
                        self.log(f"Retransmission {retransmit_packet} à {self.client_address}")
                    else:
                        self.log(f"NACK reçu pour un paquet inconnu: {nacked_seq}")
            
            except socket.timeout:
                # Retransmission de tous les paquets en vol si timeout
                self.log("Timeout - retransmission des paquets en vol")
                for seq, packet in in_flight.items():
                    client_socket.sendall(packet.to_bytes())
                    self.log(f"Retransmission (timeout) {packet} à {self.client_address}")
        
        self.log(f"Tous les {num_packets} paquets ont été envoyés et acquittés")
    
    def stop(self):
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.log("Serveur arrêté")