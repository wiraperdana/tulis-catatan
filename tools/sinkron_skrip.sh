#!/usr/bin/env bash
# Skrip bersama hidup di skills/tulis-catatan/scripts/ sebagai sumber kebenaran.
# Setiap skill harus berdiri sendiri saat dipasang, jadi buat-mindmap membawa
# salinannya sendiri. Skrip ini menyalin atau memeriksa kesamaannya.
#
# Pemakaian:
#   tools/sinkron_skrip.sh          salin dari tulis-catatan ke buat-mindmap
#   tools/sinkron_skrip.sh --cek    hanya periksa, keluar 1 bila berbeda
set -euo pipefail

AKAR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ASAL="$AKAR/skills/tulis-catatan/scripts"
TUJUAN="$AKAR/skills/buat-mindmap/scripts"
BERSAMA=(mindmap_xmind.py lokasi_output.py ekstrak_teks.py)

beda=0
for f in "${BERSAMA[@]}"; do
  if [[ "${1:-}" == "--cek" ]]; then
    if ! cmp -s "$ASAL/$f" "$TUJUAN/$f"; then
      printf 'Berbeda: %s. Jalankan tools/sinkron_skrip.sh\n' "$f"
      beda=1
    fi
  else
    mkdir -p "$TUJUAN"
    cp "$ASAL/$f" "$TUJUAN/$f"
  fi
done
[[ "${1:-}" == "--cek" ]] && [[ $beda -eq 0 ]] && printf 'Skrip bersama sinkron.\n'
exit $beda
