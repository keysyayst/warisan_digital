"""
Komponen UI - Definisi warna, font, dan widget kustom
Sistem desain untuk Warisan Digital
"""

import tkinter as tk
import customtkinter as ctk
import re


class Colors:
    """Palet warna sistem desain."""
    # Background
    BG_DARK = "#141820"
    BG_MEDIUM = "#1c2230"

    # Sidebar
    SIDEBAR = "#0f1419"

    # Cards
    CARD = "#1c2230"
    CARD_HOVER = "#232d3f"

    # Navigation
    NAV_HOVER = "#262f3f"
    NAV_ACTIVE = "#1e3a5f"

    # Text
    TEXT_PRIMARY = "#e8edf4"
    TEXT_SECONDARY = "#9dafc7"
    TEXT_MUTED = "#5a6a80"

    # Borders
    BORDER = "#2a3545"

    # Accent colors
    ACCENT_GOLD = "#c9a84c"
    ACCENT_GOLD_HOVER = "#b8963c"
    ACCENT_TEAL = "#2a8a9e"
    ACCENT_TEAL_HOVER = "#1f7a8e"
    ACCENT_PURPLE = "#6b5acd"
    ACCENT_PURPLE_HOVER = "#5a4abc"

    # Status
    SUCCESS = "#2e7d4f"
    SUCCESS_TEXT = "#4caf80"
    ERROR = "#7d2e2e"
    ERROR_TEXT = "#ef5350"
    INFO = "#1a3a5a"
    INFO_TEXT = "#5b9bd5"


class Fonts:
    """Definisi font sistem."""
    DISPLAY = ("Georgia", 24, "bold")
    HEADING = ("Georgia", 16, "bold")
    SUBHEADING = ("Segoe UI", 14, "bold")
    BODY = ("Segoe UI", 12)
    BODY_BOLD = ("Segoe UI", 12, "bold")
    SMALL = ("Segoe UI", 10)
    MONO = ("Courier New", 12)


class SectionHeader(ctk.CTkFrame):
    """Header untuk setiap halaman/section."""

    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont("Georgia", 20, "bold"),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w",
        ).pack(side="left")

        ctk.CTkFrame(
            self,
            height=2,
            fg_color=Colors.BORDER,
        ).pack(side="left", fill="x", expand=True, padx=(16, 0), pady=(0, 4))


class StatusBar(ctk.CTkFrame):
    """Status bar di bawah layar."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            height=32,
            corner_radius=0,
            fg_color=Colors.SIDEBAR,
            border_width=0,
            **kwargs,
        )
        self.pack_propagate(False)

        self._status_label = ctk.CTkLabel(
            self,
            text="Siap",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        )
        self._status_label.pack(side="left", padx=16)

        ctk.CTkLabel(
            self,
            text="AES-256 | LSB Steganography | Python",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=Colors.TEXT_MUTED,
            anchor="e",
        ).pack(side="right", padx=16)

    def set_status(self, message: str, level: str = "info"):
        color_map = {
            "success": Colors.SUCCESS_TEXT,
            "error": Colors.ERROR_TEXT,
            "info": Colors.INFO_TEXT,
            "warning": Colors.ACCENT_GOLD,
        }
        color = color_map.get(level, Colors.TEXT_MUTED)
        self._status_label.configure(text=message, text_color=color)
        # Reset ke muted setelah 6 detik
        self.after(6000, lambda: self._status_label.configure(
            text="Siap", text_color=Colors.TEXT_MUTED
        ))


class PasswordStrengthMeter(ctk.CTkFrame):
    """Indikator kekuatan kata sandi visual."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._bar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._bar_frame.pack(fill="x")

        self._bars = []
        self.score = 0
        for i in range(4):
            bar = ctk.CTkFrame(
                self._bar_frame,
                height=4,
                corner_radius=2,
                fg_color=Colors.BORDER,
            )
            bar.pack(side="left", fill="x", expand=True, padx=2)
            self._bars.append(bar)

        self._label = ctk.CTkLabel(
            self,
            text="Masukkan kata sandi",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        )
        self._label.pack(anchor="w", pady=(4, 0))

    def update_strength(self, password: str):
        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
            score += 1
        if re.search(r"[0-9]", password) and re.search(r"[^A-Za-z0-9]", password):
            score += 1

        color_map = {
            0: (Colors.BORDER, "Masukkan kata sandi"),
            1: ("#c0392b", "Lemah"),
            2: ("#e67e22", "Cukup"),
            3: ("#f1c40f", "Kuat"),
            4: ("#2ecc71", "Sangat Kuat"),
        }

        if not password:
            score = 0

        bar_color, label_text = color_map[score]
        self.score = score

        for i, bar in enumerate(self._bars):
            if i < score:
                bar.configure(fg_color=bar_color)
            else:
                bar.configure(fg_color=Colors.BORDER)

        self._label.configure(
            text=label_text,
            text_color=bar_color if password else Colors.TEXT_MUTED,
        )


class AnimatedButton(ctk.CTkButton):
    """Tombol dengan efek hover yang lebih halus."""
    pass


class InfoCard(ctk.CTkFrame):
    """Kartu informasi sederhana."""

    def __init__(self, parent, title: str, content: str, accent_color: str = None, **kwargs):
        super().__init__(parent, fg_color=Colors.CARD, corner_radius=12, **kwargs)

        if accent_color:
            ctk.CTkFrame(self, height=3, fg_color=accent_color, corner_radius=0).pack(fill="x")

        inner = ctk.CTkFrame(self, fg_color="transparent")
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
            text=content,
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=Colors.TEXT_SECONDARY,
            wraplength=260,
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(6, 0))


class FileDropZone(ctk.CTkFrame):
    """Area drag-and-drop untuk file."""

    def __init__(self, parent, label_text: str = "Klik atau seret file ke sini", **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BG_DARK,
            border_color=Colors.BORDER,
            border_width=1,
            corner_radius=10,
            **kwargs,
        )

        ctk.CTkLabel(
            self,
            text=label_text,
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=Colors.TEXT_MUTED,
        ).pack(expand=True)


class ScrollableFrame(ctk.CTkScrollableFrame):
    """Frame yang dapat di-scroll."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color="transparent",
            scrollbar_button_color=Colors.BORDER,
            scrollbar_button_hover_color=Colors.ACCENT_GOLD,
            **kwargs,
        )