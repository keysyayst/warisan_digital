# Warisan Digital Tersembunyi

Sistem kriptografi dan steganografi untuk menyimpan informasi warisan digital secara aman di dalam foto keluarga.

## Deskripsi

Aplikasi ini memungkinkan pengguna untuk:
- menyembunyikan pesan rahasia ke dalam foto menggunakan enkripsi AES-256 dan steganografi LSB,
- mengungkap kembali pesan dari foto yang telah diberi data tersembunyi,
- memeriksa apakah sebuah foto sudah mengandung pesan tersembunyi atau belum,
- menghasilkan laporan PDF otomatis setelah proses penyembunyian berhasil.

Hasil akhirnya adalah foto yang secara visual tetap tampak normal, tetapi di dalamnya menyimpan data terenkripsi yang hanya bisa dibuka dengan kata sandi yang benar.

## Fitur yang Sudah Diterapkan

### 1. Sembunyikan Pesan ke dalam Foto
- Pilih foto carrier (format JPG, PNG, BMP, TIFF, dll.)
- Masukkan pesan yang ingin disembunyikan
- Tentukan kata sandi yang kuat
- Konfirmasi kata sandi
- Pilih folder hasil output secara opsional
- Simpan foto hasil dengan nama yang bisa ditentukan
- Menampilkan pratinjau foto dan estimasi kapasitas pesan

### 2. Ungkap Pesan dari Foto
- Pilih foto yang diduga mengandung pesan tersembunyi
- Masukkan kata sandi yang digunakan saat proses penyembunyian
- Tampilkan isi pesan yang berhasil didekripsi
- Menyediakan fitur copy hasil pesan ke clipboard

### 3. Cek Status Foto
- Periksa apakah foto mengandung pesan tersembunyi atau tidak
- Menampilkan informasi seperti ukuran gambar, kapasitas, dan persentase penggunaan ruang stego

### 4. Laporan PDF Otomatis
- Setelah proses penyembunyian berhasil, aplikasi membuat laporan PDF berisi:
  - nama file carrier,
  - nama file hasil,
  - panjang pesan,
  - kapasitas foto,
  - instruksi untuk ahli waris.

### 5. Antarmuka Modern
- Menggunakan antarmuka berbasis CustomTkinter
- Tersedia halaman Beranda, Sembunyikan Pesan, Ungkap Pesan, Cek Status Foto, dan Panduan Cara Kerja

## Cara Kerja

### Kriptografi: AES-256-CBC
- Pesan dienkripsi sebelum disisipkan ke dalam foto
- Kata sandi diolah menjadi kunci 256-bit menggunakan SHA-256
- Menggunakan mode CBC dan IV acak untuk keamanan tambahan

### Steganografi: LSB
- Data terenkripsi disisipkan ke bit paling tidak signifikan dari piksel foto
- Perubahan yang terjadi sangat kecil sehingga tidak terlihat secara visual
- Format output yang digunakan adalah PNG agar data tetap aman dan tidak rusak

## Persyaratan

- Python 3.10 atau lebih baru
- Paket yang dibutuhkan dapat diinstal dari file requirements.txt

## Instalasi

```bash
pip install -r requirements.txt
```

## Menjalankan Aplikasi

```bash
python app.py
```

Hasil file .exe akan berada di folder dist.

## Struktur Proyek

```text
app_warisan/
├── app.py                # Aplikasi utama dan antarmuka pengguna
├── crypto_engine.py      # Modul enkripsi dan dekripsi AES-256
├── stego_engine.py       # Modul steganografi LSB
├── pdf_exporter.py       # Pembuatan laporan PDF otomatis
├── ui_components.py      # Komponen UI kustom
├── assets/               # File pendukung seperti icon aplikasi
├── requirements.txt      # Daftar dependensi
└── README.md             # Dokumentasi proyek
```

## Catatan Keamanan

- Gunakan kata sandi yang kuat dan aman
- Simpan file hasil di lokasi yang terpercaya
- Jangan mengubah format foto hasil secara sembarangan karena dapat merusak data tersembunyi
- Pesan hanya bisa dibuka jika kata sandi yang benar digunakan
