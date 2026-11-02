# Praktikum RPC — Komputasi Paralel dan Terdistribusi

Siti Qori'ah Muhafidloh · NIM 247006111141 · Kelas E · Informatika, Universitas Siliwangi

Struktur: `p1/` (XML-RPC), `p2/` (gRPC), `p3/` (concurrency, timeout, toleransi kegagalan),
`hasil_eksekusi/` (keluaran terminal yang dipakai di laporan).

## Instalasi (PowerShell, Python 3.10+)
```powershell
cd "D:\Semester 5\KPT\RPC"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Praktikum 1 hanya memakai pustaka bawaan Python. Untuk dua komputer, ganti `localhost` dengan IP server
dan izinkan port (8000, 50051, 50052) di firewall.

## Praktikum 1 — XML-RPC (folder p1)
```powershell
python server_kalkulator.py            # terminal 1 (tambah --quiet untuk benchmark)
python client_kalkulator.py            # terminal 2 (pesan XML verbose)
python client_latihan.py               # L1.1, L1.2, L1.3
python bench_l14.py localhost          # L1.4 (ganti localhost dengan IP server untuk 2 komputer)
python client_error.py localhost mentah    # L1.5, matikan server (Ctrl+C) saat berjalan
python client_error.py localhost aman
python analisis_ukuran.py              # pertanyaan analisis
```

## Praktikum 2 — gRPC (folder p2)
Stub sudah digenerate; untuk generate ulang:
```powershell
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. akademik.proto
```
```powershell
python server_grpc.py                  # terminal 1
python client_grpc.py                  # dasar
python client_l21.py                   # L2.1 client streaming
python client_l22.py                   # L2.2 bidirectional streaming
python client_l23_lama.py              # L2.3 client lama (stub_lama/) vs server baru
python demo_l23_bytes.py               # L2.3 bukti tingkat byte
python bench_ukuran.py                 # L2.4 (butuh paket xmlrpc bawaan)
$env:DELAY="0.2"; python server_grpc.py   # lalu: python client_l25_async.py (L2.5)
```
Ulangi server dari awal sebelum L2.2/L2.3 agar data awal bersih.

## Praktikum 3 — folder p3
Variabel lingkungan PowerShell: `$env:NAMA="nilai"` (hapus dengan `Remove-Item Env:NAMA`).
Server perlu dijalankan ulang di setiap percobaan (saldo kembali A=1000, B=500).
```powershell
$env:SEED="42"; python server_transfer.py          # L3.1 / L3.2
python client_l31_l32.py tetap                     # L3.1 (request_id tetap)
python client_l31_l32.py baru                      # L3.2 (uuid baru tiap percobaan)

$env:USE_LOCK="0"; $env:SLOW_PROB="0"; python server_transfer.py                          # L3.3a
$env:USE_LOCK="0"; $env:SLOW_PROB="0"; $env:RACE_WINDOW="0.005"; python server_transfer.py # L3.3b
$env:USE_LOCK="1"; $env:SLOW_PROB="0"; $env:RACE_WINDOW="0.005"; python server_transfer.py # L3.3c
python client_l33.py

$env:MAX_WORKERS="4"; $env:DELAY="0.1"; $env:SLOW_PROB="0"; python server_transfer.py      # L3.4 (1, 4, 10)
python client_l34.py 4

$env:PORT="50051"; python server_transfer.py       # L3.5 terminal A
$env:PORT="50052"; python server_transfer.py       # L3.5 terminal B
python client_l35_failover.py                      # matikan terminal A saat client berjalan

python uji_restart.py memori                       # pertanyaan analisis (dedup di memori)
python uji_restart.py db                           # pertanyaan analisis (dedup persisten, SQLite)
```
