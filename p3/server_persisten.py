"""Perbaikan untuk pertanyaan analisis P3: saldo + request_id disimpan DURABEL (SQLite).

Env:  PORT (50060) | DB (bank.db) | DEDUP = "db" (tabel proses persisten) atau "memori" (hilang saat restart)
Kunci perbaikan: update saldo dan pencatatan request_id dilakukan dalam SATU transaksi atomik.
"""
import os
import sqlite3
import threading
from concurrent import futures

import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc

PORT = int(os.environ.get("PORT", "50060"))
DB = os.environ.get("DB", "bank.db")
DEDUP = os.environ.get("DEDUP", "db")

LOCK = threading.Lock()
conn = sqlite3.connect(DB, check_same_thread=False, isolation_level=None)  # transaksi manual
conn.execute("CREATE TABLE IF NOT EXISTS saldo(akun TEXT PRIMARY KEY, jumlah REAL)")
conn.execute("CREATE TABLE IF NOT EXISTS proses(request_id TEXT PRIMARY KEY, sukses INTEGER, pesan TEXT)")
conn.execute("INSERT OR IGNORE INTO saldo VALUES ('A', 1000.0), ('B', 500.0)")
CACHE_MEMORI = {}      # dipakai hanya jika DEDUP == "memori"


def saldo_semua():
    return dict(conn.execute("SELECT akun, jumlah FROM saldo").fetchall())


class Layanan(pb_grpc.LayananNilaiServicer):
    def Transfer(self, request, context):
        with LOCK:
            conn.execute("BEGIN IMMEDIATE")
            try:
                if DEDUP == "db":
                    row = conn.execute("SELECT sukses, pesan FROM proses WHERE request_id=?",
                                       (request.request_id,)).fetchone()
                    if row:
                        conn.execute("COMMIT")
                        return pb.StatusResponse(sukses=bool(row[0]), pesan=row[1])
                elif request.request_id in CACHE_MEMORI:
                    conn.execute("COMMIT")
                    return CACHE_MEMORI[request.request_id]
                (sd,) = conn.execute("SELECT jumlah FROM saldo WHERE akun=?", (request.dari,)).fetchone()
                if sd < request.jumlah:
                    sukses, pesan = False, "Saldo tidak cukup"
                else:
                    conn.execute("UPDATE saldo SET jumlah=jumlah-? WHERE akun=?", (request.jumlah, request.dari))
                    conn.execute("UPDATE saldo SET jumlah=jumlah+? WHERE akun=?", (request.jumlah, request.ke))
                    sukses, pesan = True, "Transfer berhasil"
                if DEDUP == "db":
                    conn.execute("INSERT INTO proses VALUES (?,?,?)", (request.request_id, int(sukses), pesan))
                else:
                    CACHE_MEMORI[request.request_id] = pb.StatusResponse(sukses=sukses, pesan=pesan)
                conn.execute("COMMIT")                  # saldo & request_id tersimpan bersamaan
                return pb.StatusResponse(sukses=sukses, pesan=pesan)
            except Exception:
                conn.execute("ROLLBACK")
                raise

    def GetSaldo(self, request, context):
        return pb.SaldoResponse(saldo=saldo_semua())


if __name__ == "__main__":
    s = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_LayananNilaiServicer_to_server(Layanan(), s)
    s.add_insecure_port(f"[::]:{PORT}")
    s.start()
    print(f"Server persisten port {PORT} | dedup={DEDUP} | db={DB}", flush=True)
    s.wait_for_termination()
