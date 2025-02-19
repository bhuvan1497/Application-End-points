import requests
import time
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread, Event

# Global variables
monitoring = False
stop_event = Event()

# Define RAG thresholds
RAG_THRESHOLDS = {
    "Green": 1.0,
    "Amber": 3.0,
    "Red": float('inf')
}

# Function to get RAG status
def get_rag_status(response_time):
    for status, threshold in RAG_THRESHOLDS.items():
        if response_time <= threshold:
            return status
    return "Error"

# Function to monitor URL
def monitor_url(url, duration_sec):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=duration_sec)
        end_time = time.time()
        response_time = end_time - start_time
        rag_status = get_rag_status(response_time)
        return response_time, rag_status
    except requests.RequestException as e:
        return None, f"Error: {e}"

# Monitoring loop
def monitoring_loop(url, duration_sec, interval_sec):
    global monitoring
    while monitoring and not stop_event.is_set():
        response_time, rag_status = monitor_url(url, duration_sec)
        if response_time is not None:
            result_tree.insert("", "end", values=(f"Request", f"{response_time:.2f}s", rag_status))
        else:
            result_tree.insert("", "end", values=(f"Request", "Error", rag_status))
        time.sleep(interval_sec)

# Start monitoring
def start_monitoring():
    global monitoring, stop_event
    url = url_entry.get()
    duration_sec = int(duration_entry.get())
    interval_sec = int(interval_entry.get())

    if not url:
        messagebox.showerror("Error", "Please enter a URL.")
        return

    if not duration_sec or duration_sec <= 0:
        messagebox.showerror("Error", "Please enter a valid duration.")
        return

    if not interval_sec or interval_sec <= 0:
        messagebox.showerror("Error", "Please enter a valid interval.")
        return

    result_tree.delete(*result_tree.get_children())
    monitoring = True
    stop_event.clear()
    Thread(target=monitoring_loop, args=(url, duration_sec, interval_sec), daemon=True).start()

    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

# Stop monitoring
def stop_monitoring():
    global monitoring, stop_event
    monitoring = False
    stop_event.set()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# Create the main window
root = tk.Tk()
root.title("URL Response Time Monitor")
root.geometry("600x400")
root.configure(bg="#f4f4f9")

# URL input
tk.Label(root, text="Enter URL:", bg="#f4f4f9", fg="#333", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="w")
url_entry = tk.Entry(root, width=50, font=("Arial", 12))
url_entry.grid(row=0, column=1, padx=10, pady=5)

# Duration input
tk.Label(root, text="Duration (seconds):", bg="#f4f4f9", fg="#333", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=5, sticky="w")
duration_entry = tk.Entry(root, width=10, font=("Arial", 12))
duration_entry.insert(0, "5")
duration_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

# Interval input
tk.Label(root, text="Interval (seconds):", bg="#f4f4f9", fg="#333", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=5, sticky="w")
interval_entry = tk.Entry(root, width=10, font=("Arial", 12))
interval_entry.insert(0, "1")
interval_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

# Buttons
start_button = tk.Button(root, text="Start Monitoring", command=start_monitoring, bg="#28a745", fg="white", font=("Arial", 12))
start_button.grid(row=3, column=0, padx=10, pady=10)

stop_button = tk.Button(root, text="Stop Monitoring", command=stop_monitoring, bg="#dc3545", fg="white", font=("Arial", 12), state=tk.DISABLED)
stop_button.grid(row=3, column=1, padx=10, pady=10)

# Results table
result_tree = ttk.Treeview(root, columns=("Request", "Response Time", "Status"), show="headings", height=10)
result_tree.heading("Request", text="Request")
result_tree.heading("Response Time", text="Response Time")
result_tree.heading("Status", text="Status")
result_tree.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Run the application
root.mainloop()