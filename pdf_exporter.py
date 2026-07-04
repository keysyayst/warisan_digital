"""
Modul PDF Exporter - Laporan bukti warisan digital
Dibuat dengan guard import agar tidak crash jika reportlab belum terpasang.
"""

from datetime import datetime
from pathlib import Path


def _check_reportlab() -> bool:
    try:
        import reportlab
        return True
    except ImportError:
        return False


def generate_report(
    carrier_filename: str,
    output_filename:  str,
    message_length:   int,
    capacity_bytes:   int,
    output_dir:       str,
) -> str:
    """
    Buat laporan PDF formal. Kembalikan path file PDF.
    Raise RuntimeError jika reportlab tidak tersedia.
    """
    if not _check_reportlab():
        raise RuntimeError(
            "Modul 'reportlab' belum terpasang.\n"
            "Jalankan perintah berikut di terminal:\n\n"
            "    pip install reportlab\n\n"
            "lalu buka aplikasi kembali."
        )

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rc
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table,
        TableStyle, HRFlowable
    )

    now       = datetime.now()
    tanggal   = now.strftime("%d %B %Y")
    waktu     = now.strftime("%H:%M:%S")
    doc_no    = f"WD-{now.strftime('%Y%m%d-%H%M%S')}"
    cap_chars = capacity_bytes // 2
    used_pct  = min(100.0, (message_length / max(cap_chars, 1)) * 100)

    stem       = Path(output_filename).stem
    report_path = str(Path(output_dir) / f"{stem}_laporan.pdf")

    # Warna
    DARK  = rc.HexColor("#0d1a2e")
    GOLD  = rc.HexColor("#c8a84b")
    LGRAY = rc.HexColor("#f4f4f4")
    MGRAY = rc.HexColor("#888888")
    DARK_TEXT = rc.HexColor("#1a1a2e")
    BORDER = rc.HexColor("#cccccc")
    AMBER  = rc.HexColor("#b07800")
    GREEN  = rc.HexColor("#2e7d4f")

    doc = SimpleDocTemplate(
        report_path, pagesize=A4,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.5*cm,  bottomMargin=2.5*cm,
    )
    styles = getSampleStyleSheet()

    def sty(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    s_title  = sty("T", fontName="Helvetica-Bold", fontSize=22, leading=26,
                   textColor=rc.white, alignment=TA_CENTER)
    s_sub    = sty("S", fontName="Helvetica", fontSize=10, leading=14,
                   textColor=rc.HexColor("#cccccc"), alignment=TA_CENTER)
    s_head   = sty("H", fontName="Helvetica-Bold", fontSize=11,
                   textColor=DARK_TEXT, spaceBefore=14, spaceAfter=6)
    s_body   = sty("B", fontName="Helvetica", fontSize=10,
                   textColor=DARK_TEXT, leading=14, spaceAfter=3)
    s_warn   = sty("W", fontName="Helvetica-Bold", fontSize=9,
                   textColor=AMBER, leading=13)
    s_footer = sty("F", fontName="Helvetica", fontSize=8,
                   textColor=MGRAY, alignment=TA_CENTER)

    W = doc.width
    story = []

    # Header
    header = Table([
    [Paragraph("<b>WARISAN DIGITAL TERSEMBUNYI</b>", s_title)],
    [Paragraph("Bukti Pembuatan Pesan Warisan Digital Terenkripsi", s_sub)]
    ], colWidths=[W])

    header.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), DARK),

        ("TOPPADDING",(0,0),(-1,0),18),
        ("BOTTOMPADDING",(0,0),(-1,0),6),

        ("TOPPADDING",(0,1),(-1,1),0),
        ("BOTTOMPADDING",(0,1),(-1,1),18),

        ("LEFTPADDING",(0,0),(-1,-1),18),
        ("RIGHTPADDING",(0,0),(-1,-1),18),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))

    story.append(header)

    # Meta
    meta = [
        ["Nomor Dokumen", f": {doc_no}"],
        ["Tanggal Dibuat", f": {tanggal}"],
        ["Waktu Dibuat",   f": {waktu} WIB"],
        ["Status",         ": TERENKRIPSI DAN TERSEMBUNYI"],
    ]
    mt = Table(meta, colWidths=[4.5*cm, W-4.5*cm])
    mt.setStyle(TableStyle([
        ("FONTNAME", (0,0),(0,-1), "Helvetica-Bold"),
        ("FONTNAME", (1,0),(1,-1), "Helvetica"),
        ("FONTSIZE", (0,0),(-1,-1), 10),
        ("TEXTCOLOR",(0,0),(-1,-1), DARK_TEXT),
        ("TEXTCOLOR",(1,3),(1,3),   GREEN),
        ("FONTNAME", (1,3),(1,3),   "Helvetica-Bold"),
        ("TOPPADDING",(0,0),(-1,-1),3),
        ("BOTTOMPADDING",(0,0),(-1,-1),3),
        ("LEFTPADDING",(0,0),(-1,-1),0),
    ]))
    story.append(mt)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=8))

    # Teknis
    story.append(Paragraph("1.  INFORMASI TEKNIS", s_head))
    tech = [
        ["PARAMETER", "NILAI"],
        ["Foto Asli (Carrier)",    carrier_filename],
        ["Foto Output (Stego)",    output_filename],
        ["Algoritma Enkripsi",     "AES-256-CBC (Advanced Encryption Standard)"],
        ["Metode Steganografi",    "LSB — 1 bit per kanal warna piksel (R, G, B)"],
        ["Derivasi Kunci",         "SHA-256 dari kata sandi pengguna"],
        ["Format Output",          "PNG (lossless — bit tidak berubah)"],
        ["Verifikasi Integritas",  "SHA-256 checksum embedded dalam payload"],
    ]
    tt = Table(tech, colWidths=[5.5*cm, W-5.5*cm])
    tt.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), DARK),
        ("TEXTCOLOR", (0,0),(-1,0), rc.white),
        ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",  (0,0),(-1,-1), 9),
        ("FONTNAME",  (0,1),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",  (1,1),(1,-1), "Helvetica"),
        ("TEXTCOLOR", (0,1),(-1,-1), DARK_TEXT),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [rc.white, LGRAY]),
        ("TOPPADDING",   (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("RIGHTPADDING", (0,0),(-1,-1), 8),
        ("GRID",         (0,0),(-1,-1), 0.5, BORDER),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(tt)

    # Statistik
    story.append(Paragraph("2.  STATISTIK PESAN", s_head))
    stat = [
        ["METRIK", "NILAI", "KETERANGAN"],
        ["Panjang Pesan",   f"{message_length:,} karakter", "Teks sebelum enkripsi"],
        ["Kapasitas Foto",  f"{cap_chars:,} karakter",      f"({capacity_bytes:,} byte)"],
        ["Penggunaan",      f"{used_pct:.1f}%",             f"{message_length:,} dari {cap_chars:,}"],
    ]
    st = Table(stat, colWidths=[4.5*cm, 3.5*cm, W-8*cm])
    st.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), DARK),
        ("TEXTCOLOR", (0,0),(-1,0), rc.white),
        ("FONTNAME",  (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",  (0,0),(-1,-1), 9),
        ("FONTNAME",  (0,1),(0,-1), "Helvetica-Bold"),
        ("FONTNAME",  (1,1),(-1,-1), "Helvetica"),
        ("TEXTCOLOR", (0,1),(-1,-1), DARK_TEXT),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [rc.white, LGRAY]),
        ("TOPPADDING",   (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("RIGHTPADDING", (0,0),(-1,-1), 8),
        ("GRID",         (0,0),(-1,-1), 0.5, BORDER),
        ("VALIGN",       (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(st)

    # Instruksi
    story.append(Paragraph("3.  INSTRUKSI UNTUK AHLI WARIS", s_head))
    for i, txt in enumerate([
        "Simpan file foto PNG yang tercantum di atas di tempat aman.",
        "Instal aplikasi Warisan Digital Tersembunyi di perangkat.",
        "Buka halaman Ungkap Pesan, pilih file foto PNG tersebut.",
        "Masukkan kata sandi yang telah diberikan oleh pewaris.",
        "Baca dan catat informasi warisan yang muncul di layar.",
    ], 1):
        story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;{i}.&nbsp; {txt}", s_body))

    story.append(Spacer(1, 8))

    # Peringatan
    story.append(Paragraph("4.  PERINGATAN KEAMANAN", s_head))
    warn_rows = [[Paragraph("PENTING — BACA SEBELUM MENYIMPAN",
                            sty("WH", fontName="Helvetica-Bold", fontSize=9, textColor=AMBER))]]
    for w in [
        "Simpan foto dalam format PNG. JANGAN konversi ke JPEG.",
        "JANGAN kirim via WhatsApp, Telegram, atau media sosial — kompresi otomatis merusak pesan.",
        "JANGAN edit foto dengan aplikasi apa pun setelah pesan disembunyikan.",
        "Simpan kata sandi di tempat terpisah yang hanya diketahui ahli waris terpercaya.",
    ]:
        warn_rows.append([Paragraph(f"  -  {w}", s_warn)])
    wt = Table(warn_rows, colWidths=[W])
    wt.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), rc.HexColor("#221900")),
        ("BOX",        (0,0),(-1,-1), 1, AMBER),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 10),
        ("RIGHTPADDING",  (0,0),(-1,-1), 10),
    ]))
    story.append(wt)
    story.append(Spacer(1, 14))

    # Footer
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=6))
    story.append(Paragraph(
        f"Aplikasi Warisan Digital Tersembunyi  |  {tanggal} {waktu}  |  {doc_no}",
        s_footer))
    story.append(Paragraph(
        "AES-256-CBC  |  LSB Steganography  |  SHA-256 Integrity Verification",
        s_footer))

    doc.build(story)
    return report_path