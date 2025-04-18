# client_ui.py
# Handles the client side of the UI

import tkinter as tk
from constants import DISCONNECTED, CONNECTED

class ClientUI:
    def __init__(self, parent_frame, event_manager):
        self.frame = tk.LabelFrame(parent_frame, text="Client", padx=10, pady=10, width=400)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.event_manager = event_manager
        
        # State variables
        self.state = DISCONNECTED
        
        # Initialize UI components
        self.setup_ui()
    
    def setup_ui(self):
        # Status display
        status_frame = tk.Frame(self.frame)
        status_frame.pack(fill=tk.X, pady=5)
        tk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_label = tk.Label(status_frame, text=DISCONNECTED, fg="red")
        self.status_label.pack(side=tk.LEFT)
        
        # Log display
        log_frame = tk.Frame(self.frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        tk.Label(log_frame, text="Log:").pack(anchor=tk.W)
        self.log = tk.Text(log_frame, height=10, width=40)
        self.log.pack(fill=tk.BOTH, expand=True)
        client_scroll = tk.Scrollbar(self.log)
        client_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log.config(yscrollcommand=client_scroll.set)
        client_scroll.config(command=self.log.yview)
        
        # Controls
        controls_frame = tk.Frame(self.frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Number of packets
        packet_frame = tk.Frame(controls_frame)
        packet_frame.pack(fill=tk.X, pady=2)
        tk.Label(packet_frame, text="Number of packets:").pack(side=tk.LEFT)
        self.num_packets_var = tk.StringVar(value="5")
        tk.Entry(packet_frame, textvariable=self.num_packets_var, width=5).pack(side=tk.LEFT)

        # Window size
        window_frame = tk.Frame(controls_frame)
        window_frame.pack(fill=tk.X, pady=2)
        tk.Label(window_frame, text="Window size:").pack(side=tk.LEFT)
        self.window_size_var = tk.StringVar(value="3")
        tk.Entry(window_frame, textvariable=self.window_size_var, width=5).pack(side=tk.LEFT)
        
        # Error rate
        error_frame = tk.Frame(controls_frame)
        error_frame.pack(fill=tk.X, pady=2)
        tk.Label(error_frame, text="Error rate (%):").pack(side=tk.LEFT)
        self.error_rate_var = tk.StringVar(value="10")
        tk.Entry(error_frame, textvariable=self.error_rate_var, width=5).pack(side=tk.LEFT)
        
        # Connection buttons
        button_frame = tk.Frame(controls_frame)
        button_frame.pack(fill=tk.X, pady=5)
        self.connect_button = tk.Button(button_frame, text="Start Connection", command=self.on_connect)
        self.connect_button.pack(side=tk.LEFT, padx=5)
        self.close_button = tk.Button(button_frame, text="Close Connection", command=self.on_close, state=tk.DISABLED)
        self.close_button.pack(side=tk.LEFT, padx=5)
        self.reset_button = tk.Button(button_frame, text="Reset Client", command=self.on_reset)
        self.reset_button.pack(side=tk.LEFT, padx=5)
    
    def update_status(self):
        """Update the status display based on current state"""
        def _update():
            self.status_label.config(text=self.state)
            if self.state == DISCONNECTED:
                self.status_label.config(fg="red")
                self.connect_button.config(state=tk.NORMAL)
                self.close_button.config(state=tk.DISABLED)
            elif self.state == CONNECTED:
                self.status_label.config(fg="green")
                self.connect_button.config(state=tk.DISABLED)
                self.close_button.config(state=tk.NORMAL)
            else:
                self.status_label.config(fg="orange")
                self.connect_button.config(state=tk.DISABLED)
                self.close_button.config(state=tk.DISABLED)
        
        self.event_manager.queue_event(_update)
    
    def log_message(self, message):
        """Add message to the client log"""
        def _log():
            self.log.insert(tk.END, f"{message}\n")
            self.log.see(tk.END)
        
        self.event_manager.queue_event(_log)
    
    def clear_log(self):
        """Clear the log contents"""
        def _clear():
            self.log.delete(1.0, tk.END)
        
        self.event_manager.queue_event(_clear)
    
    def set_state(self, new_state):
        """Update the client state and UI"""
        self.state = new_state
        self.update_status()
    
    # Event handlers - these will be connected to the actual logic by the Controller
    def on_connect(self):
        """Handle connection button click"""
        if hasattr(self, 'connection_handler'):
            self.connection_handler()
        
    def on_close(self):
        """Handle close connection button click"""
        if hasattr(self, 'close_handler'):
            self.close_handler()
            
    def on_reset(self):
        """Handle reset button click"""
        if hasattr(self, 'reset_handler'):
            self.reset_handler()
    
    # Getters for configuration values
    def get_packet_count(self):
        try:
            return int(self.num_packets_var.get())
        except ValueError:
            return 5  # Default value
    
    def get_window_size(self):
        try:
            return int(self.window_size_var.get())
        except ValueError:
            return 3  # Default value
    
    def get_error_rate(self):
        try:
            return float(self.error_rate_var.get()) / 100.0
        except ValueError:
            return 0.1  # Default value (10%)
        

def verify_state(self):
    """Ensure UI matches actual state"""
    if self.state == DISCONNECTED:
        self.connect_button.config(state=tk.NORMAL)
        self.close_button.config(state=tk.DISABLED)
    elif self.state == CONNECTED:
        self.connect_button.config(state=tk.DISABLED)
        self.close_button.config(state=tk.NORMAL)
    self.status_label.config(text=self.state)