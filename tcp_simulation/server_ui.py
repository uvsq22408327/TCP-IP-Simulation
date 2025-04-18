# server_ui.py
# Handles the server side of the UI

import tkinter as tk
from constants import DISCONNECTED

class ServerUI:
    def __init__(self, parent_frame, event_manager):
        self.frame = tk.LabelFrame(parent_frame, text="Server", padx=10, pady=10, width=400)
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
        server_scroll = tk.Scrollbar(self.log)
        server_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log.config(yscrollcommand=server_scroll.set)
        server_scroll.config(command=self.log.yview)
        
        # Controls
        controls_frame = tk.Frame(self.frame)
        controls_frame.pack(fill=tk.X, pady=10)
        
        # Reset button
        self.reset_button = tk.Button(controls_frame, text="Reset Server", command=self.on_reset)
        self.reset_button.pack(pady=5)
    
    def update_status(self):
        """Update the status display based on current state"""
        def _update():
            self.status_label.config(text=self.state)
            if self.state == DISCONNECTED:
                self.status_label.config(fg="red")
            elif self.state == "CONNECTED":
                self.status_label.config(fg="green")
            else:
                self.status_label.config(fg="orange")
        
        self.event_manager.queue_event(_update)
    
    def log_message(self, message):
        """Add message to the server log"""
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
        """Update the server state and UI"""
        self.state = new_state
        self.update_status()
    
    # Event handlers - will be connected to actual logic by Controller
    def on_reset(self):
        """Handle reset button click"""
        if hasattr(self, 'reset_handler'):
            self.reset_handler()