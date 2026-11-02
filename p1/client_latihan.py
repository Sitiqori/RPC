"""Praktikum 1 - Uji L1.1, L1.2, L1.3 (tanpa verbose agar output ringkas)."""
import datetime
import xmlrpc.client

HOST = "localhost"
proxy = xmlrpc.client.ServerProxy(f"http://{HOST}:8000/", allow_none=True)

print("=== L1.1 pangkat() dan akar() ===")
print("pangkat(2, 10) =", proxy.pangkat(2, 10))
print("pangkat(5, 3)  =", proxy.pangkat(5, 3))
print("akar(144)      =", proxy.akar(144))
print("akar(2)        =", proxy.akar(2))
try:
    proxy.akar(-4)
except xmlrpc.client.Fault as e:
    print("akar(-4)       -> Fault:", e.faultString)

print("\n=== L1.2 statistik(daftar) ===")
data = [4, 8, 15, 16, 23, 42]
hasil = proxy.statistik(data)
print("input :", data)
print("output:", hasil, "| tipe di client:", type(hasil).__name__)
print("\nXML request (list):")
print(xmlrpc.client.dumps((data,), "statistik"))
print("XML response (dict):")
print(xmlrpc.client.dumps((hasil,), methodresponse=True))

print("=== L1.3a datetime ===")
sekarang = datetime.datetime(2026, 10, 31, 14, 30, 0)
print("kirim   :", sekarang)
print("tipe di server:", proxy.tipe(sekarang))
balik = proxy.echo(sekarang)
print("diterima:", balik, "| tipe:", type(balik).__name__)
print("XML datetime:")
print(xmlrpc.client.dumps((sekarang,), "echo"))

print("=== L1.3b bilangan sangat besar ===")
for n in (2**31 - 1, 2**31, 2**40):
    try:
        print(f"echo({n}) ->", proxy.echo(n))
    except Exception as e:
        print(f"echo({n}) -> {type(e).__name__}: {e}")
print("-- solusi: kirim sebagai string / float --")
print("echo(str(2**40))   ->", proxy.echo(str(2**40)))
print("int(...) di client ->", int(proxy.echo(str(2**40))))
print("echo(float(2**40)) ->", proxy.echo(float(2**40)))
