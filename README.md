# tulis-catatan dan buat-mindmap

Dua skill agent untuk Claude Code, Codex, dan harness lain yang mengikuti standar Agent Skills.

| Skill | Mengubah | Menjadi |
|---|---|---|
| `tulis-catatan` | Transkrip rekaman, plus slide atau materi sebagai lampiran | Catatan Markdown yang lengkap, bersumber, dan bertimestamp, dengan rumus tervalidasi. Opsional: mindmap `.xmind` |
| `buat-mindmap` | Dokumen apa pun yang isinya bisa dibaca: Markdown, DOCX, PPTX, PDF, XLSX, HTML, foto | Mindmap `.xmind` yang tetap terbaca saat semua cabang dibuka dan dicetak di A4 |

```
/tulis-catatan kuliah rekaman.vtt slide-minggu6.pdf --mindmap
/buat-mindmap slide-minggu6.pptx catatan-saya.md
```

## Kenapa ini ada

Fitur catatan otomatis di aplikasi rapat punya dua masalah. Panjang outputnya dibatasi, sehingga catatan kuliah dua jam terpotong di tengah. Selain itu, ia mencampur isi rekaman dengan pengetahuan umum model tanpa tanda, sehingga pembaca tidak tahu kalimat mana yang benar-benar diucapkan.

Skill ini menulis catatan bagian per bagian langsung ke file, jadi panjangnya tidak dibatasi satu kali jawaban. Setiap poin kunci membawa label sumbernya, misalnya `[00:12:30]` untuk transkrip dan `[Slide 14]` untuk slide. Penjelasan dari luar rekaman selalu ditandai `💬 Extra tip:`.

## Delapan mode

| Mode | Untuk | Yang khas |
|---|---|---|
| `kuliah` | Kuliah, kelas, pelatihan | Sinyal ujian hanya yang diucapkan dosen, rumus tervalidasi, isi slide yang tidak dibahas |
| `kajian` | Kajian Islam, ceramah | Ayat dan hadits diverifikasi lewat MCP Quran dan Hadits, tidak pernah dari ingatan model |
| `mom` | Rapat, notulen | Keputusan dan action item dengan PIC dan tenggat |
| `brainstorming` | Curah gagasan | Semua ide tercatat, termasuk yang ditolak beserta alasannya |
| `bimbingan` | Bimbingan tesis atau hibah | Masukan dipetakan ke bagian naskah |
| `wawancara` | Wawancara riset atau pengguna | Kutipan verbatim dan anonimisasi |
| `seminar` | Webinar, kuliah tamu | Klaim, angka, dan rujukan dipisah untuk diverifikasi |
| `klien` | Rapat discovery atau progres klien | Kebutuhan dengan kata-kata klien, sinyal risiko proyek |

Setiap mode punya template di `skills/tulis-catatan/templates/`. Menambah mode cukup dengan menambah satu file template, lalu mendaftarkannya di tabel `SKILL.md`.

## Pemasangan

```bash
git clone https://github.com/wiraperdana/tulis-catatan.git
cd tulis-catatan
./install.sh
```

Tanpa opsi, kedua skill dipasang ke semua lokasi yang relevan:

| Opsi | Lokasi | Untuk |
|---|---|---|
| (tanpa opsi) | `~/.claude/skills` bila ada, dan `~/.agents/skills` | Semua harness yang terdeteksi |
| `--claude` | `~/.claude/skills` | Claude Code |
| `--agents` | `~/.agents/skills` | Codex dan harness lain yang membaca lokasi universal Agent Skills |
| `--project` | `.claude/skills` dan `.agents/skills` di folder kerja | Satu project saja |
| `--dest <folder>` | Folder pilihan sendiri | Harness dengan lokasi skill lain |
| `--link` | Ditambahkan ke opsi mana pun | Pasang sebagai symlink ke repo ini, jadi `git pull` langsung berlaku tanpa install ulang |

### Memanggil di tiap harness

| Harness | Cara memanggil |
|---|---|
| Claude Code | Ketik `/tulis-catatan` atau `/buat-mindmap` |
| Codex | Sebut nama skill-nya, misalnya "pakai skill buat-mindmap untuk slide.pptx" |
| Harness lain | Sama seperti Codex. Bila harness tidak menemukan skill otomatis, minta ia membaca `SKILL.md` di folder skill lalu menjalankannya |

Skill ini hanya berisi instruksi Markdown dan skrip Python atau Node. Tidak ada yang bergantung pada tool khusus satu harness. Format yang tidak bisa dibaca harness diekstrak lewat `ekstrak_teks.py`.

Kebutuhan:

| Komponen | Untuk | Wajib? |
|---|---|---|
| Python 3.9+ | Merapikan transkrip, ekstraksi dokumen, dan membuat mindmap | Ya |
| Node.js dan npm | Validasi rumus dengan KaTeX | Hanya bila catatan memuat matematika |
| MCP Quran dan Hadits | Verifikasi dalil di mode `kajian` | Tidak. Tanpanya, dalil diberi tanda `[belum terverifikasi]` |
| `pdftotext` (poppler) atau `pypdf` | Ekstraksi PDF | Hanya bila harness tidak bisa membaca PDF sendiri |
| Xmind | Membuka mindmap | Hanya untuk mindmap |

`install.sh` juga memasang KaTeX ke `~/.cache/tulis-catatan` bila npm tersedia.

## Pemakaian `tulis-catatan`

```
/tulis-catatan <mode> <file-transkrip> [lampiran ...] [--mindmap] [--lang id|en] [--out <folder>]
```

| Argumen | Keterangan |
|---|---|
| `<file-transkrip>` | `.vtt`, `.srt`, `.txt`, `.md`, atau `.docx`. Transkrip Zoom (`.vtt`) memberi hasil terbaik karena membawa timestamp dan nama pembicara |
| `[lampiran ...]` | Slide (`.pdf`, `.pptx`), handout, catatan sendiri, foto papan tulis, atau URL |
| `--mindmap` | Buat juga `mindmap_<nama>.xmind` |
| `--lang` | `id` (default): Bahasa Indonesia dengan istilah teknis Inggris. `en`: Bahasa Inggris |
| `--out` | Folder output. Default: lihat "Lokasi output" di bawah |

Bila mode tidak disebut, skill menebak dari isi transkrip lalu meminta konfirmasi.

### Lokasi output

Tanpa `--out`, catatan ditulis di folder yang sama dengan transkrip.

Pengecualiannya untuk workspace **Personal-OS**, yaitu folder yang punya `AGENTS.md` berfrontmatter `schema: personal-os/agents@1`. Di sana catatan masuk ke `_output/` milik Project terdekat, atau milik Entity terdekat bila tidak ada Project. Skill selalu menyebut folder tujuannya sebelum menulis.

## Pemakaian `buat-mindmap`

```
/buat-mindmap <file> [file lain ...] [--judul "<judul>"] [--fokus "<bagian>"] [--lang id|en] [--out <folder>]
```

| Argumen | Keterangan |
|---|---|
| `<file>` | `.md`, `.txt`, `.docx`, `.pptx`, `.xlsx`, `.pdf`, `.html`, `.odt`, `.odp`, gambar, atau URL. Beberapa file digabung jadi satu mindmap |
| `--judul` | Teks node pusat. Default: judul dokumen pertama |
| `--fokus` | Batasi ke satu bab, topik, atau rentang slide. Berguna untuk dokumen tebal yang tidak muat dalam 70 node |
| `--lang`, `--out` | Sama seperti `tulis-catatan` |

Skill menyusun struktur dari isi dokumen, memakai istilah dokumen apa adanya, lalu melaporkan bagian yang tidak masuk karena batas node dan isi yang tidak terbaca, misalnya slide yang hanya berisi gambar.

## Notasi matematika

Rumus ditulis dengan `$...$` dan `$$...$$`, lalu setiap rumus di-render dengan [KaTeX](https://katex.org) untuk memastikan tidak ada yang rusak. Skrip validasi juga menolak simbol Unicode di dalam rumus dan pembatas `\(` atau `\[`, karena keduanya sering tampil rusak di editor Markdown. Catatan bisa dibaca di Obsidian, VS Code, Typora, atau GitHub.

Validasi ini memastikan rumus **bisa di-render**. Kebenaran isinya bergantung pada sumber, jadi rumus yang hanya diucapkan dosen diberi tanda `(rekonstruksi dari ucapan, cek dengan slide)`.

## Mindmap untuk A4

Mindmap yang semua cabangnya dibuka harus tetap terbaca di satu lembar A4 landscape. Skrip `mindmap_xmind.py` menolak outline yang melanggar aturan ini:

| Aturan | Nilai |
|---|---|
| Kedalaman | Setiap cabang utama mencapai level 3. Level 4 maksimal 15% node |
| Cabang utama | 4 sampai 7 |
| Anak per node | Maksimal 5 |
| Total node | Maksimal 70 |
| Panjang label | 5 kata di level 1 dan 2, 10 kata di level 3 dan 4 |

Batas ini titik awal dan belum dikalibrasi dengan cetak uji. Bila hasil cetak Anda terlalu padat atau terlalu longgar, ubah konstanta di bagian atas `skills/tulis-catatan/scripts/mindmap_xmind.py`, lalu jalankan `tools/sinkron_skrip.sh`.

## Tanpa agent: template Zoom Notes

Folder `zoom/` berisi template instruksi untuk fitur catatan AI di Zoom. Template itu dirancang supaya selesai sampai bagian terakhir walaupun panjang output Zoom dibatasi: setiap bagian diberi batas kata sendiri, dan totalnya sekitar 2.300 kata.

## Struktur repo

```
skills/tulis-catatan/
├── SKILL.md                     prosedur dan aturan inti
├── templates/<mode>.md          satu template per mode
└── scripts/
    ├── rapikan_transkrip.py     vtt, srt, txt, docx jadi transkrip ringkas
    ├── cek_latex.mjs            validasi rumus dengan KaTeX
    ├── mindmap_xmind.py         cek bentuk outline dan tulis .xmind   (bersama)
    ├── lokasi_output.py         tentukan folder output                (bersama)
    └── ekstrak_teks.py          docx, pptx, xlsx, pdf jadi teks       (bersama)
skills/buat-mindmap/
├── SKILL.md
└── scripts/                     salinan tiga skrip bersama
tools/sinkron_skrip.sh           salin dan periksa skrip bersama
zoom/instruction_lecture-note_zoom.md
install.sh
```

Setiap skill membawa salinan skrip bersamanya sendiri, supaya tetap jalan bila dipasang terpisah. Sumber kebenarannya `skills/tulis-catatan/scripts/`. Setelah mengubah skrip bersama, jalankan `tools/sinkron_skrip.sh`. `install.sh` menolak berjalan bila salinannya berbeda.

## Lisensi

MIT. Lihat `LICENSE`.
