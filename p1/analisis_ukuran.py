"""Pertanyaan analisis P1 - ukuran pesan XML untuk tambah(5, 3)."""
import xmlrpc.client

req = xmlrpc.client.dumps((5, 3), "tambah")
resp = xmlrpc.client.dumps((8,), methodresponse=True)
print("=== methodCall ===");     print(req)
print("=== methodResponse ==="); print(resp)

# data sebenarnya: nama method + nilai parameter
data_req = len("tambah") + len("5") + len("3")
data_resp = len("8")
for nama, pesan, data in (("methodCall", req, data_req), ("methodResponse", resp, data_resp)):
    b = len(pesan.encode("utf-8"))
    print(f"{nama:15s}: {b} byte | data sebenarnya {data} byte ({data/b*100:.1f}%) | overhead {b-data} byte ({(b-data)/b*100:.1f}%)")
