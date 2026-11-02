"""L1.4 - Bandingkan 100 panggilan tambah() lokal vs RPC (XML-RPC)."""
import sys
import time
import xmlrpc.client

HOST = sys.argv[1] if len(sys.argv) > 1 else "localhost"
N = 100


def tambah(a, b):
    return a + b


# lokal
t0 = time.perf_counter()
for i in range(N):
    tambah(i, 1)
lokal = time.perf_counter() - t0

# RPC
proxy = xmlrpc.client.ServerProxy(f"http://{HOST}:8000/")
proxy.tambah(0, 0)  # pemanasan koneksi
t0 = time.perf_counter()
for i in range(N):
    proxy.tambah(i, 1)
rpc = time.perf_counter() - t0

print(f"Host server          : {HOST}")
print(f"{N} panggilan lokal   : {lokal*1000:.4f} ms  ({lokal/N*1e6:.2f} us/panggilan)")
print(f"{N} panggilan RPC     : {rpc*1000:.2f} ms  ({rpc/N*1000:.3f} ms/panggilan)")
print(f"RPC lebih lambat sekitar {rpc/lokal:,.0f}x dibanding panggilan lokal")
