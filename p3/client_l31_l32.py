"""L3.1 (request_id tetap) dan L3.2 (uuid baru tiap percobaan): 20x transfer 10 dari A ke B."""
import sys
import grpc
import akademik_pb2_grpc as pb_grpc
from client_lib import transfer_dengan_retry, ambil_saldo

id_tetap = sys.argv[1] == "tetap"
retry_total = 0
gagal_total = 0


def log(msg):
    global retry_total
    retry_total += 1
    print(msg)


with grpc.insecure_channel("localhost:50051") as ch:
    stub = pb_grpc.LayananNilaiStub(ch)
    print("Saldo awal :", ambil_saldo(stub))
    for i in range(1, 21):
        print(f"Transfer ke-{i:02d}: A -> B 10")
        try:
            r = transfer_dengan_retry(stub, "A", "B", 10, maks=3, id_tetap=id_tetap, log=log)
            if not r.sukses:
                print("   gagal:", r.pesan)
        except grpc.RpcError as e:
            gagal_total += 1
            print(f"   !! menyerah setelah 3 percobaan ({e.code().name}) - client TIDAK tahu apakah transfer terjadi")
    s = ambil_saldo(stub)
    print("\nJumlah retry terjadi :", retry_total)
    print("Transfer menyerah    :", gagal_total)
    print("Saldo akhir          :", s)
    print("Total saldo          :", sum(s.values()), "(harus 1500)")
    print("A berkurang          :", 1000 - s["A"], "(harus 200)")
    print("B bertambah          :", s["B"] - 500)
