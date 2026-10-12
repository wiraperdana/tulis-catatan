#!/usr/bin/env python3
"""Periksa outline mindmap, lalu tulis jadi file .xmind.

Outline ditulis sebagai JSON bersarang:

    {"title": "Judul sesi",
     "children": [
        {"title": "Cabang utama", "sumber": "Slide 3-7", "children": [
            {"title": "Sub-cabang", "children": [
                {"title": "Detail"}
            ]}
        ]}
     ]}

Outline multi-sheet ditulis sebagai {"sheets": [akar, akar, ...]}; tiap sheet
diperiksa terpisah dan ditulis ke satu berkas .xmind.

Node konsep boleh ditulis sebagai objek dengan elemen penjelasan opsional:

    {"concept": "Gini index", "sumber": "[07a] s24", "definisi": "...",
     "langkah": "G = 1 - Σp²", "contoh": "...", "hubungan": "..."}

Elemen yang dikenal: definisi, jenis, tujuan, kapan, asumsi, urutan, langkah,
contoh, interpretasi, pembeda, hubungan, plusminus, jebakan, catatan. Nilai
daftar menjadi anak level berikutnya. Field "sumber" boleh ada di node mana
pun; isinya ditulis sebagai catatan (notes) Xmind, bukan label.

Dua opsi menentukan bentuk mindmap:

    --isi  penjelasan (default)  konsep ditulis sebagai objek berelemen
           ringkasan             label pendek saja; objek konsep ditolak
    --alur kronologi (default)   urutan mengikuti sumber; cabang dan konsep
                                 diberi nomor, dan "sumber" tidak boleh mundur
           konsep                dikelompokkan menurut topik, tanpa nomor

Dua subperintah:

    python3 mindmap_xmind.py cek  outline.json [--isi ...] [--alur ...]
    python3 mindmap_xmind.py buat outline.json -o mindmap.xmind [--isi ...] [--alur ...]

`buat` selalu menjalankan `cek` lebih dulu dan menolak menulis bila ada error,
kecuali diberi --paksa.

Kenapa ada aturan bentuk: mindmap yang semua cabangnya dibuka harus tetap
terbaca saat dicetak di satu lembar A4 landscape. Terlalu dangkal membuatnya
tidak berguna, terlalu dalam atau terlalu banyak node membuat huruf mengecil
sampai tidak terbaca. Batas di bawah adalah titik awal, kalibrasi dengan cetak
uji bila perlu.

File .xmind adalah arsip zip berisi content.json, metadata.json, dan
manifest.json, jadi cukup pustaka bawaan Python.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
import zipfile
from pathlib import Path

CABANG_UTAMA_MIN, CABANG_UTAMA_MAKS = 4, 7
ANAK_MAKS = 5
KEDALAMAN_MIN, KEDALAMAN_MAKS = 3, 4
PORSI_LEVEL4_MAKS = 0.15
NODE_MIN, NODE_MAKS = 40, 70
KATA_MAKS = {1: 5, 2: 5, 3: 10, 4: 10}
KATA_JUDUL_MAKS = 8

STRUKTUR = "org.xmind.ui.map.unbalanced"
NOMOR = re.compile(r"^\d+(\.\d+)*\.?\s+")


def jumlah_kata(teks: str) -> int:
    """Hitung kata label. Nomor urut alur kronologi ("2.3 ") tidak dihitung."""
    return len(NOMOR.sub("", teks).split())


def jelajah(node: dict, level: int = 0, jalur: str = ""):
    """Hasilkan (level, jalur, node) untuk setiap node, akar di level 0."""
    judul = str(node.get("title", "")).strip()
    jalur_ini = f"{jalur} > {judul}" if jalur else judul
    yield level, jalur_ini, node
    for anak in node.get("children", []) or []:
        yield from jelajah(anak, level + 1, jalur_ini)


def kedalaman(node: dict) -> int:
    anak = node.get("children") or []
    return 0 if not anak else 1 + max(kedalaman(a) for a in anak)


def cek(akar: dict) -> tuple[list[str], list[str]]:
    error: list[str] = []
    peringatan: list[str] = []

    judul_akar = str(akar.get("title", "")).strip()
    if not judul_akar:
        error.append("akar tidak punya title")
    elif jumlah_kata(judul_akar) > KATA_JUDUL_MAKS:
        peringatan.append(f"judul akar {jumlah_kata(judul_akar)} kata, idealnya maksimal {KATA_JUDUL_MAKS}")

    utama = akar.get("children") or []
    if not CABANG_UTAMA_MIN <= len(utama) <= CABANG_UTAMA_MAKS:
        error.append(f"cabang utama ada {len(utama)}, harus {CABANG_UTAMA_MIN} sampai {CABANG_UTAMA_MAKS}")

    for cabang in utama:
        d = 1 + kedalaman(cabang)
        if d < KEDALAMAN_MIN:
            error.append(
                f"cabang '{cabang.get('title')}' hanya {d} level, setiap cabang utama harus mencapai level {KEDALAMAN_MIN}"
            )

    semua = list(jelajah(akar))
    node_isi = [(lv, jl, n) for lv, jl, n in semua if lv > 0]
    total = len(node_isi)
    level4 = sum(1 for lv, _, _ in node_isi if lv == 4)

    for lv, jl, n in node_isi:
        judul = str(n.get("title", "")).strip()
        if not judul:
            error.append(f"node tanpa title di: {jl}")
            continue
        if lv > KEDALAMAN_MAKS:
            error.append(f"level {lv} melebihi batas {KEDALAMAN_MAKS}: {jl}")
        batas = KATA_MAKS.get(lv, KATA_MAKS[4])
        if jumlah_kata(judul) > batas:
            error.append(f"label level {lv} berisi {jumlah_kata(judul)} kata, maksimal {batas}: '{judul}'")
        if "$" in judul or re.search(r"\\[a-zA-Z]+", judul):
            error.append(f"label memuat LaTeX, tulis nama rumusnya saja: '{judul}'")
        if "\u2014" in judul:
            error.append(f"label memuat em dash: '{judul}'")
        anak = n.get("children") or []
        if len(anak) > ANAK_MAKS:
            error.append(f"'{judul}' punya {len(anak)} anak, maksimal {ANAK_MAKS}")
        elif len(anak) == 1:
            peringatan.append(f"'{judul}' hanya punya 1 anak, pertimbangkan menggabungkannya")

    if total > NODE_MAKS:
        error.append(f"total {total} node, maksimal {NODE_MAKS} agar terbaca di A4")
    elif total < NODE_MIN:
        peringatan.append(f"total {total} node, di bawah {NODE_MIN}. Wajar untuk sesi pendek")

    if total and level4 / total > PORSI_LEVEL4_MAKS:
        error.append(
            f"{level4} node level 4 ({level4 / total:.0%}), maksimal {PORSI_LEVEL4_MAKS:.0%} dari {total} node"
        )

    return error, peringatan


# Katalog elemen penjelasan konsep. Semua opsional; pilih yang logis untuk jenis
# konsepnya (lihat SKILL.md buat-mindmap, bagian "Mindmap penjelasan konsep").
# Urutan di sini = urutan tampil. "urutan" = tahapan tanpa hitungan, "langkah" =
# langkah matematis; "hubungan" = kaitan dengan bagian sebelum atau sesudahnya.
ELEMEN = [
    ("definisi", "Definisi"), ("jenis", "Jenis/komponen"), ("tujuan", "Tujuan"), ("kapan", "Kapan"),
    ("asumsi", "Asumsi"), ("urutan", "Urutan"), ("langkah", "Langkah"), ("contoh", "Contoh"),
    ("interpretasi", "Interpretasi"), ("pembeda", "Pembeda"), ("hubungan", "Hubungan"),
    ("plusminus", "Kelebihan/kekurangan"), ("jebakan", "Jebakan"), ("catatan", "Catatan"),
]
JUDUL_DAFTAR = {"langkah": "Langkah matematis", "urutan": "Urutan"}


def kembangkan(node: dict) -> dict:
    """Ubah objek konsep {"concept": ..., "definisi": ..., ...} menjadi node biasa.

    Elemen bernilai teks menjadi label "Elemen: isi". Elemen bernilai daftar
    menjadi node elemen dengan anak per butir. Node biasa diteruskan apa adanya.
    Node hasil konsep ditandai "_konsep" agar pemeriksaan --isi mengenalinya."""
    if "concept" not in node:
        hasil = {k: v for k, v in node.items() if k != "children"}
        if node.get("children"):
            hasil["children"] = [kembangkan(a) for a in node["children"]]
        return hasil
    asing = set(node) - {k for k, _ in ELEMEN} - {"concept", "sumber"}
    if asing:
        raise SystemExit(f"Elemen tidak dikenal pada '{node['concept']}': {sorted(asing)}")
    anak = []
    for kunci, label in ELEMEN:
        isi = node.get(kunci)
        if not isi:
            continue
        if isinstance(isi, list):
            anak.append({"title": JUDUL_DAFTAR.get(kunci, label), "children": [{"title": x} for x in isi]})
        else:
            anak.append({"title": f"{label}: {isi}"})
    if len(anak) < 2:
        raise SystemExit(f"Konsep '{node['concept']}' butuh minimal 2 elemen")
    hasil = {"title": node["concept"], "children": anak, "_konsep": True}
    if node.get("sumber"):
        hasil["sumber"] = node["sumber"]
    return hasil


def cek_isi(akar: dict, isi: str) -> tuple[list[str], list[str]]:
    """--isi ringkasan menolak objek konsep; --isi penjelasan mengingatkan bila tidak ada."""
    konsep = [n for _, _, n in jelajah(akar) if n.get("_konsep")]
    if isi == "ringkasan" and konsep:
        return [f"--isi ringkasan, tetapi ada {len(konsep)} objek konsep. Tulis label biasa, atau pakai --isi penjelasan"], []
    if isi == "penjelasan" and not konsep:
        return [], ["--isi penjelasan, tetapi tidak ada objek konsep. Ini mindmap ringkasan; pakai --isi ringkasan bila disengaja"]
    return [], []


def posisi(sumber: str):
    """Ambil posisi pertama dalam teks sumber sebagai kunci urut.

    Dikenali: "[07a] s24" (kode dek dan nomor slide), stempel waktu "00:12:30"
    atau "12:30", dan "slide 6", "hal. 12", "halaman 12", "s6". Kembalikan None
    bila tidak ada posisi yang bisa dibaca."""
    m = re.search(r"\[(\w+)\]\s*s(\d+)", sumber)
    if m:
        return (m.group(1), int(m.group(2)))
    m = re.search(r"\b(\d{1,2}):(\d{2})(?::(\d{2}))?\b", sumber)
    if m:
        a, b, c = m.groups()
        detik = int(a) * 3600 + int(b) * 60 + int(c) if c else int(a) * 60 + int(b)
        return ("", detik)
    m = re.search(r"(?i)\b(?:slide|hal(?:aman)?\.?|s)\s*(\d+)", sumber)
    if m:
        return ("", int(m.group(1)))
    return None


def cek_urutan(akar: dict) -> list[str]:
    """Alur kronologi: posisi sumber tidak boleh mundur dalam urutan baca sheet."""
    error, lalu = [], None
    for _, _, n in jelajah(akar):
        p = posisi(str(n.get("sumber", "")))
        if p is None:
            continue
        if lalu and p < lalu[0]:
            error.append(f"urutan mundur: '{n['title']}' ({n['sumber']}) muncul setelah '{lalu[1]}' ({lalu[2]})")
        lalu = (p, n["title"], n["sumber"])
    return error


def beri_nomor(akar: dict) -> None:
    """Alur kronologi: cabang utama diberi "1.", "2.", konsep di bawahnya "1.1", "1.2"."""
    for i, cabang in enumerate(akar.get("children") or [], 1):
        if not NOMOR.match(cabang["title"]):
            cabang["title"] = f"{i}. {cabang['title']}"
        for j, anak in enumerate(cabang.get("children") or [], 1):
            if not NOMOR.match(anak["title"]):
                anak["title"] = f"{i}.{j} {anak['title']}"


def ke_topik(node: dict, akar: bool = False) -> dict:
    topik = {"id": uuid.uuid4().hex, "class": "topic", "title": str(node.get("title", "")).strip()}
    if akar:
        topik["structureClass"] = STRUKTUR
    if node.get("sumber"):
        topik["notes"] = {"plain": {"content": f"Sumber: {node['sumber']}"}}
    anak = node.get("children") or []
    if anak:
        topik["children"] = {"attached": [ke_topik(a) for a in anak]}
    return topik


def buat(sheets: list[dict], tujuan: Path) -> None:
    """Tulis satu berkas .xmind. Satu sheet per akar; satu akar = mindmap biasa."""
    konten = [
        {
            "id": uuid.uuid4().hex,
            "class": "sheet",
            "title": str(akar.get("title", "Mindmap")).strip(),
            "rootTopic": ke_topik(akar, akar=True),
            "topicPositioning": "fixed",
        }
        for akar in sheets
    ]
    metadata = {"creator": {"name": "tulis-catatan", "version": "1.1.0"}}
    manifest = {"file-entries": {"content.json": {}, "metadata.json": {}}}
    with zipfile.ZipFile(tujuan, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("content.json", json.dumps(konten, ensure_ascii=False))
        z.writestr("metadata.json", json.dumps(metadata))
        z.writestr("manifest.json", json.dumps(manifest))


def lapor(akar: dict, error: list[str], peringatan: list[str]) -> None:
    semua = [lv for lv, _, _ in jelajah(akar) if lv > 0]
    per_level = {lv: semua.count(lv) for lv in sorted(set(semua))}
    ringkas = ", ".join(f"level {lv}: {n}" for lv, n in per_level.items())
    print(f"{len(semua)} node ({ringkas})")
    for p in peringatan:
        print(f"PERINGATAN: {p}")
    for e in error:
        print(f"ERROR: {e}")
    print("Lolos." if not error else f"{len(error)} error, perbaiki outline lalu cek ulang.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="perintah", required=True)
    p_cek = sub.add_parser("cek")
    p_buat = sub.add_parser("buat")
    for p in (p_cek, p_buat):
        p.add_argument("outline", type=Path)
        p.add_argument("--isi", choices=["penjelasan", "ringkasan"], default="penjelasan",
                       help="penjelasan (default): konsep berelemen; ringkasan: label pendek")
        p.add_argument("--alur", choices=["kronologi", "konsep"], default="kronologi",
                       help="kronologi (default): ikuti urutan sumber dan beri nomor; konsep: kelompok topik")
    p_buat.add_argument("-o", "--keluaran", type=Path, required=True)
    p_buat.add_argument("--paksa", action="store_true", help="tulis meski ada error bentuk")
    args = parser.parse_args()

    data = json.loads(args.outline.read_text(encoding="utf-8"))
    # Outline multi-sheet: {"sheets": [akar, akar, ...]}. Tiap sheet diperiksa terpisah.
    sheets = [kembangkan(s) for s in data["sheets"]] if "sheets" in data else [kembangkan(data)]
    print(f"Opsi: --isi {args.isi} --alur {args.alur}")
    ada_error = False
    for akar in sheets:
        if len(sheets) > 1:
            print(f"== {akar.get('title', '')}")
        error, peringatan = cek(akar)
        e2, p2 = cek_isi(akar, args.isi)
        error, peringatan = error + e2, peringatan + p2
        if args.alur == "kronologi":
            error += cek_urutan(akar)
            beri_nomor(akar)
        lapor(akar, error, peringatan)
        ada_error = ada_error or bool(error)

    if args.perintah == "cek":
        return 1 if ada_error else 0
    if ada_error and not args.paksa:
        print("File .xmind tidak ditulis.")
        return 1
    buat(sheets, args.keluaran)
    print(f"Ditulis: {args.keluaran} ({len(sheets)} sheet)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
