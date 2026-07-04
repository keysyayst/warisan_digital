"""
Warisan Digital Tersembunyi
Sistem Kriptografi & Steganografi untuk Aset Digital
Menggunakan AES-256 (enkripsi) + LSB Steganography (penyembunyian pesan dalam foto)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import os
import sys
import threading
import time
from pathlib import Path
from PIL import Image

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --- Import modules ---
from crypto_engine import CryptoEngine
from stego_engine import StegoEngine
from ui_components import (
    Colors, Fonts, AnimatedButton, PasswordStrengthMeter,
    InfoCard, SectionHeader, FileDropZone, ScrollableFrame
)
from pdf_exporter import generate_report


class WaisanDigitalApp(ctk.CTk):
    def _clear_label_image(self, label_widget):
        try:
            if label_widget is None:
                return
            if hasattr(label_widget, "_label"):
                label_widget._label.configure(image="")
                label_widget._label.image = None
            label_widget._image = None
            label_widget._photo_ref = None
        except Exception:
            pass

    def __init__(self):
        super().__init__()

        self.withdraw()

        self.title("Warisan Digital Tersembunyi")
        self.geometry("1100x720")
        self.minsize(900, 640)
        self.configure(fg_color=Colors.BG_DARK)

        self.crypto = CryptoEngine()
        self.stego = StegoEngine()

        self._selected_image_path = None
        self._selected_output_dir = None
        self._extract_image_path = None
        self._check_image_path = None
        self._current_page = None
        self._setup_icon()
        self.loading_window = None
        self.after(10, self._show_loading_screen)
    
    def _setup_icon(self):
        try:
            icon_path = Path(__file__).parent / "assets" / "icon.png"
            if icon_path.exists():
                img = tk.PhotoImage(file=str(icon_path))
                self.iconphoto(True, img)
        except Exception:
            pass
    
    def _start_application(self):
        progress = 0

        def animate():
            nonlocal progress

            self.loading_bar.set(progress / 100)
            self.loading_percent.configure(text=f"{progress}%")

            if progress == 80:

                self._build_layout()
                self._show_page("beranda")

            if progress < 100:
                progress += 1
                self.after(25, animate)

            else:
                self.loading_window.focus_set()
                self.loading_window.destroy()

                self.deiconify()
                self.lift()
                self.focus_force()

        animate()

    def _build_layout(self):
        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=Colors.SIDEBAR,
            border_width=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self._build_sidebar()

        # --- Main content ---
        self.main_area = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=Colors.BG_DARK,
        )
        self.main_area.pack(side="left", fill="both", expand=True)

        # --- Page container ---
        self.page_container = ctk.CTkFrame(
            self.main_area,
            fg_color="transparent",
        )
        self.page_container.pack(fill="both", expand=True, padx=0, pady=0)

        self.pages = {}
        self._build_pages()

    def _build_sidebar(self):
        # Logo area
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=100)
        logo_frame.pack(fill="x", pady=(24, 8))
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(
            logo_frame,
            text="W",
            font=ctk.CTkFont("Georgia", 38, "bold"),
            text_color=Colors.ACCENT_GOLD,
        ).pack(pady=(8, 0))

        ctk.CTkLabel(
            logo_frame,
            text="Warisan Digital",
            font=ctk.CTkFont("Georgia", 11, "bold"),
            text_color=Colors.TEXT_MUTED,
        ).pack()

        # Divider
        ctk.CTkFrame(self.sidebar, height=1, fg_color=Colors.BORDER).pack(
            fill="x", padx=16, pady=8
        )

        # Nav items
        self._nav_buttons = {}
        nav_items = [
            ("beranda", "Beranda", "home"),
            ("sembunyikan", "Sembunyikan Pesan", "lock"),
            ("ungkap", "Ungkap Pesan", "unlock"),
            ("cek_status", "Cek Status Foto", "check"),
            ("panduan", "Cara Kerja", "info"),
        ]

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=12, pady=4)

        for page_id, label, icon in nav_items:
            icon_map = {
                "home": "\u2302",
                "lock": "\u26BF",
                "unlock": "\u2756",
                "check": "\U0001F50D",
                "info": "\u24D8",
            }
            btn = ctk.CTkButton(
                nav_frame,
                text=f"  {icon_map[icon]}  {label}",
                anchor="w",
                height=42,
                corner_radius=10,
                font=ctk.CTkFont("Segoe UI", 13),
                fg_color="transparent",
                hover_color=Colors.NAV_HOVER,
                text_color=Colors.TEXT_MUTED,
                command=lambda pid=page_id: self._show_page(pid),
            )
            btn.pack(fill="x", pady=3)
            self._nav_buttons[page_id] = btn

        # Bottom info
        ctk.CTkFrame(self.sidebar, height=1, fg_color=Colors.BORDER).pack(
            fill="x", padx=16, pady=(16, 8), side="bottom"
        )
        ctk.CTkLabel(
            self.sidebar,
            text="AES-256 + LSB Steganography",
            font=ctk.CTkFont("Segoe UI", 9),
            text_color=Colors.TEXT_MUTED,
        ).pack(side="bottom", pady=(0, 12))

        ctk.CTkLabel(
            self.sidebar,
            text="Sistem Warisan Digital",
            font=ctk.CTkFont("Segoe UI", 9, "bold"),
            text_color=Colors.TEXT_MUTED,
        ).pack(side="bottom", pady=2)

    def _build_pages(self):
        for page_id in ["beranda", "sembunyikan", "ungkap", "cek_status", "panduan"]:
            frame = ctk.CTkScrollableFrame(
                self.page_container,
                fg_color="transparent",
                scrollbar_button_color=Colors.BORDER,
                scrollbar_button_hover_color=Colors.ACCENT_GOLD,
            )
            self.pages[page_id] = frame

        self._build_beranda()
        self._build_sembunyikan()
        self._build_ungkap()
        self._build_cek_status()
        self._build_panduan()

    def _show_page(self, page_id):
        previous_page = getattr(self, "_current_page", None)
        if previous_page and previous_page != page_id:
            self._reset_page(previous_page)

        for pid, frame in self.pages.items():
            frame.pack_forget()
        self.pages[page_id].pack(fill="both", expand=True, padx=0, pady=0)

        for pid, btn in self._nav_buttons.items():
            if pid == page_id:
                btn.configure(
                    fg_color=Colors.NAV_ACTIVE,
                    text_color=Colors.TEXT_PRIMARY,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Colors.TEXT_MUTED,
                )

        self._current_page = page_id

    def _reset_page(self, page_id):
        """Bersihkan form/hasil pada halaman yang ditinggalkan."""
        if page_id == "sembunyikan":
            self._reset_encode_form()
        elif page_id == "ungkap":
            self._reset_decode_form()
        elif page_id == "cek_status":
            self._reset_check_form()

    # ===================== BERANDA =====================
    def _build_beranda(self):
        page = self.pages["beranda"]

        # Hero section
        hero = ctk.CTkFrame(page, fg_color=Colors.CARD, corner_radius=16)
        hero.pack(fill="x", padx=28, pady=(28, 12))

        hero_inner = ctk.CTkFrame(hero, fg_color="transparent")
        hero_inner.pack(fill="x", padx=32, pady=28)

        ctk.CTkLabel(
            hero_inner,
            text="Sistem Warisan Digital Tersembunyi",
            font=ctk.CTkFont("Georgia", 22, "bold"),
            text_color=Colors.ACCENT_GOLD,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            hero_inner,
            text="Lindungi dan wariskan aset digital Anda dengan aman melalui\nenkripsi AES-256 dan steganografi LSB di dalam foto keluarga.",
            font=ctk.CTkFont("Segoe UI", 13),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            justify="left",
        ).pack(anchor="w", pady=(8, 20))

        # Fitur Aplikasi - penjelasan fitur dengan tombol langsung ke halamannya
        fitur_section = ctk.CTkFrame(page, fg_color="transparent")
        fitur_section.pack(fill="x", padx=28, pady=(4, 12))

        ctk.CTkLabel(
            fitur_section,
            text="Fitur Aplikasi",
            font=ctk.CTkFont("Georgia", 16, "bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            fitur_section,
            text="Pilih fitur yang ingin digunakan, lalu klik tombolnya untuk membuka halaman terkait.",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(0, 14))

        fitur_grid = ctk.CTkFrame(fitur_section, fg_color="transparent")
        fitur_grid.pack(fill="x")

        fitur_data = [
            (
                "\u26BF",
                "Sembunyikan Pesan",
                "Enkripsi pesan warisan dengan AES-256, lalu sembunyikan ke dalam foto keluarga.",
                Colors.ACCENT_GOLD,
                "sembunyikan",
            ),
            (
                "\u2756",
                "Ungkap Pesan",
                "Ekstrak dan dekripsi pesan warisan yang tersembunyi di dalam foto.",
                Colors.ACCENT_PURPLE,
                "ungkap",
            ),
            (
                "\U0001F50D",
                "Cek Status Foto",
                "Periksa apakah sebuah foto sudah mengandung pesan terenkripsi atau belum.",
                Colors.ACCENT_TEAL,
                "cek_status",
            ),
            (
                "\u24D8",
                "Cara Kerja",
                "Pelajari alur enkripsi AES-256 dan penyisipan LSB Steganography secara lengkap.",
                Colors.ACCENT_GOLD,
                "panduan",
            ),
        ]

        for i, (icon, title, desc, color, page_id) in enumerate(fitur_data):
            fitur_grid.grid_columnconfigure(i, weight=1)
            fcard = ctk.CTkFrame(fitur_grid, fg_color=Colors.CARD, corner_radius=12)
            fcard.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")

            ctk.CTkFrame(fcard, fg_color=color, corner_radius=4, height=4).pack(fill="x", side="top")

            finner = ctk.CTkFrame(fcard, fg_color="transparent")
            finner.pack(fill="both", expand=True, padx=16, pady=14)

            ctk.CTkLabel(
                finner,
                text=icon,
                font=ctk.CTkFont("Segoe UI", 22),
                text_color=color,
                anchor="w",
            ).pack(anchor="w", pady=(0, 6))

            ctk.CTkLabel(
                finner,
                text=title,
                font=ctk.CTkFont("Segoe UI", 13, "bold"),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                finner,
                text=desc,
                font=ctk.CTkFont("Segoe UI", 11),
                text_color=Colors.TEXT_SECONDARY,
                wraplength=200,
                justify="left",
                anchor="w",
            ).pack(anchor="w", pady=(6, 12))

            btn_text_color = "#1a1a1a" if color == Colors.ACCENT_GOLD else "#ffffff"

            ctk.CTkButton(
                finner,
                text="Buka Halaman",
                font=ctk.CTkFont("Segoe UI", 11, "bold"),
                fg_color=color,
                hover_color=Colors.CARD_HOVER,
                text_color=btn_text_color,
                corner_radius=8,
                height=32,
                command=lambda pid=page_id: self._show_page(pid),
            ).pack(anchor="w", fill="x")

        # Highlight: fitur laporan PDF otomatis
        pdf_highlight = ctk.CTkFrame(page, fg_color=Colors.CARD, corner_radius=12)
        pdf_highlight.pack(fill="x", padx=28, pady=(4, 12))

        ctk.CTkFrame(pdf_highlight, fg_color=Colors.ACCENT_GOLD, corner_radius=4, height=4).pack(
            fill="x", side="top"
        )

        pdf_inner = ctk.CTkFrame(pdf_highlight, fg_color="transparent")
        pdf_inner.pack(fill="x", padx=20, pady=16)

        pdf_row = ctk.CTkFrame(pdf_inner, fg_color="transparent")
        pdf_row.pack(fill="x")

        ctk.CTkLabel(
            pdf_row,
            text="\U0001F4C4",
            font=ctk.CTkFont("Segoe UI", 24),
            text_color=Colors.ACCENT_GOLD,
        ).pack(side="left", padx=(0, 14))

        pdf_text_col = ctk.CTkFrame(pdf_row, fg_color="transparent")
        pdf_text_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            pdf_text_col,
            text="Laporan PDF Otomatis",
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            pdf_text_col,
            text=(
                "Setiap kali pesan berhasil disembunyikan, aplikasi otomatis membuat "
                "laporan PDF berisi detail teknis, statistik kapasitas, dan instruksi "
                "langkah-demi-langkah untuk ahli waris membuka pesan tersebut nantinya."
            ),
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=760,
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(4, 0))

        # Info cards
        cards_row = ctk.CTkFrame(page, fg_color="transparent")
        cards_row.pack(fill="x", padx=28, pady=4)

        card_data = [
            (
                "Enkripsi AES-256",
                "Pesan Anda dienkripsi menggunakan standar enkripsi militer AES-256-CBC sebelum disembunyikan.",
                Colors.ACCENT_TEAL,
            ),
            (
                "LSB Steganografi",
                "Data terenkripsi disembunyikan dalam bit-bit terkecil piksel foto sehingga tidak terdeteksi.",
                Colors.ACCENT_PURPLE,
            ),
            (
                "Foto Tetap Normal",
                "Foto keluarga yang dihasilkan tampak identik secara visual dan dapat disimpan di mana saja.",
                Colors.ACCENT_GOLD,
            ),
        ]

        for i, (title, desc, color) in enumerate(card_data):
            cards_row.grid_columnconfigure(i, weight=1)
            card = ctk.CTkFrame(cards_row, fg_color=Colors.CARD, corner_radius=12)
            card.grid(row=0, column=i, padx=6, pady=8, sticky="nsew")

            indicator = ctk.CTkFrame(card, fg_color=color, corner_radius=4, height=4)
            indicator.pack(fill="x", padx=0, pady=(0, 0), side="top")

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=16, pady=14)

            ctk.CTkLabel(
                inner,
                text=title,
                font=ctk.CTkFont("Segoe UI", 13, "bold"),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                inner,
                text=desc,
                font=ctk.CTkFont("Segoe UI", 11),
                text_color=Colors.TEXT_SECONDARY,
                wraplength=220,
                justify="left",
                anchor="w",
            ).pack(anchor="w", pady=(6, 0))

        # Scenario section
        scenario = ctk.CTkFrame(page, fg_color=Colors.CARD, corner_radius=16)
        scenario.pack(fill="x", padx=28, pady=(8, 12))

        sc_inner = ctk.CTkFrame(scenario, fg_color="transparent")
        sc_inner.pack(fill="x", padx=28, pady=20)

        ctk.CTkLabel(
            sc_inner,
            text="Kenapa Perlu Warisan Digital?",
            font=ctk.CTkFont("Georgia", 15, "bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w", pady=(0, 10))

        scenarios = [
            "Akun bank digital, kripto wallet, dan investasi online tidak bisa diakses ahli waris tanpa kata sandi.",
            "Menyimpan di kertas berisiko hilang, rusak, atau jatuh ke tangan yang salah.",
            "Layanan notaris digital belum tersedia luas dan tidak semua orang tahu prosedurnya.",
            "Foto keluarga adalah media yang wajar disimpan dan tidak mencurigakan.",
        ]

        for sc in scenarios:
            row = ctk.CTkFrame(sc_inner, fg_color="transparent")
            row.pack(fill="x", pady=4)

            ctk.CTkFrame(row, width=6, height=6, corner_radius=3, fg_color=Colors.ACCENT_GOLD).pack(
                side="left", padx=(0, 12), pady=6
            )
            ctk.CTkLabel(
                row,
                text=sc,
                font=ctk.CTkFont("Segoe UI", 12),
                text_color=Colors.TEXT_SECONDARY,
                wraplength=680,
                justify="left",
                anchor="w",
            ).pack(side="left", fill="x")

    # ===================== SEMBUNYIKAN =====================
    def _build_sembunyikan(self):
        page = self.pages["sembunyikan"]

        SectionHeader(page, "Sembunyikan Pesan dalam Foto").pack(
            fill="x", padx=28, pady=(28, 4)
        )

        ctk.CTkLabel(
            page,
            text="Pesan akan dienkripsi AES-256, lalu disembunyikan dalam piksel foto menggunakan metode LSB.",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", padx=28, pady=(0, 16))

        # Two column layout
        cols = ctk.CTkFrame(page, fg_color="transparent")
        cols.pack(fill="both", padx=28, pady=0, expand=True)
        cols.grid_columnconfigure(0, weight=3)
        cols.grid_columnconfigure(1, weight=2)

        # Left column - form
        left = ctk.CTkFrame(cols, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Image picker
        img_card = ctk.CTkFrame(left, fg_color=Colors.CARD, corner_radius=12)
        img_card.pack(fill="x", pady=(0, 10))

        img_inner = ctk.CTkFrame(img_card, fg_color="transparent")
        img_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            img_inner,
            text="Foto Carrier",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        self._img_label = ctk.CTkLabel(
            img_inner,
            text="Belum ada foto yang dipilih",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_MUTED,
            fg_color=Colors.BG_DARK,
            corner_radius=8,
            height=44,
        )
        self._img_label.pack(fill="x", pady=(0, 8))

        btn_row = ctk.CTkFrame(img_inner, fg_color="transparent")
        btn_row.pack(fill="x")

        ctk.CTkButton(
            btn_row,
            text="Pilih Foto",
            font=ctk.CTkFont("Segoe UI", 12),
            fg_color=Colors.ACCENT_TEAL,
            hover_color=Colors.ACCENT_TEAL_HOVER,
            text_color="#ffffff",
            corner_radius=8,
            height=36,
            command=self._pick_carrier_image,
        ).pack(side="left", padx=(0, 8))

        self._img_capacity_label = ctk.CTkLabel(
            btn_row,
            text="",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=Colors.TEXT_MUTED,
        )
        self._img_capacity_label.pack(side="left")

        # Message input
        msg_card = ctk.CTkFrame(left, fg_color=Colors.CARD, corner_radius=12)
        msg_card.pack(fill="x", pady=(0, 10))

        msg_inner = ctk.CTkFrame(msg_card, fg_color="transparent")
        msg_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            msg_inner,
            text="Pesan Warisan",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        self._message_placeholder = ("Tuliskan informasi warisan di sini...\n"
                        "Contoh: nama ahli waris, nomor rekening, kata sandi akun, dan sebagainya.")
        self._message_placeholder_active = True

        self._message_text = ctk.CTkTextbox(
            msg_inner,
            height=160,
            font=ctk.CTkFont("Segoe UI", 12),
            fg_color=Colors.BG_DARK,
            text_color=Colors.TEXT_MUTED,
            border_color=Colors.BORDER,
            border_width=1,
            corner_radius=8,
            wrap="word",
        )
        self._message_text.pack(fill="x")
        self._message_text.insert("0.0", self._message_placeholder)
        self._message_text.bind("<FocusIn>", self._on_message_focus_in)
        self._message_text.bind("<FocusOut>", self._on_message_focus_out)
        self._message_text.bind("<KeyRelease>", self._update_char_count)

        self._char_count_label = ctk.CTkLabel(
            msg_inner,
            text="0 karakter",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=Colors.TEXT_MUTED,
            anchor="e",
        )
        self._char_count_label.pack(anchor="e", pady=(4, 0))

        # Password
        pw_card = ctk.CTkFrame(left, fg_color=Colors.CARD, corner_radius=12)
        pw_card.pack(fill="x", pady=(0, 10))

        pw_inner = ctk.CTkFrame(pw_card, fg_color="transparent")
        pw_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            pw_inner,
            text="Kata Sandi Enkripsi",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            pw_inner,
            text="Minimal 8 karakter, gunakan huruf besar dan kecil, angka, simbol.",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            wraplength=580,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        self._password_var = tk.StringVar()
        self._password_var.trace_add("write", self._on_password_change)

        self._password_shown = False

        pw_entry_row = ctk.CTkFrame(pw_inner, fg_color="transparent")
        pw_entry_row.pack(fill="x", pady=(0, 4))

        self._password_entry = ctk.CTkEntry(
            pw_entry_row,
            textvariable=self._password_var,
            show="*",
            font=ctk.CTkFont("Segoe UI", 13),
            height=40,
            corner_radius=8,
            fg_color=Colors.BG_DARK,
            border_color=Colors.BORDER,
            placeholder_text="",
        )
        self._password_entry.pack(side="left", fill="x", expand=True)

        self._toggle_pw_btn = ctk.CTkButton(
            pw_entry_row,
            text="Show",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            width=56,
            height=40,
            fg_color="transparent",
            hover_color=Colors.NAV_HOVER,
            text_color=Colors.TEXT_SECONDARY,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=8,
            command=self._toggle_password_visibility,
        )
        self._toggle_pw_btn.pack(side="right", padx=(8, 0))

        self._pw_strength = PasswordStrengthMeter(pw_inner)
        self._pw_strength.pack(fill="x", pady=(0, 4))

        self._pw_warning = ctk.CTkLabel(
            pw_inner,
            text="",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=Colors.ACCENT_GOLD,
            anchor="w",
        )
        self._pw_warning.pack(fill="x")

        ctk.CTkLabel(
            pw_inner,
            text="Konfirmasi Kata Sandi",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(8, 8))

        self._confirm_var = tk.StringVar()

        confirm_row = ctk.CTkFrame(pw_inner, fg_color="transparent")
        confirm_row.pack(fill="x")

        self._confirm_entry = ctk.CTkEntry(
            confirm_row,
            textvariable=self._confirm_var,
            show="*",
            font=ctk.CTkFont("Segoe UI", 13),
            height=40,
            corner_radius=8,
            fg_color=Colors.BG_DARK,
            border_color=Colors.BORDER,
            placeholder_text="",
        )
        self._confirm_entry.pack(side="left", fill="x", expand=True)

        self._confirm_password_shown = False

        self._toggle_confirm_btn = ctk.CTkButton(
            confirm_row,
            text="Show",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            width=56,
            height=40,
            fg_color="transparent",
            hover_color=Colors.NAV_HOVER,
            text_color=Colors.TEXT_SECONDARY,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=8,
            command=self._toggle_confirm_visibility,
        )
        self._toggle_confirm_btn.pack(side="right", padx=(8, 0))

        # Output dir
        out_card = ctk.CTkFrame(left, fg_color=Colors.CARD, corner_radius=12)
        out_card.pack(fill="x", pady=(0, 10))

        out_inner = ctk.CTkFrame(out_card, fg_color="transparent")
        out_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            out_inner,
            text="Nama File Hasil (opsional)",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            out_inner,
            text="Kosongkan untuk memakai nama otomatis: [nama_foto]_warisan.png",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            wraplength=580,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        self._output_filename_var = tk.StringVar()

        self._output_filename_entry = ctk.CTkEntry(
            out_inner,
            textvariable=self._output_filename_var,
            font=ctk.CTkFont("Segoe UI", 13),
            height=40,
            corner_radius=8,
            fg_color=Colors.BG_DARK,
            border_color=Colors.BORDER,
            placeholder_text="contoh: warisan_untuk_anak",
        )
        self._output_filename_entry.pack(fill="x", pady=(0, 16))

        ctk.CTkLabel(
            out_inner,
            text="Folder Simpan Hasil",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        self._outdir_label = ctk.CTkLabel(
            out_inner,
            text="Belum dipilih (akan menggunakan folder foto asal)",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_MUTED,
            fg_color=Colors.BG_DARK,
            corner_radius=8,
            height=36,
        )
        self._outdir_label.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            out_inner,
            text="Pilih Folder Output",
            font=ctk.CTkFont("Segoe UI", 11),
            fg_color="transparent",
            hover_color=Colors.NAV_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            border_color=Colors.BORDER,
            border_width=1,
            corner_radius=8,
            height=34,
            command=self._pick_output_dir,
        ).pack(anchor="w")

        # Action button
        self._encode_btn = ctk.CTkButton(
            left,
            text="Sembunyikan Pesan dalam Foto",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            fg_color=Colors.ACCENT_GOLD,
            hover_color=Colors.ACCENT_GOLD_HOVER,
            text_color="#1a1a1a",
            corner_radius=12,
            height=48,
            command=self._run_encode,
        )
        self._encode_btn.pack(fill="x", pady=(4, 16))
        self._encode_btn.configure(state="disabled")

        # Right column - preview & info
        right = ctk.CTkFrame(cols, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Preview
        preview_card = ctk.CTkFrame(right, fg_color=Colors.CARD, corner_radius=12)
        preview_card.pack(fill="x", pady=(0, 10))

        pv_inner = ctk.CTkFrame(preview_card, fg_color="transparent")
        pv_inner.pack(fill="x", padx=16, pady=16)

        ctk.CTkLabel(
            pv_inner,
            text="Pratinjau Foto",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        self._preview_label = ctk.CTkLabel(
            pv_inner,
            text="Pilih foto untuk pratinjau",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_MUTED,
            fg_color=Colors.BG_DARK,
            corner_radius=8,
            height=200,
        )
        self._preview_label.pack(fill="x")

        # Encode info
        info_card = ctk.CTkFrame(right, fg_color=Colors.CARD, corner_radius=12)
        info_card.pack(fill="x", pady=(0, 10))

        ii_inner = ctk.CTkFrame(info_card, fg_color="transparent")
        ii_inner.pack(fill="x", padx=16, pady=16)

        ctk.CTkLabel(
            ii_inner,
            text="Cara Penggunaan",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        steps = [
            "Pilih foto keluarga sebagai carrier",
            "Tulis pesan warisan (kata sandi akun, nomor rekening, dll)",
            "Buat kata sandi yang kuat untuk enkripsi",
            "Klik Sembunyikan dan simpan foto hasilnya",
            "Simpan foto bersama keluarga terpercaya",
        ]

        for i, step in enumerate(steps, 1):
            row = ctk.CTkFrame(ii_inner, fg_color="transparent")
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row,
                text=str(i),
                font=ctk.CTkFont("Segoe UI", 10, "bold"),
                text_color="#1a1a1a",
                fg_color=Colors.ACCENT_TEAL,
                width=22,
                height=22,
                corner_radius=11,
            ).pack(side="left", padx=(0, 10))

            ctk.CTkLabel(
                row,
                text=step,
                font=ctk.CTkFont("Segoe UI", 11),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w",
                wraplength=200,
                justify="left",
            ).pack(side="left")

        # Progress indicator (hidden initially)
        self._encode_progress = ctk.CTkProgressBar(
            left,
            mode="indeterminate",
            fg_color=Colors.BG_DARK,
            progress_color=Colors.ACCENT_GOLD,
        )

    def _build_ungkap(self):
        page = self.pages["ungkap"]

        SectionHeader(page, "Ungkap Pesan dari Foto").pack(
            fill="x", padx=28, pady=(28, 4)
        )

        ctk.CTkLabel(
            page,
            text="Muat foto yang mengandung pesan tersembunyi, masukkan kata sandi, dan lihat pesan warisan.",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", padx=28, pady=(0, 16))

        cols = ctk.CTkFrame(page, fg_color="transparent")
        cols.pack(fill="both", padx=28, pady=0, expand=True)
        cols.grid_columnconfigure(0, weight=3)
        cols.grid_columnconfigure(1, weight=2)

        # Left column
        left = ctk.CTkFrame(cols, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Image picker
        img_card = ctk.CTkFrame(left, fg_color=Colors.CARD, corner_radius=12)
        img_card.pack(fill="x", pady=(0, 10))

        img_inner = ctk.CTkFrame(img_card, fg_color="transparent")
        img_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            img_inner,
            text="Foto Berisi Pesan",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        self._extract_img_label = ctk.CTkLabel(
            img_inner,
            text="Belum ada foto yang dipilih",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_MUTED,
            fg_color=Colors.BG_DARK,
            corner_radius=8,
            height=44,
        )
        self._extract_img_label.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            img_inner,
            text="Pilih Foto",
            font=ctk.CTkFont("Segoe UI", 12),
            fg_color=Colors.ACCENT_TEAL,
            hover_color=Colors.ACCENT_TEAL_HOVER,
            text_color="#ffffff",
            corner_radius=8,
            height=36,
            command=self._pick_extract_image,
        ).pack(anchor="w")

        # Password
        pw_card = ctk.CTkFrame(left, fg_color=Colors.CARD, corner_radius=12)
        pw_card.pack(fill="x", pady=(0, 10))

        pw_inner = ctk.CTkFrame(pw_card, fg_color="transparent")
        pw_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            pw_inner,
            text="Kata Sandi Dekripsi",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        self._decode_pw_var = tk.StringVar()
        self._decode_pw_var.trace_add(
        "write",
        lambda *args: self._decode_pw_warning.configure(text="")
    )
        self._decode_pw_entry = ctk.CTkEntry(
            pw_inner,
            textvariable=self._decode_pw_var,
            show="*",
            font=ctk.CTkFont("Segoe UI", 13),
            height=40,
            corner_radius=8,
            fg_color=Colors.BG_DARK,
            border_color=Colors.BORDER,
            placeholder_text="Masukkan kata sandi yang digunakan saat menyembunyikan...",
        )
        self._decode_pw_entry.pack(fill="x", pady=(0, 8))
        self._decode_pw_warning = ctk.CTkLabel(
            pw_inner,
            text="",
            text_color="#DC2626",
            font=ctk.CTkFont("Segoe UI", 11),
        )
        self._decode_pw_warning.pack(anchor="w", pady=(2, 0))

        self._show_pw_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            pw_inner,
            text="Tampilkan kata sandi",
            variable=self._show_pw_var,
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_MUTED,
            fg_color=Colors.ACCENT_TEAL,
            hover_color=Colors.ACCENT_TEAL_HOVER,
            command=self._toggle_decode_pw_visibility,
        ).pack(anchor="w")

        # Decode button
        self._decode_btn = ctk.CTkButton(
            left,
            text="Ungkap Pesan",
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            fg_color=Colors.ACCENT_PURPLE,
            hover_color=Colors.ACCENT_PURPLE_HOVER,
            text_color="#ffffff",
            corner_radius=12,
            height=48,
            command=self._run_decode,
        )
        self._decode_btn.pack(fill="x", pady=(4, 10))

        self._decode_progress = ctk.CTkProgressBar(
            left,
            mode="indeterminate",
            fg_color=Colors.BG_DARK,
            progress_color=Colors.ACCENT_PURPLE,
        )

        # Result area
        result_card = ctk.CTkFrame(left, fg_color=Colors.CARD, corner_radius=12)
        result_card.pack(fill="x", pady=(0, 10))

        result_inner = ctk.CTkFrame(result_card, fg_color="transparent")
        result_inner.pack(fill="both", padx=20, pady=16, expand=True)

        header_row = ctk.CTkFrame(result_inner, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            header_row,
            text="Hasil Pesan Warisan",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(side="left")

        self._copy_btn = ctk.CTkButton(
            header_row,
            text="Salin",
            font=ctk.CTkFont("Segoe UI", 10),
            fg_color="transparent",
            hover_color=Colors.NAV_HOVER,
            text_color=Colors.TEXT_MUTED,
            border_color=Colors.BORDER,
            border_width=1,
            corner_radius=6,
            height=26,
            width=60,
            command=self._copy_result,
        )
        self._copy_btn.pack(side="right")

        self._result_text = ctk.CTkTextbox(
            result_inner,
            height=200,
            font=ctk.CTkFont("Courier New", 12),
            fg_color=Colors.BG_DARK,
            text_color=Colors.TEXT_PRIMARY,
            border_color=Colors.BORDER,
            border_width=1,
            corner_radius=8,
            state="disabled",
        )
        self._result_text.pack(fill="x")

        # Right column - preview
        right = ctk.CTkFrame(cols, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        preview_card = ctk.CTkFrame(right, fg_color=Colors.CARD, corner_radius=12)
        preview_card.pack(fill="x", pady=(0, 10))

        pv_inner = ctk.CTkFrame(preview_card, fg_color="transparent")
        pv_inner.pack(fill="x", padx=16, pady=16)

        ctk.CTkLabel(
            pv_inner,
            text="Pratinjau Foto",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        self._extract_preview_label = ctk.CTkLabel(
            pv_inner,
            text="Pilih foto untuk pratinjau",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_MUTED,
            fg_color=Colors.BG_DARK,
            corner_radius=8,
            height=200,
        )
        self._extract_preview_label.pack(fill="x")

        # Warning card
        warn_card = ctk.CTkFrame(right, fg_color="#2d0e0e", corner_radius=12, border_color="#5a1a1a", border_width=1)
        warn_card.pack(fill="x", pady=(0, 10))

        wi = ctk.CTkFrame(warn_card, fg_color="transparent")
        wi.pack(fill="x", padx=16, pady=14)

        ctk.CTkLabel(
            wi,
            text="Peringatan",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            text_color="#DC3545",
            anchor="w",
        ).pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(
            wi,
            text="Pastikan anda berada di tempat yang aman dan tidak ada yang mengintip layar saat mengungkap pesan warisan.",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color="#ffffff",
            wraplength=240,
            justify="left",
            anchor="w",
        ).pack(anchor="w")

    def _build_cek_status(self):
        page = self.pages["cek_status"]

        # Header
        SectionHeader(page, "Cek Status Foto").pack(
            fill="x", padx=28, pady=(28, 4)
        )

        ctk.CTkLabel(
            page,
            text="Upload foto untuk memeriksa apakah sudah mengandung pesan terenkripsi atau belum.",
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=Colors.TEXT_MUTED,
        ).pack(anchor="w", padx=28, pady=(0, 16))

        cols = ctk.CTkFrame(page, fg_color="transparent")
        cols.pack(fill="both", padx=28, pady=0, expand=False)
        cols.grid_columnconfigure(0, weight=1)
        cols.grid_columnconfigure(1, weight=1)

        # Left column - Image picker
        left = ctk.CTkFrame(cols, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        img_card = ctk.CTkFrame(left, fg_color=Colors.CARD, corner_radius=12)
        img_card.pack(fill="x", pady=(0, 10))

        img_inner = ctk.CTkFrame(img_card, fg_color="transparent")
        img_inner.pack(fill="x", padx=20, pady=16)

        ctk.CTkLabel(
            img_inner,
            text="Pilih Foto untuk Diperiksa",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        self._check_img_label = ctk.CTkLabel(
            img_inner,
            text="Belum ada foto yang dipilih",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_MUTED,
            fg_color=Colors.BG_DARK,
            corner_radius=8,
            height=44,
        )
        self._check_img_label.pack(fill="x", pady=(0, 8))

        ctk.CTkButton(
            img_inner,
            text="Pilih Foto",
            font=ctk.CTkFont("Segoe UI", 12),
            fg_color=Colors.ACCENT_GOLD,
            hover_color=Colors.ACCENT_GOLD_HOVER,
            text_color="#ffffff",
            corner_radius=8,
            height=36,
            command=self._pick_check_image,
        ).pack(anchor="w", pady=(0, 8))

        self._check_btn = ctk.CTkButton(
            img_inner,
            text="Cek Status",
            font=ctk.CTkFont("Segoe UI", 12),
            fg_color=Colors.ACCENT_TEAL,
            hover_color=Colors.ACCENT_TEAL_HOVER,
            text_color="#ffffff",
            corner_radius=8,
            height=36,
            command=self._run_check_status,
        )
        self._check_btn.pack(anchor="w")

        self._check_progress = ctk.CTkProgressBar(
            img_inner,
            mode="indeterminate",
            fg_color=Colors.BG_DARK,
            progress_color=Colors.ACCENT_TEAL,
        )

        # Preview
        preview_card = ctk.CTkFrame(left, fg_color=Colors.CARD, corner_radius=12)
        preview_card.pack(fill="x", pady=(0, 10))

        pv_inner = ctk.CTkFrame(preview_card, fg_color="transparent")
        pv_inner.pack(fill="x", padx=16, pady=16)

        ctk.CTkLabel(
            pv_inner,
            text="Pratinjau Foto",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 8))

        self._check_preview_label = ctk.CTkLabel(
            pv_inner,
            text="Pilih foto untuk pratinjau",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_MUTED,
            fg_color=Colors.BG_DARK,
            corner_radius=8,
            height=200,
        )
        self._check_preview_label.pack(fill="x")

        # Right column - Result
        right = ctk.CTkFrame(cols, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        result_card = ctk.CTkFrame(right, fg_color=Colors.CARD, corner_radius=12)
        result_card.pack(fill="x", pady=(0, 10))

        result_inner = ctk.CTkFrame(result_card, fg_color="transparent")
        result_inner.pack(fill="x", padx=20, pady=16, expand=True)

        ctk.CTkLabel(
            result_inner,
            text="Hasil Pemeriksaan",
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 12))

        self._check_result_frame = ctk.CTkFrame(result_inner, fg_color="transparent")
        self._check_result_frame.pack(fill="x")

        # Default result message
        self._check_result_label = ctk.CTkLabel(
            self._check_result_frame,
            text="Pilih foto dan klik 'Cek Status' untuk memeriksa...",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_MUTED,
            justify="left",
            anchor="w",
        )
        self._check_result_label.pack(anchor="w", fill="x")

    def _build_panduan(self):
        page = self.pages["panduan"]

        SectionHeader(page, "Cara Kerja Sistem").pack(
            fill="x", padx=28, pady=(28, 4)
        )

        # AES Explanation
        aes_card = ctk.CTkFrame(page, fg_color=Colors.CARD, corner_radius=12)
        aes_card.pack(fill="x", padx=28, pady=(12, 8))

        aes_inner = ctk.CTkFrame(aes_card, fg_color="transparent")
        aes_inner.pack(fill="x", padx=24, pady=20)

        top_row = ctk.CTkFrame(aes_inner, fg_color="transparent")
        top_row.pack(fill="x")

        ctk.CTkFrame(top_row, width=4, fg_color=Colors.ACCENT_TEAL, corner_radius=2, height=40).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            top_row,
            text="Enkripsi AES-256-CBC",
            font=ctk.CTkFont("Georgia", 15, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            aes_inner,
            text=(
                "AES (Advanced Encryption Standard) adalah standar enkripsi simetris yang digunakan oleh pemerintah AS dan "
                "institusi keuangan global. Dengan panjang kunci 256-bit dan mode CBC (Cipher Block Chaining), pesan Anda "
                "diubah menjadi data acak yang tidak bisa dibaca tanpa kata sandi yang tepat.\n\n"
                "Proses enkripsi: Kata sandi di-hash menggunakan SHA-256 untuk menghasilkan kunci 256-bit. "
                "Setiap blok 16-byte pesan dienkripsi dengan XOR terhadap blok cipher sebelumnya, "
                "lalu diproses oleh 14 putaran substitusi dan permutasi AES."
            ),
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=740,
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(10, 0))

        # LSB Explanation
        lsb_card = ctk.CTkFrame(page, fg_color=Colors.CARD, corner_radius=12)
        lsb_card.pack(fill="x", padx=28, pady=(0, 8))

        lsb_inner = ctk.CTkFrame(lsb_card, fg_color="transparent")
        lsb_inner.pack(fill="x", padx=24, pady=20)

        top_row2 = ctk.CTkFrame(lsb_inner, fg_color="transparent")
        top_row2.pack(fill="x")

        ctk.CTkFrame(top_row2, width=4, fg_color=Colors.ACCENT_PURPLE, corner_radius=2, height=40).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            top_row2,
            text="LSB Steganography (Least Significant Bit)",
            font=ctk.CTkFont("Georgia", 15, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            lsb_inner,
            text=(
                "LSB adalah teknik steganografi yang menyisipkan data ke dalam bit paling tidak signifikan dari setiap komponen "
                "warna piksel (R, G, B). Perubahan satu bit pada nilai 0-255 hanya mengubah warna sebesar 0.4%, "
                "yang tidak dapat dibedakan oleh mata manusia.\n\n"
                "Contoh: Piksel dengan warna merah (R) = 200 = 11001000 dalam biner. Dengan menyisipkan bit '1', "
                "nilainya menjadi 11001001 = 201. Perbedaan ini tidak terlihat secara visual, "
                "namun data tersembunyi di dalamnya bisa dibaca oleh program yang tahu cara mengekstraknya."
            ),
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=740,
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(10, 0))

        # Flow diagram (text-based)
        flow_card = ctk.CTkFrame(page, fg_color=Colors.CARD, corner_radius=12)
        flow_card.pack(fill="x", padx=28, pady=(0, 8))

        flow_inner = ctk.CTkFrame(flow_card, fg_color="transparent")
        flow_inner.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(
            flow_inner,
            text="Alur Proses Lengkap",
            font=ctk.CTkFont("Georgia", 15, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 14))

        flow_steps = [
            ("Enkripsi", "Pesan + Kata Sandi masuk ke AES-256-CBC", Colors.ACCENT_TEAL),
            ("Format", "Hasil enkripsi + panjang data dikemas dalam format biner", Colors.ACCENT_GOLD),
            ("Sisipkan", "Bit-bit data disimpan ke LSB piksel foto satu per satu", Colors.ACCENT_PURPLE),
            ("Simpan", "Foto disimpan dalam format PNG (lossless, tidak ada kompresi yang merusak bit)", Colors.ACCENT_TEAL),
        ]

        flow_row = ctk.CTkFrame(flow_inner, fg_color="transparent")
        flow_row.pack(fill="x")

        for i, (title, desc, color) in enumerate(flow_steps):
            flow_row.grid_columnconfigure(i, weight=1)
            step_frame = ctk.CTkFrame(flow_row, fg_color=Colors.BG_DARK, corner_radius=10)
            step_frame.grid(row=0, column=i, padx=4, sticky="nsew")

            ctk.CTkFrame(step_frame, fg_color=color, height=3, corner_radius=2).pack(fill="x")

            si = ctk.CTkFrame(step_frame, fg_color="transparent")
            si.pack(fill="both", padx=12, pady=10)

            ctk.CTkLabel(
                si,
                text=f"{i+1}. {title}",
                font=ctk.CTkFont("Segoe UI", 11, "bold"),
                text_color=color,
                anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                si,
                text=desc,
                font=ctk.CTkFont("Segoe UI", 10),
                text_color=Colors.TEXT_MUTED,
                anchor="w",
                wraplength=150,
                justify="left",
            ).pack(anchor="w", pady=(4, 0))

        # References
        ref_card = ctk.CTkFrame(page, fg_color=Colors.CARD, corner_radius=12)
        ref_card.pack(fill="x", padx=28, pady=(0, 28))

        ref_inner = ctk.CTkFrame(ref_card, fg_color="transparent")
        ref_inner.pack(fill="x", padx=24, pady=20)

        ctk.CTkLabel(
            ref_inner,
            text="Referensi Algoritma",
            font=ctk.CTkFont("Georgia", 14, "bold"),
            text_color=Colors.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 10))

        refs = [
            "NIST FIPS 197 - Advanced Encryption Standard (AES), 2001",
            "Anderson, R. & Petitcolas, F. - On The Limits of Steganography, 1998",
            "Daemen, J. & Rijmen, V. - The Design of Rijndael: AES - The Advanced Encryption Standard, 2002",
        ]

        for ref in refs:
            row = ctk.CTkFrame(ref_inner, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkFrame(row, width=5, height=5, corner_radius=2, fg_color=Colors.ACCENT_GOLD).pack(side="left", padx=(0, 10), pady=4)
            ctk.CTkLabel(
                row,
                text=ref,
                font=ctk.CTkFont("Segoe UI", 11),
                text_color=Colors.TEXT_MUTED,
                anchor="w",
            ).pack(side="left")

    # ===================== ACTIONS =====================
    def _pick_carrier_image(self):
        path = filedialog.askopenfilename(
            title="Pilih Foto Carrier",
            filetypes=[("Gambar", "*.png *.jpg *.jpeg *.bmp *.tiff"), ("Semua", "*.*")],
        )
        if not path:
            return
        self._selected_image_path = path
        fname = Path(path).name
        self._img_label.configure(text=fname, text_color=Colors.TEXT_PRIMARY)
        self._load_preview(path, self._preview_label)
        self._update_capacity(path)

    def _pick_extract_image(self):
        path = filedialog.askopenfilename(
            title="Pilih Foto Berisi Pesan",
            filetypes=[("PNG", "*.png"), ("Semua Gambar", "*.png *.jpg *.jpeg"), ("Semua", "*.*")],
        )
        if not path:
            return
        self._extract_image_path = path
        fname = Path(path).name
        self._extract_img_label.configure(text=fname, text_color=Colors.TEXT_PRIMARY)
        self._load_preview(path, self._extract_preview_label)

    def _pick_output_dir(self):
        path = filedialog.askdirectory(title="Pilih Folder Simpan Hasil")
        if not path:
            return
        self._selected_output_dir = path
        self._outdir_label.configure(text=path, text_color=Colors.TEXT_PRIMARY)

    def _load_preview(self, image_path, label_widget):
        try:
            from PIL import Image as PILImage
            img = PILImage.open(image_path)
            img.thumbnail((280, 200), PILImage.LANCZOS)
            self._clear_label_image(label_widget)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            label_widget.configure(image=ctk_img, text="", height=200)
            label_widget._photo_ref = ctk_img
        except Exception as e:
            self._clear_label_image(label_widget)
            label_widget.configure(text="Tidak bisa memuat pratinjau", text_color=Colors.TEXT_MUTED)

    def _update_capacity(self, path):
        try:
            from PIL import Image
            img = Image.open(path).convert("RGB")
            w, h = img.size
            capacity_bytes = (w * h * 3) // 8 - 64
            capacity_chars = capacity_bytes // 2
            self._img_capacity_label.configure(
                text=f"Kapasitas: ~{capacity_chars:,} karakter",
                text_color=Colors.TEXT_MUTED,
            )
        except Exception:
            pass

    def _get_message_text(self):
        text = self._message_text.get("0.0", "end").strip()
        if self._message_placeholder_active:
            return ""
        return text

    def _update_char_count(self, event=None):
        try:
            text = self._get_message_text()
            self._char_count_label.configure(text=f"{len(text)} karakter")
        except Exception:
            pass

    def _on_message_focus_in(self, event=None):
        if self._message_placeholder_active:
            self._message_text.delete("0.0", "end")
            self._message_text.configure(text_color=Colors.TEXT_PRIMARY)
            self._message_placeholder_active = False

    def _on_message_focus_out(self, event=None):
        text = self._message_text.get("0.0", "end").strip()
        if not text:
            self._message_text.delete("0.0", "end")
            self._message_text.insert("0.0", self._message_placeholder)
            self._message_text.configure(text_color=Colors.TEXT_MUTED)
            self._message_placeholder_active = True
        self._update_char_count()

    def _reset_encode_form(self):
        self._selected_image_path = None
        self._selected_output_dir = None

        self._img_label.configure(
            text="Belum ada foto yang dipilih",
            text_color=Colors.TEXT_MUTED,
        )

        self._clear_label_image(self._preview_label)
        self._preview_label.configure(
            text="Pilih foto untuk pratinjau",
            image=None
        )

        self._img_capacity_label.configure(
            text="",
            text_color=Colors.TEXT_MUTED,
        )

        # Reset pesan
        self._message_text.delete("0.0", "end")
        self._message_text.insert("0.0", self._message_placeholder)
        self._message_text.configure(text_color=Colors.TEXT_MUTED)
        self._message_placeholder_active = True
        self._update_char_count()

        # Reset password
        self._password_var.set("")
        self._confirm_var.set("")

        # Password utama
        self._password_entry.configure(show="*")
        self._password_shown = False
        self._toggle_pw_btn.configure(text="Show")

        # Konfirmasi password
        self._confirm_entry.configure(show="*")
        self._confirm_password_shown = False
        self._toggle_confirm_btn.configure(text="Show")

        # Reset indikator kekuatan password
        self._pw_strength.update_strength("")
        self._pw_warning.configure(text="")

        # Reset folder output
        self._outdir_label.configure(
            text="Belum dipilih (akan menggunakan folder foto asal)",
            text_color=Colors.TEXT_MUTED,
        )

        # Reset nama file hasil
        self._output_filename_var.set("")

        # Nonaktifkan tombol encode
        self._encode_btn.configure(state="disabled")

    def _reset_decode_form(self):
        """Bersihkan form dan hasil pada halaman Ungkap Pesan."""
        self._extract_image_path = None

        self._extract_img_label.configure(
            text="Belum ada foto yang dipilih",
            text_color=Colors.TEXT_MUTED,
        )

        self._clear_label_image(self._extract_preview_label)
        self._extract_preview_label.configure(
            text="Pilih foto untuk pratinjau",
            image=None,
        )

        self._decode_pw_var.set("")
        self._decode_pw_warning.configure(text="")

        self._show_pw_var.set(False)
        self._decode_pw_entry.configure(show="*")

        self._result_text.configure(state="normal")
        self._result_text.delete("0.0", "end")
        self._result_text.configure(state="disabled")

        self._decode_btn.configure(state="normal")

    def _reset_check_form(self):
        """Bersihkan form dan hasil pada halaman Cek Status Foto."""
        self._check_image_path = None

        self._check_img_label.configure(
            text="Belum ada foto yang dipilih",
            text_color=Colors.TEXT_MUTED,
        )

        self._clear_label_image(self._check_preview_label)
        self._check_preview_label.configure(
            text="Pilih foto untuk pratinjau",
            image=None,
        )

        for widget in self._check_result_frame.winfo_children():
            widget.destroy()

        self._check_result_label = ctk.CTkLabel(
            self._check_result_frame,
            text="Pilih foto dan klik 'Cek Status' untuk memeriksa...",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_MUTED,
            justify="left",
            anchor="w",
        )
        self._check_result_label.pack(anchor="w", fill="x")

        self._check_btn.configure(state="normal")

    def _on_password_change(self, *args):
        pw = self._password_var.get()
        self._pw_strength.update_strength(pw)
        if self._pw_strength.score < 2:
            self._pw_warning.configure(
                text="Kata sandi terlalu lemah. Tambahkan panjang, angka, simbol, dan huruf besar/kecil."
            )
            self._encode_btn.configure(state="disabled")
        else:
            self._pw_warning.configure(text="")
            self._encode_btn.configure(state="normal")
    def _toggle_password_visibility(self):
        if self._password_shown:
            self._password_entry.configure(show="*")
            self._toggle_pw_btn.configure(text="Show")
            self._password_shown = False
        else:
            self._password_entry.configure(show="")
            self._toggle_pw_btn.configure(text="Hide")
            self._password_shown = True

    def _toggle_confirm_visibility(self):
        if self._confirm_password_shown:
            self._confirm_entry.configure(show="*")
            self._toggle_confirm_btn.configure(text="Show")
            self._confirm_password_shown = False
        else:
            self._confirm_entry.configure(show="")
            self._toggle_confirm_btn.configure(text="Hide")
            self._confirm_password_shown = True

    def _toggle_confirm_visibility(self):
        if self._confirm_password_shown:
            self._confirm_entry.configure(show="*")
            self._toggle_confirm_btn.configure(text="Show")
            self._confirm_password_shown = False
        else:
            self._confirm_entry.configure(show="")
            self._toggle_confirm_btn.configure(text="Hide")
            self._confirm_password_shown = True

    def _toggle_decode_pw_visibility(self):
        if self._show_pw_var.get():
            self._decode_pw_entry.configure(show="")
        else:
            self._decode_pw_entry.configure(show="*")

    def _run_encode(self):
        if not self._selected_image_path:
            messagebox.showerror("Error", "Pilih foto carrier terlebih dahulu.")
            return

        message = self._get_message_text()
        if not message:
            messagebox.showerror("Error", "Pesan tidak boleh kosong.")
            return

        password = self._password_var.get()
        if not password:
            messagebox.showerror("Error", "Kata sandi tidak boleh kosong.")
            return

        if self._pw_strength.score < 2:
            messagebox.showerror(
                "Error",
                "Kata sandi terlalu lemah. Tingkatkan hingga minimal 'Cukup' sebelum submit.",
            )
            return

        if password != self._confirm_var.get():
            messagebox.showerror("Error", "Kata sandi tidak cocok dengan konfirmasi.")
            return

        # Determine output path
        in_path = Path(self._selected_image_path)

        custom_name = self._output_filename_var.get().strip()
        if custom_name:
            # Bersihkan karakter yang tidak valid untuk nama file
            safe_name = "".join(c for c in custom_name if c not in '\\/:*?"<>|').strip()
            if not safe_name:
                safe_name = f"{in_path.stem}_warisan"
            if not safe_name.lower().endswith(".png"):
                safe_name += ".png"
        else:
            safe_name = f"{in_path.stem}_warisan.png"

        if self._selected_output_dir:
            output_path = Path(self._selected_output_dir) / safe_name
        else:
            output_path = in_path.parent / safe_name

        self._encode_btn.configure(state="disabled")
        self._encode_progress.pack(fill="x", padx=0, pady=(0, 8))
        self._encode_progress.start()

        def do_encode():
            try:
                encrypted = self.crypto.encrypt(message, password)
                self.stego.encode(str(self._selected_image_path), encrypted, str(output_path))
                try:
                    capacity = self.stego._calculate_capacity(
                        Image.open(self._selected_image_path).convert("RGB")
                    )

                    pdf_path = generate_report(
                        carrier_filename=os.path.basename(self._selected_image_path),
                        output_filename=os.path.basename(output_path),
                        message_length=len(message),
                        capacity_bytes=capacity,
                        output_dir=os.path.dirname(output_path),
                    )

                    pdf_info = f"\n\nLaporan PDF berhasil dibuat:\n{pdf_path}"

                except Exception as e:
                    pdf_info = f"\n\nFoto berhasil dibuat, tetapi laporan PDF gagal dibuat.\n{e}"
                
                success_message = f"{output_path}{pdf_info}"
                self.after(0, lambda: self._encode_done(success_message, True))
            except Exception as e:
                self.after(0, lambda: self._encode_done(str(e), False))

        threading.Thread(target=do_encode, daemon=True).start()

    def _encode_done(self, result, success):
        self._encode_progress.stop()
        self._encode_progress.pack_forget()
        self._encode_btn.configure(state="normal")

        if success:
            messagebox.showinfo(
                "Berhasil",
                f"Foto berhasil disimpan di:\n{result}" 
            )
            self._reset_encode_form()
        else:
            messagebox.showerror("Gagal", f"Terjadi kesalahan:\n{result}")

    def _run_decode(self):
        self._decode_pw_warning.configure(text="")

        if not self._extract_image_path:
            messagebox.showerror("Error", "Pilih foto berisi pesan terlebih dahulu.")
            return

        password = self._decode_pw_var.get().strip()

        if not password:
            self._decode_pw_warning.configure(
                text="Kata sandi wajib diisi."
            )
            return

        # Cek apakah foto mengandung pesan tersembunyi
        if not self.stego.check_has_hidden_message(self._extract_image_path):
            messagebox.showerror(
                "Error",
                "Foto ini tidak mengandung pesan warisan tersembunyi.\n\n"
                "Pastikan Anda memilih foto yang benar (biasanya diakhiri dengan '_warisan.png')."
            )
            return

        self._decode_btn.configure(state="disabled")
        self._decode_progress.pack(fill="x", padx=0, pady=(0, 8))
        self._decode_progress.start()

        def do_decode():
            try:
                encrypted_data = self.stego.decode(self._extract_image_path)
                decrypted_message = self.crypto.decrypt(encrypted_data, password)
                self.after(0, lambda: self._decode_done(decrypted_message, True))
            except Exception as e:
                self.after(0, lambda: self._decode_done(str(e), False))

        threading.Thread(target=do_decode, daemon=True).start()

    def _decode_done(self, result, success):
        self._decode_progress.stop()
        self._decode_progress.pack_forget()
        self._decode_btn.configure(state="normal")

        if success:
            self._result_text.configure(state="normal")
            self._result_text.delete("0.0", "end")
            self._result_text.insert("0.0", result)
            self._result_text.configure(state="disabled")
        else:
            self._result_text.configure(state="normal")
            self._result_text.delete("0.0", "end")
            self._result_text.insert("0.0", "[GAGAL] Kata sandi salah atau foto tidak mengandung pesan tersembunyi.")
            self._result_text.configure(state="disabled")
            messagebox.showerror("Gagal", f"Tidak dapat mendekripsi pesan.\nPastikan kata sandi benar dan foto ini memiliki pesan tersembunyi.\n\nDetail: {result}")

    def _copy_result(self):
        try:
            text = self._result_text.get("0.0", "end").strip()
            if text and not text.startswith("[GAGAL]"):
                self.clipboard_clear()
                self.clipboard_append(text)
                messagebox.showinfo("Sukses", "Pesan berhasil disalin ke clipboard.")
        except Exception:
            pass

    def _pick_check_image(self):
        """Fungsi untuk memilih foto yang akan dicek status enkripsinya."""
        path = filedialog.askopenfilename(
            title="Pilih Foto untuk Diperiksa",
            filetypes=[("PNG", "*.png"), ("Semua Gambar", "*.png *.jpg *.jpeg *.bmp"), ("Semua", "*.*")],
        )
        if not path:
            return
        self._check_image_path = path
        fname = Path(path).name
        self._check_img_label.configure(text=fname, text_color=Colors.TEXT_PRIMARY)
        self._load_preview(path, self._check_preview_label)

    def _run_check_status(self):
        """Fungsi untuk menjalankan pengecekan status foto."""
        if not self._check_image_path:
            messagebox.showerror("Error", "Pilih foto terlebih dahulu.")
            return

        self._check_btn.configure(state="disabled")
        self._check_progress.pack(fill="x", padx=0, pady=(8, 0))
        self._check_progress.start()

        def do_check():
            try:
                info = self.stego.get_message_info(self._check_image_path)
                self.after(0, lambda: self._check_status_done(info))
            except Exception as e:
                self.after(0, lambda: self._check_status_done({"error": str(e), "status": "Gagal membaca foto"}))

        threading.Thread(target=do_check, daemon=True).start()

    def _check_status_done(self, info):
        """Tampilkan hasil pengecekan status foto."""
        self._check_progress.stop()
        self._check_progress.pack_forget()
        self._check_btn.configure(state="normal")

        # Clear previous result
        for widget in self._check_result_frame.winfo_children():
            widget.destroy()

        if info.get("error"):
            error_header = ctk.CTkFrame(self._check_result_frame, fg_color="transparent")
            error_header.pack(anchor="w", fill="x", pady=(0, 8))

            ctk.CTkLabel(
                error_header,
                text="\u2716",
                font=ctk.CTkFont("Segoe UI", 18),
                text_color=Colors.ERROR_TEXT,
                width=24,
            ).pack(side="left", padx=(0, 8))

            status_label = ctk.CTkLabel(
                error_header,
                text=info['status'],
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                text_color=Colors.ERROR_TEXT,
                justify="left",
                anchor="w",
                wraplength=280,
            )
            status_label.pack(side="left", fill="x")

            if info.get("error"):
                error_label = ctk.CTkLabel(
                    self._check_result_frame,
                    text=f"Detail: {info['error']}",
                    font=ctk.CTkFont("Segoe UI", 10),
                    text_color=Colors.TEXT_MUTED,
                    justify="left",
                    anchor="w",
                    wraplength=300,
                )
                error_label.pack(anchor="w", fill="x")
        else:
            # Foto mengandung pesan
            if info.get("has_message"):
                status_color = Colors.SUCCESS_TEXT
                status_icon = "\u2713"
            else:
                status_color = Colors.TEXT_MUTED
                status_icon = "\u25CB"

            status_header = ctk.CTkFrame(self._check_result_frame, fg_color="transparent")
            status_header.pack(anchor="w", fill="x", pady=(0, 12))

            ctk.CTkLabel(
                status_header,
                text=status_icon,
                font=ctk.CTkFont("Segoe UI", 18, "bold"),
                text_color=status_color,
                width=24,
            ).pack(side="left", padx=(0, 8))

            status_label = ctk.CTkLabel(
                status_header,
                text=info['status'],
                font=ctk.CTkFont("Segoe UI", 12, "bold"),
                text_color=status_color,
                justify="left",
                anchor="w",
                wraplength=280,
            )
            status_label.pack(side="left", fill="x")

            # Info tabel
            info_data = [
                ("Ukuran Foto", f"{info['image_size'][0]} × {info['image_size'][1]} px"),
                ("Kapasitas", info['message_size_readable'] if info['has_message'] else f"{info['image_capacity']} bytes"),
                ("Ukuran Pesan", f"{info['message_size_readable']}" if info['has_message'] else "—"),
                ("Penggunaan", f"{info['usage_percent']:.1f}%" if info['has_message'] else "0%"),
            ]

            for label, value in info_data:
                row_frame = ctk.CTkFrame(self._check_result_frame, fg_color="transparent")
                row_frame.pack(anchor="w", fill="x", pady=3)

                label_widget = ctk.CTkLabel(
                    row_frame,
                    text=f"{label}:",
                    font=ctk.CTkFont("Segoe UI", 10),
                    text_color=Colors.TEXT_MUTED,
                    width=100,
                    anchor="w",
                )
                label_widget.pack(side="left")

                value_widget = ctk.CTkLabel(
                    row_frame,
                    text=value,
                    font=ctk.CTkFont("Segoe UI", 10, "bold"),
                    text_color=Colors.TEXT_PRIMARY,
                    anchor="w",
                )
                value_widget.pack(side="left", padx=(8, 0))
    
    def _show_loading_screen(self):

        self.loading_window = ctk.CTkToplevel()

        self.loading_window.overrideredirect(True)
        self.loading_window.configure(fg_color="#0d1a2e")

        width = 520
        height = 320

        screen_width = self.loading_window.winfo_screenwidth()
        screen_height = self.loading_window.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.loading_window.geometry(f"{width}x{height}+{x}+{y}")

        self.loading_window.attributes("-topmost", True)
        self.loading_window.focus_set()

        container = ctk.CTkFrame(
            self.loading_window,
            fg_color="#0d1a2e",
            corner_radius=0
        )
        container.pack(fill="both", expand=True)

        title = ctk.CTkLabel(
            container,
            text="WARISAN DIGITAL\nTERSEMBUNYI",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="white",
            justify="center"
        )
        title.pack(pady=(55, 10))

        subtitle = ctk.CTkLabel(
            container,
            text="Memuat aplikasi...",
            font=ctk.CTkFont(size=15),
            text_color="#d6d6d6"
        )
        subtitle.pack()

        self.loading_bar = ctk.CTkProgressBar(
            container,
            width=340,
            height=12,
            progress_color="#d4af37"
        )
        self.loading_bar.pack(pady=(35, 10))
        self.loading_bar.set(0)

        self.loading_percent = ctk.CTkLabel(
            container,
            text="0%",
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        self.loading_percent.pack()

        self.loading_window.update_idletasks()

        self.after(100, self._start_application)

    def _animate_loading(self, value=0):

        if value <= 100:
            self.loading_bar.set(value / 100)
            self.loading_percent.configure(text=f"{value}%")

            self.after(
                35,    
                lambda: self._animate_loading(value + 1)
            )

        else:
            self.after(300, self._finish_loading)

    def _finish_loading(self):
        self.loading_frame.lower()
        self.loading_frame.destroy()
        self._show_page("beranda")


if __name__ == "__main__":
    app = WaisanDigitalApp()
    app.mainloop()