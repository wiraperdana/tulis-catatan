#!/usr/bin/env python3
"""Rapikan transkrip rekaman jadi teks ringkas bertimestamp.

Transkrip .vtt dari Zoom memecah satu kalimat jadi banyak potongan, dan tiap
potongan membawa dua timestamp. Skrip ini menggabungkan potongan berurutan dari
pembicara yang sama jadi satu blok, lalu menulis tiap blok sebagai:

    [hh:mm:ss] Nama Pembicara: teks

Hasilnya biasanya sekitar 30 persen lebih pendek, tanpa membuang isi ucapan.

Format masukan: .vtt, .srt, .txt, .md, dan .docx. Hanya pustaka bawaan Python.

Pemakaian:
    python3 rapikan_transkrip.py rekaman.vtt -o rekaman_rapi.txt
    python3 rapikan_transkrip.py rekaman.vtt            # cetak ke stdout
"""
from __future__ import annotations

import argparse
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

# Batas penggabungan. Blok yang terlalu panjang menyulitkan pengutipan timestamp.
JEDA_MAKS_DETIK = 20.0
PANJANG_BLOK_MAKS = 1200

POLA_WAKTU = re.compile(
    r"(\d{1,2}:)?(\d{1,2}):(\d{2})[.,](\d{1,3})\s*-->\s*(\d{1,2}:)?(\d{1,2}):(\d{2})[.,](\d{1,3})"
)
POLA_PEMBICARA = re.compile(r"^([^:\[\]]{1,60}?):\s+(.*)$")
POLA_TAG_VTT = re.compile(r"<[^>]+>")


@dataclass
class Potongan:
    mulai: float
    selesai: float
    pembicara: str
    teks: str


def ke_detik(jam: str | None, menit: str, detik: str, mili: str) -> float:
    j = int(jam.rstrip(":")) if jam else 0
    return j * 3600 + int(menit) * 60 + int(detik) + int(mili.ljust(3, "0")) / 1000


def format_waktu(detik: float) -> str:
    d = int(detik)
    return f"{d // 3600:02d}:{(d % 3600) // 60:02d}:{d % 60:02d}"


def pisah_pembicara(teks: str) -> tuple[str, str]:
    cocok = POLA_PEMBICARA.match(teks)
    if cocok and not cocok.group(1).strip().isdigit():
        return cocok.group(1).strip(), cocok.group(2).strip()
    return "", teks.strip()


def baca_berwaktu(isi: str) -> list[Potongan]:
    """Parser untuk .vtt dan .srt. Keduanya berupa cue dengan baris waktu."""
    hasil: list[Potongan] = []
    for blok in re.split(r"\n\s*\n", isi.replace("\r\n", "\n")):
        baris = [b for b in blok.strip().split("\n") if b.strip()]
        for i, b in enumerate(baris):
            cocok = POLA_WAKTU.search(b)
            if not cocok:
                continue
            g = cocok.groups()
            mulai = ke_detik(g[0], g[1], g[2], g[3])
            selesai = ke_detik(g[4], g[5], g[6], g[7])
            teks = " ".join(POLA_TAG_VTT.sub("", t).strip() for t in baris[i + 1 :])
            if teks:
                pembicara, teks = pisah_pembicara(teks)
                hasil.append(Potongan(mulai, selesai, pembicara, teks))
            break
    return hasil


def baca_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    akar = ElementTree.fromstring(xml)
    paragraf = []
    for p in akar.iter(f"{ns}p"):
        teks = "".join(t.text or "" for t in p.iter(f"{ns}t"))
        if teks.strip():
            paragraf.append(teks.strip())
    return "\n".join(paragraf)


def gabungkan(potongan: list[Potongan]) -> list[Potongan]:
    blok: list[Potongan] = []
    for p in potongan:
        if (
            blok
            and p.pembicara == blok[-1].pembicara
            and p.mulai - blok[-1].selesai <= JEDA_MAKS_DETIK
            and len(blok[-1].teks) + len(p.teks) <= PANJANG_BLOK_MAKS
        ):
            blok[-1].teks += " " + p.teks
            blok[-1].selesai = p.selesai
        else:
            blok.append(Potongan(p.mulai, p.selesai, p.pembicara, p.teks))
    return blok


def tulis_blok(blok: list[Potongan]) -> str:
    keluaran = []
    for b in blok:
        kepala = f"[{format_waktu(b.mulai)}]"
        if b.pembicara:
            kepala += f" {b.pembicara}:"
        keluaran.append(f"{kepala} {b.teks}")
    return "\n\n".join(keluaran) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("masukan", type=Path)
    parser.add_argument("-o", "--keluaran", type=Path)
    args = parser.parse_args()

    akhiran = args.masukan.suffix.lower()
    if akhiran == ".docx":
        isi = baca_docx(args.masukan)
    else:
        isi = args.masukan.read_text(encoding="utf-8-sig", errors="replace")

    potongan = baca_berwaktu(isi) if akhiran in {".vtt", ".srt"} or POLA_WAKTU.search(isi) else []

    if potongan:
        blok = gabungkan(potongan)
        hasil = tulis_blok(blok)
        pembicara = sorted({b.pembicara for b in blok if b.pembicara})
        info = (
            f"potongan masuk: {len(potongan)}, blok keluar: {len(blok)}, "
            f"durasi: {format_waktu(potongan[-1].selesai)}, "
            f"pembicara: {', '.join(pembicara) or '(tidak ada label)'}"
        )
    else:
        # Teks polos tanpa baris waktu. Rapikan spasi, pertahankan paragraf.
        hasil = re.sub(r"[ \t]+", " ", isi).strip() + "\n"
        info = "tanpa timestamp: catatan tidak bisa mengutip waktu, pakai nomor paragraf"

    if args.keluaran:
        args.keluaran.write_text(hasil, encoding="utf-8")
    else:
        sys.stdout.write(hasil)
    print(f"{info}, karakter: {len(isi)} -> {len(hasil)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
