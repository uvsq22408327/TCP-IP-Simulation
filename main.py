# network_simulation.py
import socket
import time
import threading
import random
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import queue

from NetworkSimulatorGUI import NetworkSimulatorGUI





# Point d'entrée principal
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = NetworkSimulatorGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Erreur fatale de l'application: {str(e)}")
        import traceback
        traceback.print_exc()