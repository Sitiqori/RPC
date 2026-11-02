"""Fungsi client bersama: transfer dengan timeout + retry (exponential backoff)."""
import time
import uuid
import grpc
import akademik_pb2 as pb

def transfer_dengan_retry(stub, dari, ke, jumlah, maks=3, id_tetap=True, log=print):
    """id_tetap=True  -> satu request_id dipakai untuk semua percobaan (BENAR, at-most-once)
       id_tetap=False -> uuid baru tiap percobaan (SALAH, dipakai untuk L3.2)"""
    rid = str(uuid.uuid4())
    for percobaan in range(1, maks + 1):
        if not id_tetap:
            rid = str(uuid.uuid4())
        try:
            req = pb.TransferRequest(request_id=rid, dari=dari, ke=ke, jumlah=jumlah)
            return stub.Transfer(req, timeout=2.0)
        except grpc.RpcError as e:
            bisa_ulang = e.code() in (grpc.StatusCode.DEADLINE_EXCEEDED,
                                      grpc.StatusCode.UNAVAILABLE)
            if not bisa_ulang or percobaan == maks:
                raise
            jeda = 0.5 * 2 ** (percobaan - 1)
            log(f"    Percobaan {percobaan} gagal ({e.code().name}), ulang dalam {jeda} s")
            time.sleep(jeda)

def ambil_saldo(stub):
    return dict(stub.GetSaldo(pb.Kosong()).saldo)
