"""L2.1 - Client streaming KirimBanyakNilai."""
import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc


def hasilkan_nilai():
    data = [("2023002", "Jaringan", 88), ("2023002", "Komputasi Paralel", 90),
            ("2023003", "Basis Data", 75), ("2023003", "Jaringan", 140),   # 140 -> ditolak
            ("2023003", "Sistem Operasi", 82)]
    for nim, mk, nilai in data:
        print(f"  kirim -> {nim} | {mk:18s} | {nilai}")
        yield pb.NilaiRequest(nim=nim, matkul=mk, nilai=nilai)


with grpc.insecure_channel("localhost:50051") as ch:
    stub = pb_grpc.LayananNilaiStub(ch)
    print("Mengirim aliran nilai ke server:")
    r = stub.KirimBanyakNilai(hasilkan_nilai())
    print(f"Balasan server: sukses={r.sukses} | jumlah={r.jumlah} | pesan='{r.pesan}'")
    print("Verifikasi via StreamNilai('2023002'):")
    for n in stub.StreamNilai(pb.MahasiswaRequest(nim="2023002")):
        print(f"  {n.matkul}: {n.nilai}")
