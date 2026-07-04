# Warisan Digital Tersembunyi
**Sistem Kriptografi dan Steganografi untuk Aset Digital**

---

## Deskripsi

Aplikasi ini memungkinkan pengguna untuk menyembunyikan informasi warisan digital (kata sandi akun bank, kripto wallet, email, dan aset digital lainnya) di dalam foto keluarga biasa. Foto yang dihasilkan tampak normal secara visual namun menyimpan data terenkripsi di dalamnya.

---

## Algoritma yang Digunakan

### Kriptografi: AES-256-CBC
- Standar enkripsi simetris yang digunakan oleh pemerintah AS dan institusi keuangan global
- Kunci 256-bit dihasilkan dari kata sandi menggunakan SHA-256
- Mode CBC (Cipher Block Chaining) memastikan setiap blok bergantung pada blok sebelumnya
- IV (Initialization Vector) acak digunakan untuk keamanan tambahan

### Steganografi: LSB (Least Significant Bit)
- Data tersembunyi di bit paling tidak signifikan dari setiap kanal warna piksel (R, G, B)
- Perubahan satu bit hanya mengubah warna sebesar 0.4%, tidak terdeteksi secara visual
- Foto disimpan sebagai PNG (format lossless) agar data tidak rusak

---

## Instalasi

```bash
# 1. Clone atau unduh repositori ini
# 2. Install dependencies
pip install -r requirements.txt

# 3. Jalankan aplikasi
python app.py
```

### Persyaratan
- Python 3.8 atau lebih baru
- Sistem operasi: Windows, macOS, atau Linux (dengan tkinter)

---

## Cara Penggunaan

### Menyembunyikan Pesan

1. Buka halaman **Sembunyikan Pesan**
2. Klik **Pilih Foto** dan pilih foto keluarga (JPG, PNG, BMP)
3. Tulis pesan warisan di kolom teks (kata sandi akun, nomor rekening, dll)
4. Buat kata sandi yang kuat untuk enkripsi
5. Konfirmasi kata sandi
6. Pilih folder output (opsional)
7. Klik **Sembunyikan Pesan dalam Foto**
8. Simpan foto hasil di tempat yang aman

### Mengungkap Pesan

1. Buka halaman **Ungkap Pesan**
2. Pilih foto yang mengandung pesan tersembunyi (file `_warisan.png`)
3. Masukkan kata sandi yang digunakan saat menyembunyikan
4. Klik **Ungkap Pesan**
5. Baca informasi warisan yang muncul

---

## Keamanan

- Data dienkripsi sebelum disembunyikan dalam foto
- Tanpa kata sandi yang benar, pesan tidak dapat dibaca
- Gunakan kata sandi yang kuat (minimal 12 karakter, kombinasi huruf besar/kecil, angka, simbol)
- Simpan foto di lokasi terpercaya (cloud pribadi, USB, hardisk terenkripsi)
- Jangan hapus atau konversi foto ke format JPEG karena akan merusak data tersembunyi

---

## Struktur Proyek

```
warisan_digital/
- app.py              # Aplikasi utama dan antarmuka pengguna
- crypto_engine.py    # Modul enkripsi/dekripsi AES-256-CBC
- stego_engine.py     # Modul steganografi LSB
- ui_components.py    # Komponen UI kustom
- requirements.txt    # Daftar dependensi
- README.md           # Dokumentasi ini
```

---

## Mata Kuliah

**Kriptografi** - Sistem Warisan Digital Tersembunyi dalam Foto Keluarga

Algoritma yang dibahas: AES (Advanced Encryption Standard) dan LSB Steganography
