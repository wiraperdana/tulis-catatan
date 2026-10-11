#!/usr/bin/env bash
# Pasang skill tulis-catatan dan buat-mindmap ke harness agent.
#
# Pemakaian:
#   ./install.sh                pasang ke semua harness yang terdeteksi (default)
#   ./install.sh --claude       hanya Claude Code, ke ~/.claude/skills
#   ./install.sh --agents       hanya lokasi universal ~/.agents/skills
#                               (Codex dan harness lain yang mengikuti standar Agent Skills)
#   ./install.sh --project      ke .claude/skills dan .agents/skills di direktori kerja saat ini
#   ./install.sh --dest <dir>   ke folder skill pilihan sendiri
#
# Tambahkan --link di akhir untuk memasang sebagai symlink ke repo ini, bukan
# salinan. Perubahan di repo langsung berlaku tanpa install ulang.
#   ./install.sh --link   atau   ./install.sh --agents --link
set -euo pipefail

AKAR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL=(tulis-catatan buat-mindmap)
VERSI_KATEX="0.16.29"
CACHE="${TULIS_CATATAN_CACHE:-$HOME/.cache/tulis-catatan}"

"$AKAR/tools/sinkron_skrip.sh" --cek >/dev/null || {
  printf 'Skrip bersama tidak sinkron. Jalankan tools/sinkron_skrip.sh lebih dulu.\n' >&2
  exit 1
}

MODE=salin
ARGS=()
for a in "$@"; do
  if [[ "$a" == "--link" ]]; then MODE=link; else ARGS+=("$a"); fi
done
set -- "${ARGS[@]+"${ARGS[@]}"}"

TUJUAN=()
case "${1:-}" in
  "")
    [[ -d "$HOME/.claude" ]] && TUJUAN+=("$HOME/.claude/skills")
    TUJUAN+=("$HOME/.agents/skills")
    ;;
  --claude) TUJUAN+=("$HOME/.claude/skills") ;;
  --agents) TUJUAN+=("$HOME/.agents/skills") ;;
  --project) TUJUAN+=("$(pwd)/.claude/skills" "$(pwd)/.agents/skills") ;;
  --dest)
    [[ -n "${2:-}" ]] || { printf 'Pemakaian: ./install.sh --dest <folder>\n' >&2; exit 2; }
    TUJUAN+=("$2")
    ;;
  *) sed -n '2,15p' "$0"; exit 2 ;;
esac

for t in "${TUJUAN[@]}"; do
  mkdir -p "$t"
  for s in "${SKILL[@]}"; do
    rm -rf "${t:?}/${s:?}"
    if [[ "$MODE" == link ]]; then
      ln -s "$AKAR/skills/$s" "$t/$s"
    else
      cp -R "$AKAR/skills/$s" "$t/"
    fi
  done
  printf 'Terpasang (%s) di %s: %s\n' "$MODE" "$t" "${SKILL[*]}"
done

# KaTeX dipakai tulis-catatan untuk memvalidasi rumus. Lewati bila npm tidak ada.
if command -v npm >/dev/null 2>&1; then
  if [[ ! -d "$CACHE/node_modules/katex" ]]; then
    printf 'Memasang KaTeX %s ke %s\n' "$VERSI_KATEX" "$CACHE"
    npm install --prefix "$CACHE" "katex@$VERSI_KATEX" --silent
  fi
else
  printf 'npm tidak ditemukan. Validasi rumus dilewati sampai Node.js terpasang.\n'
fi

printf '\nDi Claude Code: /tulis-catatan atau /buat-mindmap\n'
printf 'Di harness lain: sebut nama skill-nya, misalnya "pakai skill buat-mindmap untuk slide.pptx"\n'
