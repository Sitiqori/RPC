"""L1.5 - Penanganan error ketika server mati saat client berjalan."""
import http.client
import socket
import sys
import time
import xmlrpc.client

HOST = sys.argv[1] if len(sys.argv) > 1 else "localhost"
MODE = sys.argv[2] if len(sys.argv) > 2 else "aman"   # "mentah" | "aman"
proxy = xmlrpc.client.ServerProxy(f"http://{HOST}:8000/")


def panggil_aman(a, b, maks=3, jeda=0.5):
    for p in range(1, maks + 1):
        try:
            return proxy.tambah(a, b)
        except xmlrpc.client.Fault as e:                 # error logika dari server
            raise
        except (ConnectionRefusedError, ConnectionResetError, BrokenPipeError,
                http.client.RemoteDisconnected, socket.timeout, OSError) as e:
            print(f"  [percobaan {p}/{maks}] gagal: {type(e).__name__}: {e}", flush=True)
            if p == maks:
                return None
            time.sleep(jeda)


for i in range(1, 13):
    if MODE == "mentah":
        print(f"panggilan {i}: tambah({i},1) = {proxy.tambah(i, 1)}", flush=True)
    else:
        hasil = panggil_aman(i, 1)
        print(f"panggilan {i}: tambah({i},1) = {hasil if hasil is not None else 'GAGAL (server tidak tersedia)'}", flush=True)
    time.sleep(0.4)
