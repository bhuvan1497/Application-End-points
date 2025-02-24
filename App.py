import requests
import threading
import tkinter as tk
from flask import Flask, jsonify

# Flask API for monitoring
app = Flask(__name__)
monitoring_results = {}

@app.route('/status')
def status():
    return jsonify(monitoring_results)

# Function to check URL response time
def check_url(url, interval, text_var):
    while True:
        try:
            response = requests.get(url, timeout=5)
            status, response_time = response.status_code, response.elapsed.total_seconds()
            color = 'green' if status == 200 else 'red'
        except requests.RequestException:
            status, response_time, color = 'Error', '-', 'red'
        
        monitoring_results[url] = {'status': status, 'response_time': response_time}
        text_var.set(f"{url}\nStatus: {status}\nResponse Time: {response_time}s")
        threading.Event().wait(interval)

# Tkinter UI for adding URLs
def start_monitoring():
    url, interval = url_entry.get(), int(interval_entry.get())
    text_var = tk.StringVar()
    label = tk.Label(root, textvariable=text_var, fg='black')
    label.pack()
    threading.Thread(target=check_url, args=(url, interval, text_var), daemon=True).start()

# Initialize Tkinter GUI
root = tk.Tk()
root.title("URL Monitor")

tk.Label(root, text="URL:").pack()
url_entry = tk.Entry(root)
url_entry.pack()

tk.Label(root, text="Interval (s):").pack()
interval_entry = tk.Entry(root)
interval_entry.pack()

tk.Button(root, text="Start Monitoring", command=start_monitoring).pack()

# Start Flask API in a separate thread
threading.Thread(target=app.run, kwargs={'port': 5000, 'debug': False, 'use_reloader': False}, daemon=True).start()

root.mainloop()
