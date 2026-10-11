# tulis-catatan

Skill untuk Claude Code yang mengubah transkrip rekaman jadi catatan Markdown yang lengkap, bersumber, dan bertimestamp. Ia bisa menerima slide atau materi sebagai lampiran, memvalidasi notasi matematika, dan menghasilkan mindmap `.xmind` yang tetap terbaca saat dicetak di kertas A4.

```
/tulis-catatan kuliah rekaman.vtt slide-minggu6.pdf --mindmap
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
./install.sh              # pasang global, ke ~/.claude/skills
./install.sh --project    # atau pasang ke .claude/skills di project saat ini
```

Kebutuhan:

| Komponen | Untuk | Wajib? |
|---|---|---|
| Python 3.9+ | Merapikan transkrip dan membuat mindmap | Ya |
| Node.js dan npm | Validasi rumus dengan KaTeX | Hanya bila catatan memuat matematika |
| MCP Quran dan Hadits | Verifikasi dalil di mode `kajian` | Tidak. Tanpanya, dalil diberi tanda `[belum terverifikasi]` |
| Xmind | Membuka mindmap | Hanya bila memakai `--mindmap` |

`install.sh` juga memasang KaTeX ke `~/.cache/tulis-catatan` bila npm tersedia.

## Pemakaian

```
/tulis-catatan <mode> <file-transkrip> [lampiran ...] [--mindmap] [--lang id|en] [--out <folder>]
```

| Argumen | Keterangan |
|---|---|
| `<file-transkrip>` | `.vtt`, `.srt`, `.txt`, `.md`, atau `.docx`. Transkrip Zoom (`.vtt`) memberi hasil terbaik karena membawa timestamp dan nama pembicara |
| `[lampiran ...]` | Slide (`.pdf`, `.pptx`), handout, catatan sendiri, foto papan tulis, atau URL |
| `--mindmap` | Buat juga `mindmap_<nama>.xmind` |
| `--lang` | `id` (default): Bahasa Indonesia dengan istilah teknis Inggris. `en`: Bahasa Inggris |
| `--out` | Folder output. Default: folder yang sama dengan transkrip |

Bila mode tidak disebut, skill menebak dari isi transkrip lalu meminta konfirmasi.

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

Batas ini titik awal dan belum dikalibrasi dengan cetak uji. Bila hasil cetak Anda terlalu padat atau terlalu longgar, ubah konstanta di bagian atas `mindmap_xmind.py`.

## Tanpa Claude Code: template Zoom Notes

Folder `zoom/` berisi template instruksi untuk fitur catatan AI di Zoom. Template itu dirancang supaya selesai sampai bagian terakhir walaupun panjang output Zoom dibatasi: setiap bagian diberi batas kata sendiri, dan totalnya sekitar 2.300 kata.

## Struktur repo

```
skills/tulis-catatan/
├── SKILL.md                     prosedur dan aturan inti
├── templates/<mode>.md          satu template per mode
└── scripts/
    ├── rapikan_transkrip.py     vtt, srt, txt, docx jadi transkrip ringkas
    ├── cek_latex.mjs            validasi rumus dengan KaTeX
    └── mindmap_xmind.py         cek bentuk outline dan tulis .xmind
zoom/instruction_lecture-note_zoom.md
install.sh
```

## Lisensi

MIT. Lihat `LICENSE`.
