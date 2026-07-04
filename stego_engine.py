"""
Modul Steganografi - Metode LSB (Least Significant Bit)
Menyembunyikan data biner ke dalam bit paling tidak signifikan dari piksel gambar.
"""

import numpy as np
from PIL import Image
import struct


# Penanda awal dan akhir data
MAGIC_HEADER = b"WRISN1"  # 6 byte penanda


class StegoEngine:
    """
    Mesin steganografi berbasis LSB (Least Significant Bit).

    Format data tersembunyi dalam gambar:
    [MAGIC_HEADER (6 byte)] + [panjang data (4 byte, big-endian)] + [data terenkripsi (N byte)]

    Setiap byte diubah menjadi 8 bit, lalu setiap bit disisipkan ke dalam
    bit LSB dari komponen R, G, atau B setiap piksel.
    Satu piksel bisa menyimpan 3 bit data (satu per kanal warna).
    """

    HEADER_SIZE = len(MAGIC_HEADER)   # 6 byte
    LENGTH_SIZE = 4                   # 4 byte untuk menyimpan panjang data (uint32)

    def _bytes_to_bits(self, data: bytes) -> list:
        """Mengubah bytes menjadi daftar bit (0 atau 1)."""
        bits = []
        for byte in data:
            for i in range(7, -1, -1):
                bits.append((byte >> i) & 1)
        return bits

    def _bits_to_bytes(self, bits: list) -> bytes:
        """Mengubah daftar bit kembali menjadi bytes."""
        result = []
        for i in range(0, len(bits), 8):
            byte_bits = bits[i:i + 8]
            if len(byte_bits) < 8:
                break
            byte_val = 0
            for bit in byte_bits:
                byte_val = (byte_val << 1) | bit
            result.append(byte_val)
        return bytes(result)

    def _calculate_capacity(self, image: Image.Image) -> int:
        """
        Menghitung kapasitas maksimum data yang dapat disimpan dalam gambar (dalam byte).
        Kapasitas = (lebar * tinggi * 3 kanal) / 8 bit per byte - overhead header
        """
        w, h = image.size
        total_bits = w * h * 3
        total_bytes = total_bits // 8
        overhead = self.HEADER_SIZE + self.LENGTH_SIZE
        return total_bytes - overhead

    def encode(self, image_path: str, data: bytes, output_path: str) -> None:
        """
        Menyembunyikan data dalam gambar menggunakan metode LSB.

        Args:
            image_path:  Path foto carrier
            data:        Data terenkripsi yang akan disembunyikan
            output_path: Path foto output (harus .png agar lossless)

        Raises:
            ValueError: Jika data terlalu besar untuk foto yang dipilih
        """
        image = Image.open(image_path).convert("RGB")
        capacity = self._calculate_capacity(image)

        if len(data) > capacity:
            raise ValueError(
                f"Data ({len(data)} byte) terlalu besar untuk foto ini "
                f"(kapasitas: {capacity} byte). Pilih foto dengan resolusi lebih besar."
            )

        # Bangun payload: header + panjang + data
        length_bytes = struct.pack(">I", len(data))
        payload = MAGIC_HEADER + length_bytes + data

        bits_to_embed = self._bytes_to_bits(payload)

        # Konversi gambar ke array numpy
        pixels = np.array(image, dtype=np.uint8)
        flat_pixels = pixels.flatten()

        # Sisipkan setiap bit ke LSB piksel
        for i, bit in enumerate(bits_to_embed):
            flat_pixels[i] = (flat_pixels[i] & 0xFE) | bit

        # Rekonstruksi gambar
        modified_pixels = flat_pixels.reshape(pixels.shape)
        result_image = Image.fromarray(modified_pixels, "RGB")

        # Simpan sebagai PNG (lossless - JPEG akan merusak bit yang tersembunyi)
        if not output_path.lower().endswith(".png"):
            output_path = output_path.rsplit(".", 1)[0] + ".png"

        result_image.save(output_path, format="PNG", optimize=False)

    def check_has_hidden_message(self, image_path: str) -> bool:
        """
        Cek apakah foto mengandung pesan tersembunyi.

        Args:
            image_path: Path foto yang akan dicek

        Returns:
            bool: True jika mengandung pesan, False jika tidak

        Raises:
            Exception: Jika gagal membuka foto
        """
        try:
            image = Image.open(image_path).convert("RGB")
            pixels = np.array(image, dtype=np.uint8)
            flat_pixels = pixels.flatten()

            # Baca header dulu untuk validasi (6 byte = 48 bit)
            header_bits_count = self.HEADER_SIZE * 8
            if len(flat_pixels) < header_bits_count:
                return False

            header_bits = [int(flat_pixels[i]) & 1 for i in range(header_bits_count)]
            header_bytes = self._bits_to_bytes(header_bits)

            return header_bytes == MAGIC_HEADER
        except Exception:
            return False

    def get_message_info(self, image_path: str) -> dict:
        """
        Mendapatkan informasi detail pesan tersembunyi dalam foto.

        Args:
            image_path: Path foto yang akan diperiksa

        Returns:
            dict: Informasi dengan struktur:
            {
                "has_message": bool,
                "message_size": int (bytes),
                "message_size_readable": str,
                "image_size": tuple (width, height),
                "image_capacity": int (bytes),
                "usage_percent": float,
                "status": str,
                "error": str (jika ada)
            }
        """
        result = {
            "has_message": False,
            "message_size": 0,
            "message_size_readable": "0 B",
            "image_size": (0, 0),
            "image_capacity": 0,
            "usage_percent": 0.0,
            "status": "Tidak ada pesan",
            "error": None
        }

        try:
            image = Image.open(image_path).convert("RGB")
            w, h = image.size
            result["image_size"] = (w, h)
            
            # Hitung kapasitas
            capacity = self._calculate_capacity(image)
            result["image_capacity"] = capacity

            pixels = np.array(image, dtype=np.uint8)
            flat_pixels = pixels.flatten()

            # Baca header dulu untuk validasi (6 byte = 48 bit)
            header_bits_count = self.HEADER_SIZE * 8
            if len(flat_pixels) < header_bits_count:
                result["status"] = "Foto terlalu kecil untuk menyimpan pesan"
                return result

            header_bits = [int(flat_pixels[i]) & 1 for i in range(header_bits_count)]
            header_bytes = self._bits_to_bytes(header_bits)

            # Jika header tidak cocok
            if header_bytes != MAGIC_HEADER:
                result["status"] = "Foto ini belum mengandung pesan terenkripsi"
                result["error"] = "Magic header tidak ditemukan"
                return result

            # Header cocok, baca panjang data
            result["has_message"] = True
            
            length_start_bit = header_bits_count
            length_end_bit = length_start_bit + self.LENGTH_SIZE * 8
            
            if length_end_bit > len(flat_pixels):
                result["status"] = "Data rusak atau tidak lengkap"
                result["error"] = "Tidak bisa membaca ukuran data"
                return result

            length_bits = [int(flat_pixels[i]) & 1 for i in range(length_start_bit, length_end_bit)]
            length_bytes = self._bits_to_bytes(length_bits)
            
            try:
                message_size = struct.unpack(">I", length_bytes)[0]
            except:
                result["status"] = "Data rusak"
                result["error"] = "Ukuran data tidak valid"
                return result

            if message_size <= 0 or message_size > capacity:
                result["status"] = "Data tidak valid atau telah dimodifikasi"
                result["error"] = f"Ukuran data mencurigakan: {message_size} bytes"
                return result

            result["message_size"] = message_size
            result["message_size_readable"] = self._format_size(message_size)
            result["usage_percent"] = min(100.0, (message_size / max(capacity, 1)) * 100)
            result["status"] = "Pesan terenkripsi terdeteksi dan integritas terjaga"

            return result

        except Exception as e:
            result["error"] = str(e)
            result["status"] = "Gagal membaca foto"
            return result

    def _format_size(self, bytes_size: int) -> str:
        """Format ukuran file ke readable format (B, KB, MB)."""
        for unit in ['B', 'KB', 'MB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} GB"

    def decode(self, image_path: str) -> bytes:
        """
        Mengekstrak data tersembunyi dari gambar.

        Args:
            image_path: Path foto yang mengandung pesan tersembunyi

        Returns:
            bytes: Data terenkripsi yang ditemukan

        Raises:
            ValueError: Jika foto tidak mengandung pesan tersembunyi (magic header tidak cocok)
        """
        image = Image.open(image_path).convert("RGB")
        pixels = np.array(image, dtype=np.uint8)
        flat_pixels = pixels.flatten()

        # Baca header dulu untuk validasi (6 byte = 48 bit)
        header_bits_count = self.HEADER_SIZE * 8
        header_bits = [int(flat_pixels[i]) & 1 for i in range(header_bits_count)]
        header_bytes = self._bits_to_bytes(header_bits)

        if header_bytes != MAGIC_HEADER:
            raise ValueError(
                "Foto ini tidak mengandung pesan warisan tersembunyi, "
                "atau file telah diubah/dikompresi sehingga data hilang."
            )

        # Baca panjang data (4 byte = 32 bit)
        length_start_bit = header_bits_count
        length_end_bit = length_start_bit + self.LENGTH_SIZE * 8
        length_bits = [int(flat_pixels[i]) & 1 for i in range(length_start_bit, length_end_bit)]
        length_bytes = self._bits_to_bytes(length_bits)
        data_length = struct.unpack(">I", length_bytes)[0]

        if data_length <= 0 or data_length > self._calculate_capacity(image):
            raise ValueError(f"Panjang data tidak valid ({data_length}). File mungkin telah diubah.")

        # Baca data utama
        data_start_bit = length_end_bit
        data_end_bit = data_start_bit + data_length * 8

        if data_end_bit > len(flat_pixels):
            raise ValueError("Data yang diklaim melebihi ukuran gambar. File mungkin rusak.")

        data_bits = [int(flat_pixels[i]) & 1 for i in range(data_start_bit, data_end_bit)]
        extracted_data = self._bits_to_bytes(data_bits)

        return extracted_data