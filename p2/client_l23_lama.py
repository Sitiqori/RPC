"""L2.3 - CLIENT LAMA (stub dibuat dari proto TANPA field prodi) vs SERVER BARU."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "stub_lama"))   # pakai stub lama
import grpc
import akademik_pb2 as pb           # <- stub lama
import akademik_pb2_grpc as pb_grpc

print("Field pada message Mahasiswa menurut stub LAMA:",
      [f.name for f in pb.Mahasiswa.DESCRIPTOR.fields])
with grpc.insecure_channel("localhost:50051") as ch:
    stub = pb_grpc.LayananNilaiStub(ch)
    mhs = stub.GetMahasiswa(pb.MahasiswaRequest(nim="2023001"))
    print(f"Client lama menerima: nim={mhs.nim} nama={mhs.nama} ipk={mhs.ipk}")
    print("hasattr(mhs, 'prodi') ->", hasattr(mhs, "prodi"))
    print("Byte mentah yang diterima & di-parse (unknown field tetap disimpan):",
          len(mhs.SerializeToString()), "byte")
