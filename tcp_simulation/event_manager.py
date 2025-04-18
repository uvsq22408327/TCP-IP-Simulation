# event_manager.py
# Manages events for UI updates and simulation synchronization

import queue
import threading
import time  
class EventManager:
    def __init__(self):
        self.event_queue = queue.Queue()
        self.packet_received = threading.Event()  # Event for packet reception
        self.packet_sent = threading.Event()      # Event for packet sending
        self.packet_processing_complete = threading.Event()
        self.packet_processing_lock = threading.Lock()
        self.lock = threading.Lock()              # General purpose lock
        self.stop_flag = False
        self.paused = False

    def queue_event(self, event_func):
        """Add an event to be processed in the main thread"""
        self.event_queue.put(event_func)
    
    def process_events(self, count=10):
        """Process a batch of events from the queue"""
        try:
            for _ in range(count):  # Process a limited number of events per cycle
                if not self.event_queue.empty():
                    event = self.event_queue.get_nowait()
                    event()
        except queue.Empty:
            pass
    
    def wait_for_packet(self, timeout=None):
        """Wait for a packet to be received"""
        start_time = time.time()  # Changed from threading.time.time()
        while True:
            if self.packet_received.is_set():
                self.packet_received.clear()
                return True
            
            if timeout and (time.time() - start_time) > timeout:
                return False
                
            time.sleep(0.1)
            
            if self.stop_flag:
                return False
    
    def toggle_pause(self):
        """Toggle the pause state"""
        self.paused = not self.paused
        return self.paused
    
    def reset(self):
        """Complete event manager reset"""
        with self.lock:
            self.stop_flag = False
            self.paused = False
            self.packet_received.clear()
            self.packet_sent.clear()
            
            # Clear the event queue
            while not self.event_queue.empty():
                try:
                    self.event_queue.get_nowait()
                except queue.Empty:
                    break