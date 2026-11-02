"""L2.4 - Bandingkan ukuran pesan Protobuf vs XML-RPC untuk data yang sama."""
import xmlrpc.client
import akademik_pb2 as pb

# ---- Respons: data mahasiswa ----
data = {"nim": "2023001", "nama": "Andi", "ipk": 3.26}
mhs = pb.Mahasiswa(nim=data["nim"], nama=data["nama"], ipk=data["ipk"])
pb_resp = mhs.SerializeToString()
xml_resp = xmlrpc.client.dumps((data,), methodresponse=True).encode()

# ---- Request: tanya mahasiswa ----
pb_req = pb.MahasiswaRequest(nim="2023001").SerializeToString()
xml_req = xmlrpc.client.dumps(("2023001",), "GetMahasiswa").encode()

# ---- Pembanding dengan Praktikum 1: tambah(5, 3) ----
xml_tambah = xmlrpc.client.dumps((5, 3), "tambah").encode()

print(f"{'Pesan':34s}{'Protobuf (B)':>14s}{'XML-RPC (B)':>14s}{'Rasio XML/PB':>14s}")
for nama, a, b in (("Request GetMahasiswa(nim)", pb_req, xml_req),
                   ("Response Mahasiswa(nim,nama,ipk)", pb_resp, xml_resp)):
    print(f"{nama:34s}{len(a):>14d}{len(b):>14d}{len(b)/len(a):>13.1f}x")
print()
print("Isi Protobuf response (hex):", pb_resp.hex(" "))
print("len(mhs.SerializeToString()) =", len(pb_resp))
print("XML-RPC tambah(5,3) dari Praktikum 1 =", len(xml_tambah), "byte")
print("Catatan: gRPC menambah 5 byte prefix (1 byte flag + 4 byte panjang) per pesan pada HTTP/2 frame.")
