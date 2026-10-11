#!/usr/bin/env python3
"""Periksa outline mindmap, lalu tulis jadi file .xmind.

Outline ditulis sebagai JSON bersarang:

    {"title": "Judul sesi",
     "children": [
        {"title": "Cabang utama", "children": [
            {"title": "Sub-cabang", "children": [
                {"title": "Detail"}
            ]}
        ]}
     ]}

Dua subperintah:

    python3 mindmap_xmind.py cek  outline.json
    python3 mindmap_xmind.py buat outline.json -o mindmap.xmind

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


def jumlah_kata(teks: str) -> int:
    return len(teks.split())


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


def ke_topik(node: dict, akar: bool = False) -> dict:
    topik = {"id": uuid.uuid4().hex, "class": "topic", "title": str(node.get("title", "")).strip()}
    if akar:
        topik["structureClass"] = STRUKTUR
    anak = node.get("children") or []
    if anak:
        topik["children"] = {"attached": [ke_topik(a) for a in anak]}
    return topik


def buat(akar: dict, tujuan: Path) -> None:
    konten = [
        {
            "id": uuid.uuid4().hex,
            "class": "sheet",
            "title": str(akar.get("title", "Mindmap")).strip(),
            "rootTopic": ke_topik(akar, akar=True),
            "topicPositioning": "fixed",
        }
    ]
    metadata = {"creator": {"name": "tulis-catatan", "version": "1.0.0"}}
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
    p_cek.add_argument("outline", type=Path)
    p_buat = sub.add_parser("buat")
    p_buat.add_argument("outline", type=Path)
    p_buat.add_argument("-o", "--keluaran", type=Path, required=True)
    p_buat.add_argument("--paksa", action="store_true", help="tulis meski ada error bentuk")
    args = parser.parse_args()

    akar = json.loads(args.outline.read_text(encoding="utf-8"))
    error, peringatan = cek(akar)
    lapor(akar, error, peringatan)

    if args.perintah == "cek":
        return 1 if error else 0
    if error and not args.paksa:
        print("File .xmind tidak ditulis.")
        return 1
    buat(akar, args.keluaran)
    print(f"Ditulis: {args.keluaran}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
