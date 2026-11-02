"""Uji pertanyaan analisis P3: apa yang terjadi pada at-most-once bila server restart?

Skenario: client kirim Transfer(rid=R, A->B 100) -> server crash/restart sebelum balasan sampai
-> client retry dengan rid yang SAMA. Saldo harus tetap berkurang 100 saja.
"""
import os
import subprocess
import sys
import time

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc
from client_lib import ambil_saldo

mode = sys.argv[1]                     # "memori" atau "db"
db = f"uji_{mode}.db"
if os.path.exists(db):
    os.remove(db)


def start():
    p = subprocess.Popen([sys.executable, "server_persisten.py"],
                         env={**os.environ, "DEDUP": mode, "DB": db, "PORT": "50060"},
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    return p


def transfer(rid):
    with grpc.insecure_channel("localhost:50060") as ch:
        stub = pb_grpc.LayananNilaiStub(ch)
        r = stub.Transfer(pb.TransferRequest(request_id=rid, dari="A", ke="B", jumlah=100), timeout=3)
        return r.pesan, ambil_saldo(stub)


print(f"=== Mode dedup: {mode.upper()} (saldo selalu disimpan di SQLite) ===")
srv = start()
pesan, s = transfer("REQ-001")
print("1) Transfer pertama  rid=REQ-001 ->", pesan, "| saldo:", s)
srv.kill(); srv.wait()
print("2) Server crash / restart (balasan dianggap hilang)")
srv = start()
pesan, s = transfer("REQ-001")
print("3) Client retry rid yang SAMA   ->", pesan, "| saldo:", s)
srv.kill(); srv.wait()
print("   A berkurang", 1000 - s["A"], "(seharusnya 100)", "=> " + ("AMAN, at-most-once terjaga" if s["A"] == 900 else "TRANSFER GANDA"))
