"""L2.3 - Bukti di level byte: pesan baru (ber-prodi) dibaca kelas lama, dan sebaliknya.

Kelas 'lama' dibangun dari deskriptor terpisah (tanpa field prodi) supaya tidak
bentrok dengan stub baru di pool deskriptor yang sama.
"""
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory
import akademik_pb2 as baru

fdp = descriptor_pb2.FileDescriptorProto()
fdp.name, fdp.package, fdp.syntax = "lama.proto", "akademik_lama", "proto3"
msg = fdp.message_type.add()
msg.name = "Mahasiswa"
for nomor, (nama, tipe) in enumerate([("nim", 9), ("nama", 9), ("ipk", 1)], start=1):
    f = msg.field.add()
    f.name, f.number, f.type, f.label = nama, nomor, tipe, 1
pool = descriptor_pool.DescriptorPool()
pool.Add(fdp)
Lama = message_factory.GetMessageClass(pool.FindMessageTypeByName("akademik_lama.Mahasiswa"))

b_baru = baru.Mahasiswa(nim="2023001", nama="Andi", ipk=3.26, prodi="Informatika").SerializeToString()
print("Pesan BARU (4 field), byte:", b_baru.hex(" "))
lama = Lama()
lama.ParseFromString(b_baru)
print(f"Dibaca kelas LAMA : nim={lama.nim} nama={lama.nama} ipk={lama.ipk}  (field 4 tidak dikenal, tidak error)")
print("Unknown field tetap dibawa saat serialisasi ulang:", lama.SerializeToString() == b_baru)

b_lama = Lama(nim="2023001", nama="Andi", ipk=3.26).SerializeToString()
bar = baru.Mahasiswa()
bar.ParseFromString(b_lama)
print(f"Pesan LAMA dibaca kelas BARU: nim={bar.nim} nama={bar.nama} ipk={bar.ipk} prodi='{bar.prodi}'  (default: string kosong)")
