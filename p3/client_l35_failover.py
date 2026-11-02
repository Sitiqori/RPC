"""L3.5 - Client dengan failover otomatis: server utama :50051, cadangan :50052."""
import time
import grpc
import akademik_pb2 as pb
import akademik_pb2_grpc as pb_grpc


class ClientFailover:
    def __init__(self, targets):
        self.targets = targets
        self.idx = 0
        self._buka()

    def _buka(self):
        self.channel = grpc.insecure_channel(self.targets[self.idx])
        self.stub = pb_grpc.LayananNilaiStub(self.channel)

    def panggil(self, nama_rpc, req, timeout=1.0):
        for _ in range(len(self.targets)):
            try:
                return getattr(self.stub, nama_rpc)(req, timeout=timeout), self.targets[self.idx]
            except grpc.RpcError as e:
                if e.code() not in (
                    grpc.StatusCode.UNAVAILABLE,
                    grpc.StatusCode.DEADLINE_EXCEEDED
                ):
                    raise
                lama = self.targets[self.idx]
                self.channel.close()
                self.idx = (self.idx + 1) % len(self.targets)
                print(f"   !! {lama} UNAVAILABLE -> failover ke {self.targets[self.idx]}", flush=True)
                self._buka()
        raise RuntimeError("Semua server tidak tersedia")


c = ClientFailover(["localhost:50051", "localhost:50052"])
for i in range(1, 13):
    r, dari = c.panggil("GetMahasiswa", pb.MahasiswaRequest(nim="2023001"))
    print(f"Panggilan {i:2d}: {r.nama} IPK={r.ipk}  (dilayani {dari})", flush=True)
    time.sleep(0.5)
