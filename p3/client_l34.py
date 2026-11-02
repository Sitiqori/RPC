"""L3.4 - Throughput 200 GetMahasiswa dari 20 thread client."""
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

TOTAL, THREADS = 200, 20
label = sys.argv[1] if len(sys.argv) > 1 else "?"

with grpc.insecure_channel("localhost:50051") as ch:
    stub = pb_grpc.LayananNilaiStub(ch)
    stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"))        # pemanasan

    def satu(_):
        t = time.perf_counter()
        stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"))
        return time.perf_counter() - t

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=THREADS) as ex:
        lat = list(ex.map(satu, range(TOTAL)))
    total = time.perf_counter() - t0

print(f"RESULT {label} {total:.3f} {TOTAL/total:.2f} {sum(lat)/len(lat)*1000:.1f}")
