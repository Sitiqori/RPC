"""L3.3 - 50 transfer dari 10 thread client secara bersamaan."""
import uuid
from concurrent.futures import ThreadPoolExecutor

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc
from client_lib import ambil_saldo

with grpc.insecure_channel("localhost:50051") as ch:
    stub = pb_grpc.LayananNilaiStub(ch)
    print("Saldo awal :", ambil_saldo(stub))

    def kirim(_):
        return stub.Transfer(pb.TransferRequest(request_id=str(uuid.uuid4()), dari="A", ke="B", jumlah=10),
                             timeout=10)

    with ThreadPoolExecutor(max_workers=10) as ex:
        hasil = list(ex.map(kirim, range(50)))
    s = ambil_saldo(stub)
    print("Transfer sukses :", sum(r.sukses for r in hasil), "dari 50")
    print("Saldo akhir     :", s)
    print("Total saldo     :", sum(s.values()), "(seharusnya 1500)")
    print("Harapan         : A=500.0, B=1000.0")
    print("Status          :", "KONSISTEN" if (s['A'], s['B']) == (500.0, 1000.0) else "DATA RUSAK (race condition)")
