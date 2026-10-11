---
name: tulis-catatan
description: Ubah transkrip rekaman (kuliah, kajian Islam, rapat, brainstorming, bimbingan, wawancara, seminar, rapat klien) jadi catatan Markdown yang lengkap, bersumber, dan bertimestamp. Bisa menerima lampiran slide, materi, atau catatan sendiri, memvalidasi notasi matematika dengan KaTeX, dan menghasilkan mindmap .xmind yang terbaca saat dicetak A4. Pakai saat pengguna menyebut "tulis catatan", "catatan kuliah", "notulen", "MoM", "rangkum transkrip", atau memberi file .vtt, .srt, atau transkrip lain.
---

# /tulis-catatan

Skill ini mengubah transkrip jadi catatan yang bisa dipakai belajar atau bekerja tanpa membuka rekamannya lagi. **Transkrip** adalah teks hasil konversi suara rekaman jadi tulisan, biasanya disertai nama pembicara dan timestamp.

Prinsip utamanya satu: **pembaca harus selalu tahu dari mana setiap kalimat berasal.** Catatan yang berisi tebakan lebih berbahaya daripada catatan yang bolong, karena pembaca tidak bisa membedakan keduanya.

## Pemanggilan

```
/tulis-catatan <mode> <file-transkrip> [lampiran ...] [--mindmap] [--lang id|en] [--out <folder>]
```

| Mode | Untuk | Template |
|---|---|---|
| `kuliah` | Kuliah, kelas, pelatihan | `templates/kuliah.md` |
| `kajian` | Kajian Islam, ceramah, halaqah | `templates/kajian.md` |
| `mom` | Rapat internal, notulen | `templates/mom.md` |
| `brainstorming` | Sesi curah gagasan | `templates/brainstorming.md` |
| `bimbingan` | Sesi dengan pembimbing tesis, skripsi, atau hibah | `templates/bimbingan.md` |
| `wawancara` | Wawancara riset kualitatif atau wawancara pengguna | `templates/wawancara.md` |
| `seminar` | Webinar, kuliah tamu, talk konferensi | `templates/seminar.md` |
| `klien` | Rapat discovery atau progres dengan klien | `templates/klien.md` |

Semua path di bawah relatif terhadap **folder skill ini**, yaitu folder tempat `SKILL.md` ini berada. Setelah dipasang global, biasanya `~/.claude/skills/tulis-catatan/`.

## Langkah

### 0. Tentukan mode dan argumen

Kalau mode tidak disebut, baca 100 baris pertama transkrip, tebak modenya, lalu **tanya pengguna untuk konfirmasi** sebelum menulis. Jangan menebak diam-diam, karena template yang salah menghasilkan catatan yang salah bentuk dari awal sampai akhir.

Opsi default:

| Opsi | Default |
|---|---|
| `--lang` | `id`: Bahasa Indonesia, istilah teknis tetap dalam bentuk Inggrisnya |
| `--out` | Ditentukan otomatis oleh `scripts/lokasi_output.py`, lihat di bawah |
| `--mindmap` | Tidak dibuat |

**Folder output.** Bila `--out` tidak diberikan, jalankan:

```bash
python3 scripts/lokasi_output.py <transkrip>
```

Baris pertama keluarannya adalah folder output, baris kedua alasannya. Aturannya:

1. Transkrip di dalam workspace **Personal-OS** (ada `AGENTS.md` berfrontmatter `schema: personal-os/agents@1` di folder atasnya): tulis ke `_output/` milik Project terdekat, atau milik Entity terdekat bila tidak ada Project.
2. Di luar itu: tulis di folder yang sama dengan transkrip.

Sampaikan folder dan alasannya ke pengguna sebelum menulis, supaya ia bisa mengoreksi dengan `--out`. Buat folder `_output/` bila belum ada.

### 1. Rapikan transkrip

```bash
python3 scripts/rapikan_transkrip.py <transkrip> -o <folder-kerja>/transkrip_rapi.txt
```

Skrip menggabungkan potongan kalimat dari pembicara yang sama dan meringkas timestamp jadi `[hh:mm:ss]`. Ia menerima `.vtt`, `.srt`, `.txt`, `.md`, dan `.docx`. Simpan hasilnya di folder kerja sementara, bukan di samping transkrip.

Baca **seluruh** hasilnya. Untuk transkrip panjang, baca bertahap dengan `offset` dan `limit` sampai habis. Catatan yang ditulis dari separuh transkrip akan tampak lengkap padahal tidak.

Bila skrip melaporkan "tanpa timestamp", rujuk posisi dengan nomor paragraf `[¶12]` sebagai pengganti timestamp.

### 2. Baca lampiran

| Jenis | Cara membaca |
|---|---|
| PDF | Tool Read dengan parameter `pages`, maksimal 20 halaman per panggilan |
| PPTX | Ekstrak teks per slide, misalnya lewat skill `pptx` bila tersedia |
| DOCX | Skill `docx` bila tersedia, atau `rapikan_transkrip.py` untuk teks polos |
| Gambar (foto papan tulis, screenshot) | Tool Read langsung |
| URL | WebFetch |

Catat nomor slide atau halaman untuk setiap isi yang akan dikutip.

### 3. Susun daftar istilah dan koreksi transkrip

Sebelum menulis, buat daftar istilah teknis dari slide dan transkrip. Daftar ini sekaligus jadi kamus koreksi, karena mesin transkripsi sering salah mendengar istilah teknis. Contohnya "see sharp" yang sebenarnya "C#", atau "regresi lojistik" yang sebenarnya "logistic regression".

Istilah yang tidak bisa dipastikan ditulis apa adanya dengan tanda `[tidak jelas di transkrip]`.

### 4. Tulis catatan bagian per bagian

1. Baca template mode di `templates/<mode>.md`.
2. Tulis file `catatan_<nama-transkrip>.md` di folder output, berisi judul dan semua heading bagian dengan isi `(sedang ditulis)`.
3. Isi tiap bagian satu per satu dengan Edit. Jangan menulis seluruh catatan dalam satu panggilan Write, karena catatan sesi dua jam bisa melampaui batas satu jawaban dan terpotong di tengah.
4. Transkrip di atas sekitar dua jam diproses per topik. Selesaikan satu topik di bagian penjelasan sebelum membaca topik berikutnya.

### 5. Periksa sebelum diserahkan

- [ ] Tidak ada heading yang masih berisi `(sedang ditulis)`.
- [ ] Tidak ada konsep yang dijelaskan dua kali. Kalau ada, lebur ke satu tempat dan ganti yang lain dengan rujukan nomor.
- [ ] Setiap poin kunci punya label sumber.
- [ ] Setiap pengetahuan luar ada di dalam `💬 Extra tip:`.
- [ ] Tidak ada angka, nama, tanggal, atau rujukan yang tidak ada di sumber.

### 6. Validasi notasi matematika

Jalankan bila catatan memuat `$`:

```bash
node scripts/cek_latex.mjs <catatan.md>
```

Bila keluar dengan kode 2, KaTeX belum terpasang. Pasang sekali dengan perintah yang dicetak skrip, lalu ulangi. Perbaiki setiap masalah yang dilaporkan sampai hasilnya `0 masalah`.

### 7. Buat mindmap (bila `--mindmap`)

1. Susun outline JSON dari **catatan yang sudah jadi**, mengikuti aturan di bagian "Aturan mindmap". Catatan sudah melewati koreksi istilah, jadi mindmap tidak membawa ulang kesalahan transkrip.
2. Simpan outline di folder kerja sementara, lalu jalankan:

```bash
python3 scripts/mindmap_xmind.py buat <outline.json> -o <folder-output>/mindmap_<nama-transkrip>.xmind
```

3. Bila skrip melaporkan error, rapikan outline lalu jalankan ulang. Jangan memakai `--paksa` kecuali pengguna memintanya.

### 8. Laporkan

Sampaikan secara singkat:

1. Lokasi file catatan dan mindmap.
2. Jumlah rumus yang divalidasi, dan rumus yang berlabel rekonstruksi.
3. Untuk mode `kajian`: dalil yang terverifikasi dan yang belum.
4. Isi slide yang tidak dibahas, dan celah transkrip yang perlu dicek pengguna.

## Aturan inti (berlaku di semua mode)

1. **Label sumber.** Setiap poin kunci membawa label sumbernya:

   | Label | Sumber |
   |---|---|
   | `[00:12:30]` | Transkrip, pada waktu itu |
   | `[¶12]` | Transkrip tanpa timestamp, paragraf ke-12 |
   | `[Slide 14]` | Slide atau materi presentasi |
   | `[Catatan pengguna]` | Catatan yang ditulis pengguna sendiri |
   | `[Bacaan: nama-file, hlm. 5]` | Bacaan atau handout |

2. **Pengetahuan luar hanya di `💬 Extra tip:`.** Penjelasan dari pengetahuan umum model wajib berada di baris atau blok yang diawali `💬 Extra tip:`. Template tiap mode menentukan apakah Extra tip boleh dipakai.
3. **Jangan mengarang.** Rumus, angka, nama, tanggal, tenggat, rujukan, DOI, dan isi ujian hanya ditulis bila ada di sumber. Bila tidak jelas, tulis `[tidak jelas di transkrip]`.
4. **Koreksi salah transkrip secara terbuka.** Tulis istilah yang benar, lalu `(transkrip: "kata aslinya")`.
5. **Bahasa.** Default Bahasa Indonesia. Istilah teknis memakai bentuk yang paling umum dipakai praktisi, biasanya Inggris, dan didefinisikan pada pemakaian pertama. Kutipan langsung tetap dalam bahasa aslinya. Dengan `--lang en`, seluruh catatan termasuk heading ditulis dalam Bahasa Inggris.
6. **Katakan sekali saja.** Sebuah konsep didefinisikan di satu tempat dan dijelaskan di satu tempat. Bagian lain merujuknya dengan nomor, misalnya "lihat 5.2" atau "lihat Rumus 3".
7. **Bagian kosong tetap ditulis.** Isi dengan `Tidak dibahas di sesi ini.` supaya pembaca tahu bagian itu sudah diperiksa.
8. **Tanpa em dash.** Pakai koma, titik, atau titik dua.
9. **Privasi.** Catatan dan transkrip tidak diunggah ke layanan mana pun. Data pribadi pihak ketiga yang tidak relevan dengan isi sesi, seperti nomor telepon atau alamat, tidak ditulis.

## Aturan menggabungkan transkrip dan lampiran

Transkrip mencatat **apa yang diucapkan**, slide mencatat **apa yang ditulis**. Keduanya sah, dan pembaca harus tahu kalimat mana berasal dari yang mana.

1. **Untuk rumus dan ejaan istilah, slide lebih dipercaya.** Rumus yang diucapkan lisan paling rawan salah transkrip.
2. **Untuk penekanan, contoh, dan tanya jawab, transkrip lebih dipercaya.** Slide tidak tahu bagian mana yang ditekankan pembicara.
3. **Bila keduanya bertentangan, tampilkan keduanya** dengan tanda `⚠️ Beda sumber:`, lalu jangan memilih sendiri.
4. **Isi slide yang tidak dibahas** dikumpulkan di bagian tersendiri bila template menyediakannya, supaya pembaca tahu materi mana yang harus dipelajari sendiri.

## Aturan notasi matematika

Target render adalah editor Markdown yang memakai KaTeX atau MathJax, misalnya Obsidian, VS Code, Typora, dan GitHub.

1. Inline memakai `$...$`, tanpa spasi tepat setelah `$` pembuka atau sebelum `$` penutup.
2. Display memakai `$$` di baris sendiri, rumus di baris berikutnya, lalu `$$` penutup di baris sendiri.
3. Pakai perintah LaTeX standar: `\frac`, `\sum`, `\prod`, `\int`, `\sqrt`, `\mathbf`, `\hat`, `\bar`, `\le`, `\ge`, `\ne`, `\times`, `\cdot`, `\in`, `\rightarrow`. Kata di dalam rumus ditulis dengan `\text{...}`.
4. Rumus bertingkat memakai `\begin{aligned} ... \end{aligned}` di dalam `$$`.
5. **Tanpa simbol Unicode di dalam rumus.** Tulis `\times`, `\le`, `\alpha`, dan seterusnya.
6. **Tanpa pembatas `\(` dan `\[`.** Banyak editor Markdown tidak me-render keduanya.
7. Setiap rumus display diikuti daftar arti simbolnya.
8. Rumus dari slide diberi label `[Slide n]`. Rumus yang hanya diucapkan diberi tanda `(rekonstruksi dari ucapan, cek dengan slide)`.
9. Simbol mata uang ditulis `Rp` atau `USD`, supaya `$` hanya dipakai untuk matematika.

## Aturan mindmap

Mindmap yang semua cabangnya dibuka harus tetap terbaca saat dicetak di satu lembar A4 landscape. Kalau hanya ada cabang utama, mindmap itu tidak berguna. Kalau setiap detail ikut digambar, hurufnya mengecil sampai tidak terbaca. Skrip `mindmap_xmind.py` menegakkan aturan ini:

| Aturan | Nilai |
|---|---|
| Kedalaman | Setiap cabang utama mencapai level 3. Level 4 boleh, maksimal 15% dari semua node. Level 5 dilarang. |
| Cabang utama (level 1) | 4 sampai 7 |
| Anak per node | Maksimal 5 |
| Total node di luar akar | Maksimal 70. Di bawah 40 hanya peringatan |
| Panjang label | Level 1 dan 2 maksimal 5 kata. Level 3 dan 4 maksimal 10 kata |
| Rumus | Tulis nama rumusnya saja, tanpa LaTeX |

Format outline:

```json
{"title": "Judul sesi",
 "children": [
   {"title": "Cabang utama", "children": [
     {"title": "Sub-cabang", "children": [
       {"title": "Detail singkat"}
     ]}
   ]}
 ]}
```

Panduan isi:

1. **Akar** adalah judul sesi, maksimal 8 kata.
2. **Level 1** mengikuti pembagian terbesar catatan, misalnya topik di Peta Kuliah atau agenda rapat.
3. **Level 2** berisi konsep atau poin di dalam topik itu.
4. **Level 3** berisi detail yang paling perlu diingat: definisi singkat, contoh, atau keputusan.
5. Tulis label sebagai frasa padat, bukan kalimat. Tanpa nomor slide dan timestamp, karena keduanya ada di catatan.
