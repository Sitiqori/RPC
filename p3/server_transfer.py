"""Praktikum 3 - Server gRPC dengan Transfer (deduplikasi request_id) + opsi eksperimen via env.

Variabel lingkungan (untuk eksperimen):
  PORT         port server                              (default 50051)
  MAX_WORKERS  jumlah thread server                     (default 10)
  USE_LOCK     1 = pakai LOCK, 0 = tanpa lock (L3.3)    (default 1)
  SLOW_PROB    peluang balasan terlambat 3 detik        (default 0.3)
  RACE_WINDOW  jeda (detik) antara baca & tulis saldo   (default 0) -> memperlebar celah race
  DELAY        sleep di GetMahasiswa (L3.4)             (default 0)
  SEED         seed random agar eksperimen bisa diulang (default 0)
"""
import contextlib
import os
import random
import threading
import time
from concurrent import futures

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

PORT = int(os.environ.get("PORT", "50051"))
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", "10"))
USE_LOCK = os.environ.get("USE_LOCK", "1") == "1"
SLOW_PROB = float(os.environ.get("SLOW_PROB", "0.3"))
RACE_WINDOW = float(os.environ.get("RACE_WINDOW", "0"))
DELAY = float(os.environ.get("DELAY", "0"))
random.seed(int(os.environ.get("SEED", "0")))

DATA = {
    "2023001": {"nama": "Andi", "nilai": {"Basis Data": 85.0, "Jaringan": 78.0}},
    "2023002": {"nama": "Sari", "nilai": {"Basis Data": 92.0}},
}
SALDO = {"A": 1000.0, "B": 500.0}
PROSES = {}                      
LOCK = threading.Lock()

class LayananNilai(pb_grpc.LayananNilaiServicer):
    def GetMahasiswa(self, request, context):
        if DELAY:
            time.sleep(DELAY)
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f"NIM {request.nim} tidak ditemukan")
        daftar = list(mhs["nilai"].values())
        ipk = sum(daftar) / len(daftar) / 25 if daftar else 0.0
        return pb.Mahasiswa(nim=request.nim, nama=mhs["nama"], ipk=round(ipk, 2))

    def TambahNilai(self, request, context):
        if not 0 <= request.nilai <= 100:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Nilai harus 0-100")
        mhs = DATA.setdefault(request.nim, {"nama": "(baru)", "nilai": {}})
        mhs["nilai"][request.matkul] = request.nilai
        return pb.StatusResponse(sukses=True, pesan="Nilai tersimpan")

    def StreamNilai(self, request, context):
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "NIM tidak ditemukan")
        for matkul, nilai in mhs["nilai"].items():
            yield pb.Nilai(matkul=matkul, nilai=nilai)
            time.sleep(0.5)

    def Transfer(self, request, context):
        with (LOCK if USE_LOCK else contextlib.nullcontext()):
            if request.request_id in PROSES:               
                return PROSES[request.request_id]
            saldo_dari = SALDO[request.dari]                  
            if saldo_dari < request.jumlah:
                hasil = pb.StatusResponse(sukses=False, pesan="Saldo tidak cukup")
            else:
                if RACE_WINDOW:
                    time.sleep(RACE_WINDOW)                 
                SALDO[request.dari] = saldo_dari - request.jumlah          
                SALDO[request.ke] = SALDO[request.ke] + request.jumlah
                hasil = pb.StatusResponse(sukses=True, pesan=f"Saldo kini {SALDO}")
            PROSES[request.request_id] = hasil
        if random.random() < SLOW_PROB:
            time.sleep(3)                                    
        return hasil

    def GetSaldo(self, request, context):
        with LOCK:
            return pb.SaldoResponse(saldo=dict(SALDO))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    pb_grpc.add_LayananNilaiServicer_to_server(LayananNilai(), server)
    server.add_insecure_port(f"[::]:{PORT}")
    server.start()
    print(f"Server gRPC port {PORT} | workers={MAX_WORKERS} | lock={USE_LOCK} | "
          f"slow_prob={SLOW_PROB} | race_window={RACE_WINDOW} | delay={DELAY}", flush=True)
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
