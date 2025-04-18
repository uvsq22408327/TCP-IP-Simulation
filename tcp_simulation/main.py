# main_app.py
# Main entry point for the TCP simulation application

import tkinter as tk
from event_manager import EventManager
from client_ui import ClientUI
from server_ui import ServerUI
from network_ui import NetworkUI
from animation_manager import AnimationManager
from connection_manager import ConnectionManager

class TCPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP Protocol Simulation")
        self.root.geometry("1000x600")

        # Setup shared event manager
        self.event_manager = EventManager()

        # Top-level frame
        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # UI Components
        self.client_ui = ClientUI(main_frame, self.event_manager)
        self.network_ui = NetworkUI(main_frame, self.event_manager)
        self.server_ui = ServerUI(main_frame, self.event_manager)

        # Logic/animation manager
        self.animation_manager = AnimationManager(self.network_ui, self.event_manager)

        # Connection manager (core simulation logic)
        self.connection_manager = ConnectionManager(
            self.client_ui, self.server_ui,
            self.animation_manager, self.event_manager, self.network_ui
        )

        # Start animation thread
        self.animation_manager.start_animation_thread()

        # Start event polling loop
        self.schedule_event_processing()

    def schedule_event_processing(self):
        """Continuously process UI events"""
        try:
            self.event_manager.process_events()
            self.root.after(10, self.schedule_event_processing)
        except Exception as e:
            print(f"Error in event processing: {e}")
            self.root.after(10, self.schedule_event_processing)

if __name__ == "__main__":
    root = tk.Tk()
    app = TCPApp(root)
    root.mainloop()