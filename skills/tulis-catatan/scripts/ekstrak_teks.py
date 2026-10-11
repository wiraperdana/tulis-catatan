#!/usr/bin/env python3
"""Ekstrak teks dari dokumen jadi teks polos berpenanda lokasi.

Dipakai saat harness agent tidak bisa membaca format tertentu secara langsung.
Setiap bagian diberi penanda supaya catatan atau mindmap bisa mengutip
sumbernya, misalnya [Slide 14] atau [Halaman 5].

Format yang didukung, semuanya dengan pustaka bawaan Python kecuali PDF:

    .md .txt .csv            apa adanya
    .html .htm               tag dibuang
    .vtt .srt                baris waktu dibuang
    .docx                    paragraf dan tabel, penanda heading dipertahankan
    .pptx                    per slide, termasuk catatan pembicara
    .xlsx                    per sheet, sel dipisah tab
    .odt .odp                teks per paragraf
    .pdf                     per halaman, lewat `pdftotext` atau pustaka `pypdf`

    .png .jpg .jpeg .tif     hanya dengan --ocr

Isi berbentuk gambar. Slide tanpa teks, halaman PDF hasil scan, dan gambar di
dalam DOCX atau PPTX tidak hilang diam-diam. Skrip memberi penanda
[TANPA TEKS] di tempatnya. Dengan --gambar, gambar itu diekspor ke folder
supaya agent bisa membacanya dengan kemampuan visual. Halaman PDF tanpa teks
dirender jadi PNG lewat `pdftoppm`. Dengan --ocr, gambar raster yang diekspor
juga dibaca dengan `tesseract`, dan hasilnya disisipkan dengan penanda [OCR].

Pemakaian:
    python3 ekstrak_teks.py slide.pptx                          cetak ke stdout
    python3 ekstrak_teks.py slide.pptx -o slide.txt
    python3 ekstrak_teks.py slide.pptx -o slide.txt --gambar gambar/
    python3 ekstrak_teks.py scan.pdf -o scan.txt --gambar gambar/ --ocr

Kode keluar 3 berarti format tidak didukung atau alat yang dibutuhkan tidak ada.
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree

NS_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NS_A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
NS_S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
NS_TEXT = "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}"
NS_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
NS_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"

RASTER = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif"}
TEKS_MIN_HALAMAN = 30  # halaman PDF dengan teks lebih sedikit dianggap gambar

# Diisi main() dari argumen. Folder ekspor gambar, dan apakah OCR dijalankan.
FOLDER_GAMBAR: Path | None = None
PAKAI_OCR = False


class TidakDidukung(Exception):
    pass


def bahasa_ocr() -> str:
    hasil = subprocess.run(["tesseract", "--list-langs"], capture_output=True, text=True).stdout.split()
    return "+".join(b for b in ("ind", "eng") if b in hasil) or "eng"


def ocr(gambar: Path) -> str:
    if gambar.suffix.lower() not in RASTER:
        return ""
    keluaran = subprocess.run(
        ["tesseract", str(gambar), "-", "-l", bahasa_ocr()], capture_output=True, text=True
    )
    return re.sub(r"\n{3,}", "\n\n", keluaran.stdout).strip()


def catat_gambar(nama: str, data: bytes) -> list[str]:
    """Simpan satu gambar ke FOLDER_GAMBAR, kembalikan baris penandanya."""
    if FOLDER_GAMBAR is None:
        return []
    FOLDER_GAMBAR.mkdir(parents=True, exist_ok=True)
    tujuan = FOLDER_GAMBAR / nama
    tujuan.write_bytes(data)
    baris = [f"[Gambar: {tujuan}]"]
    if PAKAI_OCR:
        teks = ocr(tujuan)
        if teks:
            baris += [f"[OCR {tujuan.name}]", teks]
    return baris


def peta_relasi(z: zipfile.ZipFile, rels: str, dasar: str) -> dict[str, str]:
    """Petakan rId ke path gambar di dalam zip."""
    if rels not in z.namelist():
        return {}
    akar = ElementTree.fromstring(z.read(rels))
    peta = {}
    for r in akar.iter(f"{NS_REL}Relationship"):
        if r.get("Type", "").endswith("/image") and r.get("TargetMode") != "External":
            target = r.get("Target", "")
            peta[r.get("Id", "")] = str(Path(dasar) / target) if not target.startswith("/") else target[1:]
    return {k: re.sub(r"[^/]+/\.\./", "", v) for k, v in peta.items()}


def teks_polos(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def dari_html(path: Path) -> str:
    isi = teks_polos(path)
    isi = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", isi)
    isi = re.sub(r"(?i)<br\s*/?>|</(p|div|h[1-6]|li|tr)>", "\n", isi)
    isi = re.sub(r"<[^>]+>", " ", isi)
    return re.sub(r"[ \t]+", " ", html.unescape(isi))


def dari_subtitle(path: Path) -> str:
    baris = []
    for b in teks_polos(path).splitlines():
        b = b.strip()
        if not b or b == "WEBVTT" or b.isdigit() or "-->" in b:
            continue
        baris.append(re.sub(r"<[^>]+>", "", b))
    return "\n".join(baris)


def dari_docx(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        akar = ElementTree.fromstring(z.read("word/document.xml"))
        relasi = peta_relasi(z, "word/_rels/document.xml.rels", "word")
        data_gambar = {rid: z.read(t) for rid, t in relasi.items() if t in z.namelist()}
    badan = akar.find(f"{NS_W}body")
    hasil = []
    nomor_gambar = 0
    for elemen in list(badan if badan is not None else []):
        if elemen.tag == f"{NS_W}p":
            teks = "".join(t.text or "" for t in elemen.iter(f"{NS_W}t")).strip()
            for blip in elemen.iter(f"{NS_A}blip"):
                rid = blip.get(f"{NS_R}embed", "")
                if rid in data_gambar:
                    nomor_gambar += 1
                    hasil.append(f"[TANPA TEKS: gambar {nomor_gambar} di dokumen]")
                    hasil += catat_gambar(f"gambar{nomor_gambar}{Path(relasi[rid]).suffix}", data_gambar[rid])
            if not teks:
                continue
            gaya = elemen.find(f"{NS_W}pPr/{NS_W}pStyle")
            nama_gaya = gaya.get(f"{NS_W}val", "") if gaya is not None else ""
            tingkat = re.search(r"(?i)heading\s*(\d)", nama_gaya)
            hasil.append(("#" * int(tingkat.group(1)) + " " + teks) if tingkat else teks)
        elif elemen.tag == f"{NS_W}tbl":
            for baris in elemen.iter(f"{NS_W}tr"):
                sel = ["".join(t.text or "" for t in s.iter(f"{NS_W}t")).strip() for s in baris.iter(f"{NS_W}tc")]
                hasil.append("| " + " | ".join(sel) + " |")
    return "\n".join(hasil)


def nomor_urut(nama: str) -> int:
    angka = re.search(r"(\d+)", Path(nama).stem)
    return int(angka.group(1)) if angka else 0


def dari_pptx(path: Path) -> str:
    """Teks per slide, dengan penanda untuk slide yang isinya berupa gambar.

    Dua jenis isi berulang disaring, karena keduanya hanya noise:
    teks header atau footer yang muncul di banyak slide, dan gambar seperti
    logo yang dipakai di banyak slide. Slide dianggap "tanpa teks" bila teks
    uniknya, di luar teks berulang itu, kurang dari TEKS_MIN_HALAMAN karakter.
    """
    with zipfile.ZipFile(path) as z:
        nama_slide = sorted(
            (n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)), key=nomor_urut
        )
        data = []
        for nama in nama_slide:
            n = nomor_urut(nama)
            akar = ElementTree.fromstring(z.read(nama))
            paragraf = [
                "".join(t.text or "" for t in p.iter(f"{NS_A}t")).strip() for p in akar.iter(f"{NS_A}p")
            ]
            relasi = peta_relasi(z, f"ppt/slides/_rels/slide{n}.xml.rels", "ppt/slides")
            dipakai = {b.get(f"{NS_R}embed", "") for b in akar.iter(f"{NS_A}blip")}
            gambar = sorted({relasi[r] for r in dipakai if r in relasi and relasi[r] in z.namelist()})
            catatan = []
            nama_catatan = f"ppt/notesSlides/notesSlide{n}.xml"
            if nama_catatan in z.namelist():
                akar_c = ElementTree.fromstring(z.read(nama_catatan))
                catatan = [
                    "".join(t.text or "" for t in p.iter(f"{NS_A}t")).strip() for p in akar_c.iter(f"{NS_A}p")
                ]
                catatan = [c for c in catatan if c and not c.isdigit()]
            data.append((n, [x for x in paragraf if x], gambar, catatan))

        ambang = max(3, len(data) // 4)
        frek_teks: dict[str, int] = {}
        frek_gambar: dict[str, int] = {}
        for _, paragraf, gambar, _ in data:
            for x in set(paragraf):
                frek_teks[x] = frek_teks.get(x, 0) + 1
            for g in gambar:
                frek_gambar[g] = frek_gambar.get(g, 0) + 1
        teks_berulang = {x for x, k in frek_teks.items() if k >= ambang}
        gambar_berulang = {g for g, k in frek_gambar.items() if k >= ambang}

        hasil = []
        if gambar_berulang:
            daftar = ", ".join(Path(g).name for g in sorted(gambar_berulang))
            hasil += [f"[Gambar berulang di banyak slide, dilewati karena kemungkinan logo atau hiasan: {daftar}]", ""]
        for n, paragraf, gambar, catatan in data:
            hasil.append(f"[Slide {n}]")
            hasil.extend(paragraf)
            unik = "".join(x for x in paragraf if x not in teks_berulang)
            isi_gambar = [g for g in gambar if g not in gambar_berulang]
            if len(unik) < TEKS_MIN_HALAMAN:
                keterangan = f"{len(isi_gambar)} gambar" if isi_gambar else "tanpa gambar, kemungkinan bentuk atau diagram vektor"
                hasil.append(f"[TANPA TEKS: slide {n} hanya berisi teks berulang atau gambar, {keterangan}]")
            elif isi_gambar:
                hasil.append(f"[BERGAMBAR: slide {n} memuat {len(isi_gambar)} gambar]")
            for g in isi_gambar:
                hasil += catat_gambar(f"slide{n}_{Path(g).name}", z.read(g))
            if catatan:
                hasil.append(f"[Catatan pembicara slide {n}]")
                hasil.extend(catatan)
            hasil.append("")
    return "\n".join(hasil)


def dari_xlsx(path: Path) -> str:
    hasil = []
    with zipfile.ZipFile(path) as z:
        bersama: list[str] = []
        if "xl/sharedStrings.xml" in z.namelist():
            akar = ElementTree.fromstring(z.read("xl/sharedStrings.xml"))
            bersama = ["".join(t.text or "" for t in si.iter(f"{NS_S}t")) for si in akar.iter(f"{NS_S}si")]
        nama_sheet = []
        if "xl/workbook.xml" in z.namelist():
            wb = ElementTree.fromstring(z.read("xl/workbook.xml"))
            nama_sheet = [s.get("name", "") for s in wb.iter(f"{NS_S}sheet")]
        lembar = sorted(
            (n for n in z.namelist() if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n)), key=nomor_urut
        )
        for i, nama in enumerate(lembar):
            judul = nama_sheet[i] if i < len(nama_sheet) else f"Sheet {i + 1}"
            hasil.append(f"[Sheet: {judul}]")
            akar = ElementTree.fromstring(z.read(nama))
            for baris in akar.iter(f"{NS_S}row"):
                nilai = []
                for c in baris.iter(f"{NS_S}c"):
                    v = c.find(f"{NS_S}v")
                    if c.get("t") == "s" and v is not None and v.text and v.text.isdigit():
                        idx = int(v.text)
                        nilai.append(bersama[idx] if idx < len(bersama) else "")
                    elif c.get("t") == "inlineStr":
                        nilai.append("".join(t.text or "" for t in c.iter(f"{NS_S}t")))
                    else:
                        nilai.append(v.text if v is not None and v.text else "")
                if any(x.strip() for x in nilai):
                    hasil.append("\t".join(nilai))
            hasil.append("")
    return "\n".join(hasil)


def dari_odf(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        akar = ElementTree.fromstring(z.read("content.xml"))
    hasil = []
    for elemen in akar.iter():
        if elemen.tag in (f"{NS_TEXT}p", f"{NS_TEXT}h"):
            teks = "".join(elemen.itertext()).strip()
            if teks:
                hasil.append(teks)
    return "\n".join(hasil)


def dari_pdf(path: Path) -> str:
    if shutil.which("pdftotext"):
        keluaran = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"], capture_output=True, text=True, check=True
        ).stdout
        halaman = keluaran.split("\f")
    else:
        try:
            from pypdf import PdfReader  # type: ignore
        except ImportError as e:
            raise TidakDidukung(
                "PDF butuh `pdftotext` (paket poppler) atau pustaka Python `pypdf`. "
                "Bila keduanya tidak ada, baca PDF dengan kemampuan baca dokumen harness."
            ) from e
        halaman = [h.extract_text() or "" for h in PdfReader(str(path)).pages]
    if halaman and not halaman[-1].strip():
        halaman = halaman[:-1]  # pdftotext menambah satu halaman kosong di akhir
    bergambar = halaman_bergambar(path, len(halaman))
    hasil = []
    for i, isi in enumerate(halaman, start=1):
        hasil.append(f"[Halaman {i}]")
        if isi.strip():
            hasil.append(isi.rstrip())
        if len(isi.strip()) < TEKS_MIN_HALAMAN:
            hasil.append(f"[TANPA TEKS: halaman {i} kemungkinan gambar atau hasil scan]")
            hasil += render_halaman(path, i)
        elif i in bergambar:
            hasil.append(f"[BERGAMBAR: halaman {i} memuat gambar berukuran besar]")
            hasil += render_halaman(path, i)
        hasil.append("")
    return "\n".join(hasil)


def halaman_bergambar(path: Path, jumlah_halaman: int) -> set[int]:
    """Halaman yang memuat gambar besar, di luar gambar berulang seperti logo.

    Memakai `pdfimages -list` dari poppler. Bila alat itu tidak ada, kembalikan
    himpunan kosong, sehingga hanya halaman tanpa teks yang ditandai.
    """
    if not shutil.which("pdfimages"):
        return set()
    keluaran = subprocess.run(["pdfimages", "-list", str(path)], capture_output=True, text=True).stdout
    per_objek: dict[str, set[int]] = {}
    for baris in keluaran.splitlines()[2:]:
        kolom = baris.split()
        if len(kolom) < 12 or kolom[2] != "image":
            continue
        try:
            hal, lebar, tinggi = int(kolom[0]), int(kolom[3]), int(kolom[4])
        except ValueError:
            continue
        if lebar * tinggi >= 300 * 300:
            per_objek.setdefault(kolom[10], set()).add(hal)
    ambang = max(3, jumlah_halaman // 4)
    hasil: set[int] = set()
    for halaman_objek in per_objek.values():
        if len(halaman_objek) < ambang:
            hasil |= halaman_objek
    return hasil


def render_halaman(path: Path, nomor: int) -> list[str]:
    if FOLDER_GAMBAR is None:
        return []
    if not shutil.which("pdftoppm"):
        return ["[Halaman tidak bisa dirender: `pdftoppm` (poppler) tidak tersedia]"]
    FOLDER_GAMBAR.mkdir(parents=True, exist_ok=True)
    awalan = FOLDER_GAMBAR / f"halaman{nomor}"
    subprocess.run(
        ["pdftoppm", "-png", "-r", "150", "-f", str(nomor), "-l", str(nomor), "-singlefile", str(path), str(awalan)],
        check=True,
    )
    gambar = awalan.with_suffix(".png")
    baris = [f"[Gambar: {gambar}]"]
    if PAKAI_OCR:
        teks = ocr(gambar)
        if teks:
            baris += [f"[OCR {gambar.name}]", teks]
    return baris


def dari_gambar(path: Path) -> str:
    if not PAKAI_OCR:
        raise TidakDidukung(
            "berkas gambar. Baca dengan kemampuan visual harness, atau ulangi dengan --ocr."
        )
    teks = ocr(path)
    return f"[OCR {path.name}]\n{teks}" if teks else f"[TANPA TEKS: OCR tidak menemukan teks di {path.name}]"


PENGEKSTRAK = {
    ".md": teks_polos,
    ".markdown": teks_polos,
    ".txt": teks_polos,
    ".csv": teks_polos,
    ".html": dari_html,
    ".htm": dari_html,
    ".vtt": dari_subtitle,
    ".srt": dari_subtitle,
    ".docx": dari_docx,
    ".pptx": dari_pptx,
    ".xlsx": dari_xlsx,
    ".odt": dari_odf,
    ".odp": dari_odf,
    ".pdf": dari_pdf,
    **{akhiran: dari_gambar for akhiran in RASTER},
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("masukan", type=Path)
    parser.add_argument("-o", "--keluaran", type=Path)
    parser.add_argument("--gambar", type=Path, help="folder ekspor gambar dan halaman tanpa teks")
    parser.add_argument("--ocr", action="store_true", help="baca gambar raster dengan tesseract")
    args = parser.parse_args()

    global FOLDER_GAMBAR, PAKAI_OCR
    FOLDER_GAMBAR = args.gambar
    if args.ocr:
        if not shutil.which("tesseract"):
            print("Tidak bisa OCR: `tesseract` tidak tersedia. Baca gambar dengan kemampuan visual harness.", file=sys.stderr)
            return 3
        PAKAI_OCR = True
        if FOLDER_GAMBAR is None:
            FOLDER_GAMBAR = Path(tempfile.mkdtemp(prefix="ekstrak_gambar_"))

    akhiran = args.masukan.suffix.lower()
    fungsi = PENGEKSTRAK.get(akhiran)
    try:
        if fungsi is None:
            raise TidakDidukung(
                f"format {akhiran or '(tanpa akhiran)'} tidak didukung. "
                "Untuk .doc, .ppt, atau .xls lama, "
                "simpan ulang sebagai .docx, .pptx, atau .xlsx."
            )
        hasil = fungsi(args.masukan).strip() + "\n"
    except TidakDidukung as e:
        print(f"Tidak bisa diekstrak: {e}", file=sys.stderr)
        return 3

    if args.keluaran:
        args.keluaran.write_text(hasil, encoding="utf-8")
    else:
        sys.stdout.write(hasil)
    tanpa_teks = hasil.count("[TANPA TEKS")
    info = f"{args.masukan.name}: {len(hasil)} karakter"
    if tanpa_teks:
        info += f", {tanpa_teks} bagian tanpa teks"
        info += f", gambar di {FOLDER_GAMBAR}" if FOLDER_GAMBAR else ", ulangi dengan --gambar <folder> untuk membacanya"
    if PAKAI_OCR:
        info += f", OCR bahasa {bahasa_ocr()}"
    print(info, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
