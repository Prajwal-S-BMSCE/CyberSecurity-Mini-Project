import socket
import tkinter as tk
from tkinter import messagebox
import threading
import sys

# --- CONFIGURATION ---
LISTENING_PORT = 5000
ADMIN_PASSWORD = "admin123"  # <--- The only way to unlock

class LockScreenApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SECURITY ALERT")
        
        # 1. Fullscreen & Topmost (Covers everything)
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#1a0505') # Dark Red/Black
        
        # 2. Disable Closing
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)

        # --- UI ELEMENTS ---
        tk.Label(self.root, text="⚠ SECURITY LOCKDOWN ⚠", 
                 font=("Arial", 50, "bold"), fg="red", bg='#1a0505').pack(pady=(100, 20))
        
        tk.Label(self.root, text="MALICIOUS ACTIVITY DETECTED ON THIS ENDPOINT", 
                 font=("Courier", 20, "bold"), fg="white", bg='#1a0505').pack(pady=10)

        tk.Label(self.root, text="System isolated by SOC.\nContact Administrator to unlock.", 
                 font=("Arial", 14), fg="#cccccc", bg='#1a0505').pack(pady=20)

        # Password Entry
        tk.Label(self.root, text="Enter Admin Override Password:", 
                 font=("Arial", 12), fg="white", bg='#1a0505').pack(pady=(50, 5))
        
        self.password_entry = tk.Entry(self.root, font=("Arial", 20), show="*", width=20)
        self.password_entry.pack(pady=10)
        self.password_entry.bind('<Return>', self.check_password)

        # Unlock Button
        tk.Button(self.root, text="UNLOCK SYSTEM", command=self.check_password, 
                  font=("Arial", 15, "bold"), bg="red", fg="white", width=20).pack(pady=20)

    def disable_event(self):
        pass

    def check_password(self, event=None):
        entered_pass = self.password_entry.get()
        if entered_pass == ADMIN_PASSWORD:
            messagebox.showinfo("Access Granted", "System Unlocked. Incident Logged.")
            self.root.destroy()
        else:
            messagebox.showwarning("Access Denied", "INCORRECT PASSWORD!\nThis attempt has been logged.")
            self.password_entry.delete(0, 'end')

    def run(self):
        self.root.mainloop()

def start_listener():
    """Listens for the 'LOCK' signal from Admin"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', LISTENING_PORT))
    server_socket.listen(5)
    
    print(f"🛡️  GUARD ACTIVE. Listening on Port {LISTENING_PORT}...")

    while True:
        try:
            client, addr = server_socket.accept()
            print(f"⚠️ Signal received from: {addr}")
            data = client.recv(1024).decode()
            
            if data == "LOCK_NOW":
                print("🔒 LOCKING SCREEN...")
                # Use threading to ensure the GUI opens without freezing the network listener
                gui_thread = threading.Thread(target=lambda: LockScreenApp().run())
                gui_thread.start()
                
            client.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_listener()
