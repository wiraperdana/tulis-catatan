---
name: buat-mindmap
description: Buat mindmap .xmind dari dokumen apa pun yang isinya bisa dibaca, misalnya catatan Markdown, slide PPTX atau PDF, dokumen DOCX, spreadsheet XLSX, halaman web, atau foto papan tulis. Mindmap dijaga tetap terbaca saat semua cabang dibuka dan dicetak di A4, dengan minimal 3 level dan maksimal 70 node. Pakai saat pengguna meminta "buat mindmap", "mind map", "peta konsep", atau "xmind" dari materi yang sudah ada. Untuk transkrip rekaman, pakai tulis-catatan dengan opsi --mindmap.
---

# buat-mindmap

Skill ini mengubah satu atau beberapa dokumen jadi satu mindmap `.xmind`. **Mindmap** adalah diagram bercabang yang menaruh topik utama di tengah, lalu memecahnya jadi subtopik dan detail.

Prinsip utamanya: **mindmap yang semua cabangnya dibuka harus tetap terbaca di satu lembar A4 landscape.** Analoginya peta jalan satu lembar. Kalau hanya ada jalan utama, peta itu tidak berguna. Kalau setiap gang ikut digambar, hurufnya mengecil sampai tidak terbaca. Skrip `mindmap_xmind.py` menegakkan titik tengahnya.

Semua path di bawah relatif terhadap **folder skill ini**, yaitu folder tempat `SKILL.md` ini berada.

## Pemanggilan

```
buat-mindmap <file> [file lain ...] [--judul "<judul>"] [--fokus "<bagian>"] [--lang id|en] [--out <folder>]
```

Di Claude Code, ketik `/buat-mindmap`. Di harness lain, sebut nama skill-nya dalam kalimat, misalnya "pakai skill buat-mindmap untuk slide-minggu6.pptx".

| Opsi | Default | Keterangan |
|---|---|---|
| `--judul` | Judul dokumen pertama | Teks di node pusat, maksimal 8 kata |
| `--fokus` | Seluruh isi | Batasi ke satu bab, topik, atau rentang slide. Berguna untuk dokumen tebal |
| `--lang` | `id` | `id`: Bahasa Indonesia dengan istilah teknis Inggris. `en`: Bahasa Inggris |
| `--out` | Lihat langkah 1 | Folder tujuan file `.xmind` |

## Langkah

### 1. Tentukan folder output

Bila `--out` tidak diberikan, jalankan pada file pertama:

```bash
python3 scripts/lokasi_output.py <file-pertama>
```

Baris pertama keluarannya adalah folder output, baris kedua alasannya. Di dalam workspace Personal-OS, hasilnya `_output/` milik Project atau Entity terdekat. Di luar itu, folder yang sama dengan file sumber. Sampaikan folder ini ke pengguna, lalu buat foldernya bila belum ada.

Nama file: `mindmap_<nama-file-pertama-tanpa-akhiran>.xmind`.

### 2. Baca semua sumber sampai habis

Utamakan kemampuan baca bawaan harness. Bila harness tidak bisa membaca suatu format, pakai skrip ekstraksi:

```bash
python3 scripts/ekstrak_teks.py <file> -o <folder-kerja>/<nama>.txt
```

| Format | Cara |
|---|---|
| `.md`, `.txt`, `.csv` | Baca langsung |
| `.docx`, `.pptx`, `.xlsx`, `.odt`, `.odp`, `.html` | `ekstrak_teks.py`, tanpa dependensi tambahan |
| `.pdf` | Baca PDF bawaan harness, atau `ekstrak_teks.py` bila `pdftotext` atau `pypdf` tersedia |
| Gambar | Kemampuan visual harness |
| `.doc`, `.ppt`, `.xls` lama | Minta pengguna menyimpan ulang sebagai format baru |
| URL | Kemampuan baca web harness |

Simpan hasil ekstraksi di folder kerja sementara, bukan di samping sumber. Baca **seluruh** isinya, bertahap bila panjang. Mindmap yang disusun dari separuh dokumen tampak lengkap padahal tidak.

**Isi berbentuk gambar wajib dibaca, bukan sekadar dilaporkan.** Slide yang hanya berisi gambar, diagram, halaman PDF hasil scan, dan gambar di dalam dokumen sering memuat materi inti, misalnya kerangka konsep atau tabel perbandingan.

1. Untuk setiap `.pptx`, `.docx`, dan `.pdf`, jalankan ekstraksi dengan ekspor gambar, walaupun harness bisa membaca format itu sendiri. Pembaca bawaan harness sering melewati gambar tanpa memberi tahu.
   ```bash
   python3 scripts/ekstrak_teks.py <file> -o <folder-kerja>/<nama>.txt --gambar <folder-kerja>/gambar
   ```
   Skrip memberi penanda `[TANPA TEKS: ...]` untuk slide atau halaman yang isinya gambar, dan `[BERGAMBAR: ...]` untuk slide yang punya teks sekaligus gambar. Logo dan teks header yang berulang di banyak slide disaring otomatis.
2. **Lihat setiap gambar yang ditandai dengan kemampuan visual harness**, lalu tulis ulang isinya: teks, alur diagram, hierarki, dan isi tabel. Cara ini lebih baik daripada OCR, karena struktur diagram ikut terbaca. Perkecil gambar lebih dulu bila harness membatasi ukurannya. Ilustrasi dekoratif yang tidak membawa informasi, misalnya gambar orang atau ikon hiasan, cukup dilewati tanpa dicatat.
3. **Bila harness tidak punya kemampuan visual**, ulangi ekstraksi dengan `--ocr`. OCR memakai `tesseract` dan hanya membaca teks, sehingga struktur diagram hilang. Tanpa paket bahasa Indonesia (`ind`), hasil OCR teks Indonesia sering keliru, jadi periksa kewajarannya.
4. Beri label sumber yang menyebut asalnya: `[Slide 6, gambar]` untuk hasil membaca visual, `[Slide 6, OCR]` untuk hasil OCR.
5. Gambar yang tetap tidak terbaca dicantumkan di laporan akhir.

### 3. Temukan struktur

1. **Pakai struktur sumber bila sudah baik.** Heading dokumen, judul bagian slide, atau bab buku biasanya jadi cabang utama yang wajar.
2. **Susun ulang bila strukturnya datar atau berantakan.** Contohnya 40 slide tanpa pembagian bagian, atau catatan acak. Kelompokkan isi menurut konsep, bukan menurut urutan halaman.
3. **Untuk beberapa file sekaligus**, gabungkan ke satu struktur menurut topik. Bila file-filenya tidak berhubungan, tanya pengguna apakah ingin satu mindmap per file.
4. **Untuk dokumen tebal**, batas 70 node berarti tidak semua detail masuk. Pilih yang paling penting, lalu sarankan `--fokus` untuk bagian yang perlu didalami.

### 4. Tulis outline JSON

Format:

```json
{"title": "Judul",
 "children": [
   {"title": "Cabang utama", "children": [
     {"title": "Sub-cabang", "children": [
       {"title": "Detail singkat"}
     ]}
   ]}
 ]}
```

Aturan bentuk, ditegakkan skrip:

| Aturan | Nilai |
|---|---|
| Kedalaman | Setiap cabang utama mencapai level 3. Level 4 boleh, maksimal 15% node. Level 5 dilarang |
| Cabang utama (level 1) | 4 sampai 7 |
| Anak per node | Maksimal 5 |
| Total node di luar pusat | Maksimal 70. Di bawah 40 hanya peringatan |
| Panjang label | Level 1 dan 2 maksimal 5 kata. Level 3 dan 4 maksimal 10 kata |
| Rumus | Nama rumusnya saja, tanpa LaTeX |

Aturan isi:

1. **Setiap label bersumber dari dokumen.** Jangan menambah konsep yang tidak ada di sumber.
2. **Pakai istilah dokumen apa adanya.** Jangan mengganti istilah sumber dengan sinonim, karena mindmap dipakai berdampingan dengan dokumennya.
3. **Label adalah frasa padat, bukan kalimat.** Tanpa nomor halaman atau slide.
4. **Level 3 berisi yang paling perlu diingat:** definisi singkat, contoh, angka kunci, atau perbedaan antarkonsep.
5. **Bila melebihi 70 node**, gabungkan daftar pendek ke satu label lebih dulu, misalnya tiga leaf "Produk", "Teknologi", "Harga" jadi satu leaf "Produk, teknologi, dan harga". Baru setelah itu buang detail yang paling tidak penting, dan catat apa yang dibuang untuk laporan.

Simpan outline di folder kerja sementara.

### 5. Periksa dan tulis

```bash
python3 scripts/mindmap_xmind.py buat <outline.json> -o <folder-output>/mindmap_<nama>.xmind
```

Bila skrip melaporkan error, rapikan outline lalu jalankan ulang sampai `Lolos.`. Peringatan boleh dibiarkan bila alasannya jelas, misalnya dokumen sumbernya memang pendek. Jangan memakai `--paksa` kecuali pengguna memintanya.

### 6. Laporkan

1. Lokasi file `.xmind` dan jumlah node per level.
2. Bagian sumber yang tidak masuk karena batas node, supaya pengguna bisa meminta mindmap terpisah dengan `--fokus`.
3. Gambar yang sudah dibaca dan masuk mindmap, serta gambar yang tetap tidak terbaca.

Ingatkan bahwa file bisa dibuka di Xmind, lalu dicetak dengan semua cabang terbuka di A4 landscape.

## Larangan

1. **Tanpa em dash** di label.
2. **Jangan membuka aplikasi Xmind** atau aplikasi lain milik pengguna. Bila Xmind sedang membuka dokumen yang belum disimpan, membuka file baru bisa memunculkan dialog yang berisiko menghapus pekerjaan pengguna. Biarkan pengguna membukanya sendiri.
