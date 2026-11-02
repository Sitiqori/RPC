"""Praktikum 2 - Server gRPC LayananNilai (unary, server/client/bidi streaming)."""
import os
import queue
import threading
import time
from concurrent import futures

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

DELAY = float(os.environ.get("DELAY", "0"))   # simulasi waktu proses (dipakai L2.5)

DATA = {
    "2023001": {"nama": "Andi", "prodi": "Informatika", "nilai": {"Basis Data": 85.0, "Jaringan": 78.0}},
    "2023002": {"nama": "Sari", "prodi": "Informatika", "nilai": {"Basis Data": 92.0}},
}
LOCK = threading.Lock()


class LayananNilai(pb_grpc.LayananNilaiServicer):
    def __init__(self):
        self.peserta = {}                 # nama -> queue (ruang diskusi, L2.2)
        self.peserta_lock = threading.Lock()

    # ---------------- unary ----------------
    def GetMahasiswa(self, request, context):
        if DELAY:
            time.sleep(DELAY)
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f"NIM {request.nim} tidak ditemukan")
        daftar = list(mhs["nilai"].values())
        ipk = sum(daftar) / len(daftar) / 25 if daftar else 0.0   # konversi sederhana 0-100 ke 0-4
        return pb.Mahasiswa(nim=request.nim, nama=mhs["nama"], ipk=round(ipk, 2),
                            prodi=mhs.get("prodi", ""))

    def TambahNilai(self, request, context):
        if not 0 <= request.nilai <= 100:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Nilai harus 0-100")
        with LOCK:
            mhs = DATA.setdefault(request.nim, {"nama": "(baru)", "prodi": "", "nilai": {}})
            mhs["nilai"][request.matkul] = request.nilai
        return pb.StatusResponse(sukses=True, pesan="Nilai tersimpan", jumlah=1)

    # ---------------- server streaming ----------------
    def StreamNilai(self, request, context):
        mhs = DATA.get(request.nim)
        if mhs is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "NIM tidak ditemukan")
        for matkul, nilai in list(mhs["nilai"].items()):
            yield pb.Nilai(matkul=matkul, nilai=nilai)
            time.sleep(0.5)               # simulasi data dikirim bertahap

    # ---------------- client streaming (L2.1) ----------------
    def KirimBanyakNilai(self, request_iterator, context):
        tersimpan, ditolak = 0, 0
        for req in request_iterator:      # menerima aliran NilaiRequest dari client
            if not 0 <= req.nilai <= 100:
                ditolak += 1
                continue
            with LOCK:
                mhs = DATA.setdefault(req.nim, {"nama": "(baru)", "prodi": "", "nilai": {}})
                mhs["nilai"][req.matkul] = req.nilai
            tersimpan += 1
        pesan = f"{tersimpan} nilai tersimpan" + (f", {ditolak} ditolak (di luar 0-100)" if ditolak else "")
        return pb.StatusResponse(sukses=ditolak == 0, pesan=pesan, jumlah=tersimpan)

    # ---------------- bidirectional streaming (L2.2) ----------------
    def Diskusi(self, request_iterator, context):
        antrian = queue.Queue()
        nama = {"v": None}
        SELESAI = object()

        def siarkan(pesan, kecuali=None):
            with self.peserta_lock:
                for n, q in self.peserta.items():
                    if n != kecuali:
                        q.put(pesan)

        def baca():
            try:
                for msg in request_iterator:
                    if nama["v"] is None:             # pesan pertama = bergabung
                        nama["v"] = msg.pengirim
                        with self.peserta_lock:
                            self.peserta[nama["v"]] = antrian
                        siarkan(pb.Pesan(pengirim="SISTEM", isi=f"{nama['v']} bergabung"), kecuali=nama["v"])
                    if msg.isi:
                        siarkan(pb.Pesan(pengirim=msg.pengirim, isi=msg.isi), kecuali=nama["v"])
            finally:                                  # client selesai / terputus
                if nama["v"]:
                    with self.peserta_lock:
                        self.peserta.pop(nama["v"], None)
                    siarkan(pb.Pesan(pengirim="SISTEM", isi=f"{nama['v']} keluar"))
                antrian.put(SELESAI)

        threading.Thread(target=baca, daemon=True).start()
        while True:
            item = antrian.get()
            if item is SELESAI:
                return
            yield item


def serve(port=50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_LayananNilaiServicer_to_server(LayananNilai(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Server gRPC berjalan di port {port}...", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
