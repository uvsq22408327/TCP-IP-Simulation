import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from client import Client
from constants import DEFAULT_TIMEOUT, DEFAULT_WINDOW_SIZE, LOCALHOST, SERVER_PORT
from server import Server

class NetworkSimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulateur de Communication Réseau")
        self.root.geometry("800x600")
        
        self.server = None
        self.client = None
        
        self.setup_ui()
    
    def setup_ui(self):
        # Création des onglets
        self.tab_control = ttk.Notebook(self.root)
        
        self.tab_server = ttk.Frame(self.tab_control)
        self.tab_client = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.tab_server, text="Serveur")
        self.tab_control.add(self.tab_client, text="Client")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Configuration de l'onglet Serveur
        self.setup_server_tab()
        
        # Configuration de l'onglet Client
        self.setup_client_tab()
        
        # Configuration du rafraîchissement des logs
        self.root.after(100, self.update_logs)
    
    def setup_server_tab(self):
        frame = ttk.Frame(self.tab_server, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Zone de paramètres
        param_frame = ttk.LabelFrame(frame, text="Paramètres du Serveur", padding=10)
        param_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(param_frame, text="Adresse:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.server_host_var = tk.StringVar(value=LOCALHOST)
        ttk.Entry(param_frame, textvariable=self.server_host_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Port:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.server_port_var = tk.IntVar(value=SERVER_PORT)
        ttk.Entry(param_frame, textvariable=self.server_port_var, width=6).grid(row=0, column=3, padx=5, pady=5)
        
        # Boutons de contrôle
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        self.start_server_btn = ttk.Button(control_frame, text="Démarrer le Serveur", command=self.start_server)
        self.start_server_btn.pack(side="left", padx=5)
        
        self.stop_server_btn = ttk.Button(control_frame, text="Arrêter le Serveur", command=self.stop_server, state="disabled")
        self.stop_server_btn.pack(side="left", padx=5)
        
        # Zone de logs
        log_frame = ttk.LabelFrame(frame, text="Logs du Serveur", padding=10)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.server_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.server_log.pack(fill="both", expand=True)
        self.server_log.config(state="disabled")
    
    def setup_client_tab(self):
        frame = ttk.Frame(self.tab_client, padding=10)
        frame.pack(fill="both", expand=True)
        
        # Zone de paramètres
        param_frame = ttk.LabelFrame(frame, text="Paramètres du Client", padding=10)
        param_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(param_frame, text="Serveur:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.client_host_var = tk.StringVar(value=LOCALHOST)
        ttk.Entry(param_frame, textvariable=self.client_host_var, width=15).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Port:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.client_port_var = tk.IntVar(value=SERVER_PORT)
        ttk.Entry(param_frame, textvariable=self.client_port_var, width=6).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Timeout:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.timeout_var = tk.IntVar(value=DEFAULT_TIMEOUT)
        ttk.Entry(param_frame, textvariable=self.timeout_var, width=6).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Taille de fenêtre:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.window_size_var = tk.IntVar(value=DEFAULT_WINDOW_SIZE)
        ttk.Entry(param_frame, textvariable=self.window_size_var, width=6).grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(param_frame, text="Nombre de paquets:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.num_packets_var = tk.IntVar(value=10)
        ttk.Entry(param_frame, textvariable=self.num_packets_var, width=6).grid(row=2, column=1, padx=5, pady=5)
        
        # Boutons de contrôle
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        self.connect_btn = ttk.Button(control_frame, text="Connecter", command=self.connect_client)
        self.connect_btn.pack(side="left", padx=5)
        
        self.request_data_btn = ttk.Button(control_frame, text="Demander des Données", command=self.request_data, state="disabled")
        self.request_data_btn.pack(side="left", padx=5)
        
        self.close_conn_btn = ttk.Button(control_frame, text="Fermer la Connexion", command=self.close_connection, state="disabled")
        self.close_conn_btn.pack(side="left", padx=5)
        
        # Zone de logs
        log_frame = ttk.LabelFrame(frame, text="Logs du Client", padding=10)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.client_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=15)
        self.client_log.pack(fill="both", expand=True)
        self.client_log.config(state="disabled")
    
    def start_server(self):
        try:
            host = self.server_host_var.get()
            port = self.server_port_var.get()
            
            self.server = Server(host, port)
            if self.server.start():
                self.start_server_btn.config(state="disabled")
                self.stop_server_btn.config(state="normal")
                self.append_server_log("Serveur démarré avec succès")
            else:
                self.append_server_log("Échec du démarrage du serveur")
                self.server = None
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du démarrage du serveur: {str(e)}")
            self.server = None
    
    def stop_server(self):
        if self.server:
            self.server.stop()
            self.server = None
            self.start_server_btn.config(state="normal")
            self.stop_server_btn.config(state="disabled")
            self.append_server_log("Serveur arrêté")
    
    def connect_client(self):
        try:
            host = self.client_host_var.get()
            port = self.client_port_var.get()
            timeout = self.timeout_var.get()
            window_size = self.window_size_var.get()
            
            self.client = Client(host, port, timeout, window_size)
            
            # Lancement de la connexion dans un thread séparé
            self.connect_btn.config(state="disabled")
            
            def connect_thread():
                if self.client.connect():
                    self.root.after(0, lambda: self.request_data_btn.config(state="normal"))
                    self.root.after(0, lambda: self.close_conn_btn.config(state="normal"))
                else:
                    self.root.after(0, lambda: self.connect_btn.config(state="normal"))
                    self.root.after(0, lambda: messagebox.showerror("Erreur", "Échec de la connexion au serveur"))
                    self.client = None
            
            threading.Thread(target=connect_thread).start()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la connexion: {str(e)}")
            self.connect_btn.config(state="normal")
            self.client = None
    
    def request_data(self):
        if not self.client:
            messagebox.showerror("Erreur", "Pas de client connecté")
            return
            
        try:
            num_packets = self.num_packets_var.get()
            
            # Désactivation des boutons pendant l'opération
            self.request_data_btn.config(state="disabled")
            self.close_conn_btn.config(state="disabled")
            
            def request_thread():
                success = self.client.request_data(num_packets)
                self.root.after(0, lambda: self.request_data_btn.config(state="normal"))
                self.root.after(0, lambda: self.close_conn_btn.config(state="normal"))
                
                if not success:
                    self.root.after(0, lambda: messagebox.showerror("Erreur", "Échec de la demande de données"))
            
            threading.Thread(target=request_thread).start()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la demande de données: {str(e)}")
            self.request_data_btn.config(state="normal")
            self.close_conn_btn.config(state="normal")
    
    def close_connection(self):
        if not self.client:
            messagebox.showerror("Erreur", "Pas de client connecté")
            return
            
        try:
            # Désactivation des boutons pendant l'opération
            self.request_data_btn.config(state="disabled")
            self.close_conn_btn.config(state="disabled")
            
            def close_thread():
                self.client.close_connection()
                self.client = None
                self.root.after(0, lambda: self.connect_btn.config(state="normal"))
            
            threading.Thread(target=close_thread).start()
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la fermeture: {str(e)}")
            self.connect_btn.config(state="normal")
            self.client = None
    
    def append_server_log(self, message):
        self.server_log.config(state="normal")
        self.server_log.insert(tk.END, message + "\n")
        self.server_log.see(tk.END)
        self.server_log.config(state="disabled")
    
    def append_client_log(self, message):
        self.client_log.config(state="normal")
        self.client_log.insert(tk.END, message + "\n")
        self.client_log.see(tk.END)
        self.client_log.config(state="disabled")
    
    def update_logs(self):
        # Mise à jour des logs du serveur
        if self.server and not self.server.log_queue.empty():
            while not self.server.log_queue.empty():
                message = self.server.log_queue.get()
                self.append_server_log(message)
        
        # Mise à jour des logs du client
        if self.client and not self.client.log_queue.empty():
            while not self.client.log_queue.empty():
                message = self.client.log_queue.get()
                self.append_client_log(message)
        
        # Programmation de la prochaine mise à jour
        self.root.after(100, self.update_logs)