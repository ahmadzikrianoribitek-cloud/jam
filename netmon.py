"""
Netmon - pembaca lalu lintas jaringan untuk halaman Jam WITA.
Membaca penghitung byte dari sistem operasi (tanpa mengunduh/mengunggah apa pun,
jadi TIDAK memakai kuota). Menyajikan angkanya di http://127.0.0.1:8765/speed

Cara pakai:  pip install psutil   lalu   python netmon.py
"""
import json, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import psutil

PORT = 8765
INTERVAL = 0.5   # detik antar pembacaan

state = {"down": 0.0, "up": 0.0, "total_down": 0, "total_up": 0}

def counters():
    rx = tx = 0
    for name, c in psutil.net_io_counters(pernic=True).items():
        n = name.lower()
        if n == "lo" or "loopback" in n:   # abaikan lalu lintas internal
            continue
        rx += c.bytes_recv
        tx += c.bytes_sent
    return rx, tx

def sampler():
    rx0, tx0 = counters()
    start_rx, start_tx = rx0, tx0
    t0 = time.time()
    sm_d = sm_u = 0.0
    while True:
        time.sleep(INTERVAL)
        rx1, tx1 = counters()
        t1 = time.time()
        dt = t1 - t0
        if dt > 0:
            d = max(rx1 - rx0, 0) * 8 / 1e6 / dt
            u = max(tx1 - tx0, 0) * 8 / 1e6 / dt
            sm_d = sm_d * .4 + d * .6      # sedikit diperhalus
            sm_u = sm_u * .4 + u * .6
            state.update(down=sm_d, up=sm_u,
                         total_down=max(rx1 - start_rx, 0), total_up=max(tx1 - start_tx, 0))
        rx0, tx0, t0 = rx1, tx1, t1

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()
    def do_GET(self):
        body = json.dumps(state).encode()
        self.send_response(200); self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)
    def log_message(self, *a):
        pass

if __name__ == "__main__":
    threading.Thread(target=sampler, daemon=True).start()
    print(f"Netmon berjalan di http://127.0.0.1:{PORT}/speed  (Ctrl+C untuk berhenti)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
