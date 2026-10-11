#!/usr/bin/env bash
# Pasang skill tulis-catatan ke direktori skill Claude Code.
#
# Pemakaian:
#   ./install.sh              pasang global, ke ~/.claude/skills
#   ./install.sh --project    pasang ke .claude/skills di direktori kerja saat ini
set -euo pipefail

ASAL="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skills/tulis-catatan"
VERSI_KATEX="0.16.29"
CACHE="${TULIS_CATATAN_CACHE:-$HOME/.cache/tulis-catatan}"

if [[ "${1:-}" == "--project" ]]; then
  TUJUAN="$(pwd)/.claude/skills"
  RUANG="project ini"
else
  TUJUAN="$HOME/.claude/skills"
  RUANG="semua project (global)"
fi

mkdir -p "$TUJUAN"
if [[ -e "$TUJUAN/tulis-catatan" ]]; then
  printf 'Menimpa versi lama di %s\n' "$TUJUAN/tulis-catatan"
  rm -rf "${TUJUAN:?}/tulis-catatan"
fi
cp -R "$ASAL" "$TUJUAN/"
printf 'Terpasang: /tulis-catatan, untuk %s\n' "$RUANG"

# KaTeX dipakai untuk memvalidasi rumus. Lewati bila npm tidak ada.
if command -v npm >/dev/null 2>&1; then
  if [[ ! -d "$CACHE/node_modules/katex" ]]; then
    printf 'Memasang KaTeX %s ke %s\n' "$VERSI_KATEX" "$CACHE"
    npm install --prefix "$CACHE" "katex@$VERSI_KATEX" --silent
  fi
else
  printf 'npm tidak ditemukan. Validasi rumus dilewati sampai Node.js terpasang.\n'
fi

printf '\nCoba panggil: /tulis-catatan kuliah rekaman.vtt --mindmap\n'
