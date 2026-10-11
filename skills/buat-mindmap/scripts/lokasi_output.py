#!/usr/bin/env python3
"""Tentukan folder output catatan dari lokasi file transkrip.

Aturannya:

1. Bila transkrip berada di dalam workspace Personal-OS, catatan ditulis ke
   `_output/` milik Project terdekat. Bila tidak ada Project di atasnya, ke
   `_output/` milik Entity terdekat.
2. Di luar itu, catatan ditulis di folder yang sama dengan transkrip.

Workspace Personal-OS dikenali dari berkas AGENTS.md yang frontmatter-nya
memuat `schema: personal-os/agents@1` dan field `level`. Folder ber-level
`group` dilewati, karena Group hanya pembungkus dan tidak punya `_output/`.

Skrip ini hanya mencetak path, tidak membuat folder.

Pemakaian:
    python3 lokasi_output.py <file-transkrip>

Keluaran (dua baris):
    <path folder output>
    <alasan singkat>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LEVEL_PEMILIK = ("project", "entity")


def baca_level(agents: Path) -> str | None:
    """Kembalikan nilai `level` bila berkas memakai skema personal-os/agents."""
    try:
        teks = agents.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    cocok = re.match(r"^---\s*\n(.*?)\n---", teks, re.DOTALL)
    if not cocok:
        return None
    kepala = cocok.group(1)
    if not re.search(r"^schema:\s*personal-os/agents@", kepala, re.MULTILINE):
        return None
    level = re.search(r"^level:\s*['\"]?(\w+)", kepala, re.MULTILINE)
    return level.group(1).lower() if level else None


def tentukan(transkrip: Path) -> tuple[Path, str]:
    transkrip = transkrip.expanduser().resolve()
    folder = transkrip.parent
    entity_terdekat: Path | None = None

    for kandidat in [folder, *folder.parents]:
        level = baca_level(kandidat / "AGENTS.md")
        if level == "project":
            return kandidat / "_output", f"di dalam Project Personal-OS: {kandidat.name}"
        if level == "entity" and entity_terdekat is None:
            entity_terdekat = kandidat

    if entity_terdekat is not None:
        return (
            entity_terdekat / "_output",
            f"di dalam Personal-OS tanpa Project, memakai Entity terdekat: {entity_terdekat.name}",
        )
    return folder, "di luar workspace Personal-OS, ditulis di samping transkrip"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    tujuan, alasan = tentukan(Path(sys.argv[1]))
    print(tujuan)
    print(alasan)
    return 0


if __name__ == "__main__":
    sys.exit(main())
