# network_ui.py
# Handles the network visualization UI

import tkinter as tk

class NetworkUI:
    def __init__(self, parent_frame, event_manager):
        self.frame = tk.Frame(parent_frame, width=200)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.event_manager = event_manager
        
        # Initialize UI components
        self.setup_ui()
        
        # Animation variables
        self.active_animations = []
    
    def setup_ui(self):
        # Canvas for packet animation
        self.canvas = tk.Canvas(self.frame, width=200, height=400, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Speed control slider
        speed_frame = tk.Frame(self.frame)
        speed_frame.pack(fill=tk.X, pady=5)
        tk.Label(speed_frame, text="Simulation Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_slider = tk.Scale(speed_frame, from_=0.1, to=3.0, resolution=0.1, 
                                   orient=tk.HORIZONTAL, variable=self.speed_var)
        self.speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Pause/Resume button
        self.pause_button = tk.Button(self.frame, text="Pause", command=self.on_toggle_pause)
        self.pause_button.pack(pady=5)
    
    def on_toggle_pause(self):
        """Handle pause button click"""
        paused = self.event_manager.toggle_pause()
        self.pause_button.config(text="Resume" if paused else "Pause")
    
    def get_simulation_speed(self):
        """Get the current simulation speed"""
        return self.speed_var.get()
    
    def create_packet_animation(self, packet, direction):
        """Create a new packet animation on the canvas"""
        # This will be implemented by the animation manager
        pass
    
    def clear_animations(self):
        """Clear all active animations"""
        def _clear():
            for animation in self.active_animations:
                self.canvas.delete(animation.get("packet_obj"))
                self.canvas.delete(animation.get("text_obj"))
            self.active_animations = []
        
        self.event_manager.queue_event(_clear)