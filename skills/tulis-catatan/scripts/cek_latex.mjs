#!/usr/bin/env node
// Validasi semua notasi matematika di sebuah catatan Markdown dengan KaTeX.
//
// Tiap rumus $...$ dan $$...$$ di-render satu per satu. Rumus yang gagal
// dilaporkan dengan nomor barisnya. Kode di dalam ``` dan `...` dilewati.
//
// Selain error sintaks, skrip ini juga menolak tiga kebiasaan yang membuat
// rumus tampil rusak di editor Markdown:
//   1. simbol Unicode di dalam rumus, misalnya × atau ≤ (pakai \times, \le)
//   2. pembatas \( \) dan \[ \] yang tidak di-render Obsidian
//   3. $$ yang tidak punya pasangan penutup
//
// Pemakaian:
//   node cek_latex.mjs catatan.md
//
// KaTeX dicari di ~/.cache/tulis-catatan (atau $TULIS_CATATAN_CACHE). Kalau
// belum ada, skrip mencetak perintah pemasangannya lalu keluar dengan kode 2.

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";

const VERSI_KATEX = "0.16.29";
const folderCache =
  process.env.TULIS_CATATAN_CACHE || path.join(os.homedir(), ".cache", "tulis-catatan");

function muatKatex() {
  for (const dasar of [folderCache, process.cwd()]) {
    try {
      return createRequire(path.join(dasar, "noop.js"))("katex");
    } catch {
      // coba lokasi berikutnya
    }
  }
  return null;
}

const katex = muatKatex();
if (!katex) {
  console.error(
    `KaTeX belum terpasang. Pasang sekali dengan:\n` +
      `  npm install --prefix "${folderCache}" katex@${VERSI_KATEX}`
  );
  process.exit(2);
}

const berkas = process.argv[2];
if (!berkas) {
  console.error("Pemakaian: node cek_latex.mjs catatan.md");
  process.exit(2);
}

const baris = fs.readFileSync(berkas, "utf8").split("\n");

// Ganti isi kode dengan spasi sepanjang aslinya, supaya posisi kolom tetap.
function buangKode(teks) {
  return teks.replace(/`+[^`]*`+/g, (m) => " ".repeat(m.length));
}

const rumus = []; // { baris, isi, display }
const masalah = [];
let dalamKode = false;
let display = null; // { mulai, isi: [] }

baris.forEach((asli, i) => {
  const nomor = i + 1;
  if (/^\s*(```|~~~)/.test(asli)) {
    dalamKode = !dalamKode;
    return;
  }
  if (dalamKode) return;

  let teks = buangKode(asli);

  if (/\\\(|\\\[/.test(teks) && !/\\\\\[/.test(teks)) {
    masalah.push({ baris: nomor, pesan: "pembatas \\( atau \\[ dipakai, ganti dengan $ atau $$" });
  }

  // Tangani $$ (bisa lintas baris).
  let sisa = "";
  let pos = 0;
  while (pos < teks.length) {
    const idx = teks.indexOf("$$", pos);
    if (display) {
      if (idx === -1) {
        display.isi.push(teks.slice(pos));
        pos = teks.length;
      } else {
        display.isi.push(teks.slice(pos, idx));
        rumus.push({ baris: display.mulai, isi: display.isi.join("\n"), display: true });
        display = null;
        pos = idx + 2;
      }
    } else {
      if (idx === -1) {
        sisa += teks.slice(pos);
        pos = teks.length;
      } else {
        sisa += teks.slice(pos, idx);
        display = { mulai: nomor, isi: [] };
        pos = idx + 2;
      }
    }
  }

  // Rumus inline $...$ menurut aturan Pandoc: pembuka tidak diikuti spasi,
  // penutup tidak didahului spasi dan tidak diikuti angka.
  const polaInline = /(?<![\\$])\$(?![\s$])((?:\\\$|[^$\n])+?)(?<![\s\\])\$(?!\d)/g;
  let m;
  while ((m = polaInline.exec(sisa)) !== null) {
    rumus.push({ baris: nomor, isi: m[1], display: false });
  }
});

if (display) {
  masalah.push({ baris: display.mulai, pesan: "$$ dibuka tapi tidak pernah ditutup" });
}

for (const r of rumus) {
  const unicode = r.isi.match(/[^\x00-\x7F]/g);
  if (unicode) {
    masalah.push({
      baris: r.baris,
      pesan: `simbol Unicode di dalam rumus (${[...new Set(unicode)].join(" ")}), ganti dengan perintah LaTeX`,
    });
  }
  try {
    katex.renderToString(r.isi, {
      displayMode: r.display,
      throwOnError: true,
      strict: (kode) => (kode === "unicodeTextInMathMode" ? "error" : "ignore"),
    });
  } catch (e) {
    const pesan = String(e.message || e).replace(/^KaTeX parse error: /, "");
    const cuplikan = r.isi.trim().replace(/\s+/g, " ").slice(0, 70);
    masalah.push({ baris: r.baris, pesan: `${pesan}\n      rumus: ${cuplikan}` });
  }
}

masalah.sort((a, b) => a.baris - b.baris);
for (const x of masalah) console.log(`baris ${x.baris}: ${x.pesan}`);

const jumlahDisplay = rumus.filter((r) => r.display).length;
console.log(
  `\n${rumus.length} rumus diperiksa (${jumlahDisplay} display, ${rumus.length - jumlahDisplay} inline), ` +
    `${masalah.length} masalah.`
);
process.exit(masalah.length ? 1 : 0);
