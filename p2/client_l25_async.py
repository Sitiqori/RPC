"""L2.5 - GetMahasiswa asinkron dengan .future(): 10 permintaan sekaligus."""
import time
import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

NIMS = ["2023001", "2023002"] * 5          # 10 permintaan

with grpc.insecure_channel("localhost:50051") as ch:
    stub = pb_grpc.LayananNilaiStub(ch)
    stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"))   # pemanasan koneksi

    t0 = time.perf_counter()
    for nim in NIMS:
        stub.GetMahasiswa(pb.MahasiswaRequest(nim=nim))
    sinkron = time.perf_counter() - t0

    t0 = time.perf_counter()
    futures_ = [stub.GetMahasiswa.future(pb.MahasiswaRequest(nim=nim)) for nim in NIMS]
    t_kirim = time.perf_counter() - t0                       # waktu hanya untuk mengirim
    hasil = [f.result() for f in futures_]                   # kumpulkan hasil
    asinkron = time.perf_counter() - t0

print("Hasil 10 permintaan asinkron:")
for i, m in enumerate(hasil, 1):
    print(f"  {i:2d}. {m.nim} {m.nama:5s} IPK={m.ipk} prodi={m.prodi}")
print(f"\nWaktu 10 panggilan SINKRON  : {sinkron:.3f} s")
print(f"Waktu 10 panggilan ASINKRON : {asinkron:.3f} s (pengiriman semua permintaan hanya {t_kirim*1000:.1f} ms)")
print(f"Percepatan                  : {sinkron/asinkron:.1f}x")
