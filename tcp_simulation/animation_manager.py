# animation_manager.py
# Manages the network packet animations

import random
import threading
import time
import queue
from constants import PACKET_COLORS
from connection_manager import ConnectionManager

class AnimationManager:
    def __init__(self, network_ui, event_manager):
        self.network_ui = network_ui
        self.event_manager = event_manager
        self.canvas = network_ui.canvas
        self.packet_queue = queue.Queue()
        self.active_animations = []
        self.stop_flag = False
        
        # Initialize canvas safely through event manager
        self._initialize_canvas()

    def _initialize_canvas(self):
        """Safely initialize canvas state"""
        def _clear():
            self.canvas.delete("all")
            self.active_animations = []
        self.event_manager.queue_event(_clear)

    def start_animation_thread(self):
        """Start the animation processing thread"""
        self.animation_thread = threading.Thread(target=self.animation_loop)
        self.animation_thread.daemon = True
        self.animation_thread.start()

    def animation_loop(self):
        """Main animation loop - processes queued packets and updates animations"""
        while not self.stop_flag and not self.event_manager.stop_flag:
            try:
                if not self.packet_queue.empty() and not self.event_manager.paused:
                    direction, packet = self.packet_queue.get_nowait()
                    self.animate_packet(direction, packet)
                    self.event_manager.packet_sent.set()
                
                if not self.event_manager.paused:
                    self.update_animations()
                
                time.sleep(0.05)
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Animation loop error: {e}")

    def animate_packet(self, direction, packet):
        """Start a new packet animation"""
        self.event_manager.queue_event(lambda: self._animate_packet(direction, packet))

    def _animate_packet(self, direction, packet):
        """Create packet visual elements on canvas - runs in main thread"""
        try:
            canvas_width = self.canvas.winfo_width() or 200
            canvas_height = self.canvas.winfo_height() or 400
            
            start_x = 20 if direction == "client_to_server" else canvas_width - 20
            end_x = canvas_width - 20 if direction == "client_to_server" else 20
            y_pos = random.randint(30, canvas_height - 30)
            
            color = PACKET_COLORS.get(packet.packet_type, "black")
            fill_color = "white" if packet.is_corrupt else color
            
            packet_obj = self.canvas.create_oval(
                start_x - 15, y_pos - 15,
                start_x + 15, y_pos + 15,
                outline=color, fill=fill_color, width=2
            )
            
            text = f"{packet.packet_type}\n{packet.seq_num}" if packet.seq_num else packet.packet_type
            text_obj = self.canvas.create_text(start_x, y_pos, text=text, font=("Arial", 8))
            
            with self.event_manager.lock:
                self.active_animations.append({
                    "packet_obj": packet_obj,
                    "text_obj": text_obj,
                    "start_x": start_x,
                    "end_x": end_x,
                    "y_pos": y_pos,
                    "progress": 0.0,
                    "speed": 0.02,
                    "direction": direction,
                    "packet": packet
                })
        except Exception as e:
            print(f"Packet animation failed: {e}")

    def update_animations(self):
        """Update positions of all active packet animations"""
        if not self.active_animations:
            return
            
        completed = []
        speed_factor = self.network_ui.get_simulation_speed()
        
        for i, anim in enumerate(self.active_animations):
            anim["progress"] += anim["speed"] * speed_factor
            
            if anim["progress"] >= 1.0:
                completed.append(i)
                self.event_manager.packet_received.set()
                continue
                
            new_x = anim["start_x"] + anim["progress"] * (anim["end_x"] - anim["start_x"])
            self.event_manager.queue_event(lambda i=i, new_x=new_x: self._update_animation_position(i, new_x))
            
        for i in sorted(completed, reverse=True):
            self.event_manager.queue_event(lambda i=i: self._remove_animation(i))

    def _update_animation_position(self, i, new_x):
        """Update the position of an animation object - runs in main thread"""
        try:
            if i >= len(self.active_animations):
                return
                
            anim = self.active_animations[i]
            self.canvas.coords(
                anim["packet_obj"],
                new_x - 15, anim["y_pos"] - 15,
                new_x + 15, anim["y_pos"] + 15
            )
            self.canvas.coords(anim["text_obj"], new_x, anim["y_pos"])
        except Exception as e:
            print(f"Error updating animation: {e}")

    def _remove_animation(self, i):
        """Remove a completed animation - runs in main thread"""
        try:
            if i >= len(self.active_animations):
                return
                
            anim = self.active_animations.pop(i)
            self.canvas.delete(anim["packet_obj"])
            self.canvas.delete(anim["text_obj"])
            
            packet = anim["packet"]
            if (anim["direction"] == "server_to_client" and 
                hasattr(packet, "seq_num") and 
                packet.seq_num is not None):
                with self.event_manager.packet_processing_lock:
                    ConnectionManager.received_packets[packet.seq_num] = packet
            
            self.event_manager.packet_received.set()
        except Exception as e:
            print(f"Error removing animation: {e}")

    def queue_packet(self, direction, packet):
        """Queue a packet for animation"""
        self.packet_queue.put((direction, packet))
        self.event_manager.packet_sent.clear()
        self.event_manager.packet_received.clear()

    def stop_animations(self):
        """Stop all animations and clear the canvas"""
        self.stop_flag = True
        
        # Clear packet queue
        while not self.packet_queue.empty():
            try:
                self.packet_queue.get_nowait()
            except queue.Empty:
                break
        
        # Clear canvas and animations
        def _clear_all():
            self.canvas.delete("all")
            self.active_animations = []
        self.event_manager.queue_event(_clear_all)
        
        self.stop_flag = False
        print("Animations stopped and canvas cleared")

    def clear_canvas(self):
        """Public method to clear canvas (main thread only)"""
        self.event_manager.queue_event(lambda: [
            self.canvas.delete("all"),
            setattr(self, 'active_animations', [])
        ])