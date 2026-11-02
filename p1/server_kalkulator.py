"""Praktikum 1 - Server XML-RPC kalkulator (+ fungsi tambahan L1.1, L1.2, L1.3)."""
import argparse
import math
from xmlrpc.server import SimpleXMLRPCServer

def tambah(a, b):
    return a + b

def kali(a, b):
    return a * b

def bagi(a, b):
    if b == 0:
        raise ValueError("Pembagian dengan nol")
    return a / b

# L1.1 
def pangkat(a, b):
    return a ** b

def akar(x):
    if x < 0:
        raise ValueError("Akar dari bilangan negatif tidak didefinisikan")
    return math.sqrt(x)

# L1.2 
def statistik(daftar):
    if not daftar:
        raise ValueError("Daftar tidak boleh kosong")
    return {"min": min(daftar), "max": max(daftar),
            "rata2": sum(daftar) / len(daftar)}

# L1.3 (bantu pengamatan tipe data)
def tipe(x):
    """Mengembalikan nama tipe Python yang diterima server."""
    return type(x).__name__

def echo(x):
    return x

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--quiet", action="store_true", help="matikan log (untuk benchmark)")
    args = ap.parse_args()
    server = SimpleXMLRPCServer((args.host, args.port), allow_none=True,
                                logRequests=not args.quiet)
    server.register_introspection_functions()
    for f in (tambah, kali, bagi, pangkat, akar, statistik, tipe, echo):
        server.register_function(f, f.__name__)
    print(f"Server XML-RPC berjalan di port {args.port}...", flush=True)
    server.serve_forever()
