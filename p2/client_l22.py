"""L2.2 - Bidirectional streaming Diskusi: dua client (Andi dan Sari) dalam satu skrip."""
import queue
import threading
import time

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

LOG = []
LOG_LOCK = threading.Lock()


def peserta(nama, skrip, mulai):
    """skrip: list (detik_sejak_mulai, isi_pesan)."""
    keluar = queue.Queue()

    def kirim():
        yield pb.Pesan(pengirim=nama, isi="")           # pesan pertama = bergabung
        t0 = time.time()
        for waktu, isi in skrip:
            time.sleep(max(0, waktu - (time.time() - t0)))
            yield pb.Pesan(pengirim=nama, isi=isi)
        time.sleep(2.0)                                  # tunggu balasan terakhir

    def jalan():
        time.sleep(mulai)
        with grpc.insecure_channel("localhost:50051") as ch:
            stub = pb_grpc.LayananNilaiStub(ch)
            for p in stub.Diskusi(kirim()):
                with LOG_LOCK:
                    print(f"[{nama:4s} menerima] {p.pengirim}: {p.isi}", flush=True)

    t = threading.Thread(target=jalan)
    t.start()
    return t


t1 = peserta("Andi", [(1.0, "Halo semua, ada yang sudah mengerjakan L2.2?"),
                       (2.5, "Oke, nanti kita bandingkan hasilnya ya.")], mulai=0.0)
t2 = peserta("Sari", [(1.8, "Halo Andi! Sudah, pakai bidirectional streaming."),
                       (3.2, "Siap, sampai ketemu di praktikum.")], mulai=0.5)
t1.join(); t2.join()
