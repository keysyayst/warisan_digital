"""
Modul Kriptografi - AES-256-CBC
Menggunakan library cryptography (Python) untuk enkripsi dan dekripsi pesan.
"""

import os
import hashlib
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class CryptoEngine:
    """
    Mesin enkripsi dan dekripsi berbasis AES-256-CBC.

    Alur enkripsi:
    1. Kata sandi di-hash SHA-256 menghasilkan kunci 256-bit (32 byte)
    2. IV (Initialization Vector) 16-byte dibuat acak
    3. Pesan di-pad ke kelipatan 16 byte (PKCS7)
    4. Enkripsi AES-CBC menghasilkan ciphertext
    5. Output = IV (16 byte) + ciphertext

    Alur dekripsi:
    1. Ambil IV dari 16 byte pertama
    2. Dekripsi sisa data menggunakan kunci + IV
    3. Hapus padding untuk mendapatkan pesan asli
    """

    BLOCK_SIZE = 16
    KEY_SIZE = 32

    def _derive_key(self, password: str) -> bytes:
        """Menghasilkan kunci AES 256-bit dari kata sandi menggunakan SHA-256."""
        return hashlib.sha256(password.encode("utf-8")).digest()

    def _pad(self, data: bytes) -> bytes:
        """PKCS7 padding - menambahkan byte agar panjang data adalah kelipatan BLOCK_SIZE."""
        pad_len = self.BLOCK_SIZE - (len(data) % self.BLOCK_SIZE)
        return data + bytes([pad_len] * pad_len)

    def _unpad(self, data: bytes) -> bytes:
        """Menghapus PKCS7 padding dari data."""
        if not data:
            raise ValueError("Data kosong setelah dekripsi")
        pad_len = data[-1]
        if pad_len < 1 or pad_len > self.BLOCK_SIZE:
            raise ValueError("Padding tidak valid - kemungkinan kata sandi salah")
        if data[-pad_len:] != bytes([pad_len] * pad_len):
            raise ValueError("Padding tidak konsisten - kemungkinan kata sandi salah")
        return data[:-pad_len]

    def encrypt(self, plaintext: str, password: str) -> bytes:
        """
        Mengenkripsi teks menggunakan AES-256-CBC.

        Args:
            plaintext: Teks yang akan dienkripsi
            password:  Kata sandi sebagai kunci

        Returns:
            bytes: IV (16 byte) + ciphertext
        """
        key = self._derive_key(password)
        iv = os.urandom(self.BLOCK_SIZE)

        padded_data = self._pad(plaintext.encode("utf-8"))

        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()

        return iv + ciphertext

    def decrypt(self, encrypted_data: bytes, password: str) -> str:
        """
        Mendekripsi data yang telah dienkripsi dengan AES-256-CBC.

        Args:
            encrypted_data: IV + ciphertext
            password:       Kata sandi yang digunakan saat enkripsi

        Returns:
            str: Pesan asli

        Raises:
            ValueError: Jika kata sandi salah atau data korup
        """
        if len(encrypted_data) < self.BLOCK_SIZE * 2:
            raise ValueError("Data terlalu pendek atau tidak valid")

        iv = encrypted_data[:self.BLOCK_SIZE]
        ciphertext = encrypted_data[self.BLOCK_SIZE:]

        key = self._derive_key(password)

        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        try:
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        except Exception:
            raise ValueError("Gagal mendekripsi - kata sandi salah atau data rusak")

        plaintext_bytes = self._unpad(padded_plaintext)

        try:
            return plaintext_bytes.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("Gagal membaca teks - kata sandi salah atau foto telah diubah")