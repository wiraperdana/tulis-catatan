# Template mode `kajian`

Tujuan: jamaah yang tidak hadir bisa memahami isi kajian, dan setiap dalil yang disebut bisa dicek kebenaran teksnya.

Mode ini paling berisiko, karena salah mengutip ayat atau hadits adalah kesalahan serius. Ikuti empat aturan khusus di bawah sebelum menulis apa pun.

## Aturan khusus

1. **Ayat dan hadits tidak pernah dikutip dari ingatan model.** Setiap dalil yang disebut pemateri dicari lewat tool MCP Quran dan Hadits bila tersedia di sesi ini. Untuk Quran, baca aturan grounding-nya lebih dulu (`fetch_grounding_rules`), lalu pakai `search_quran`, `fetch_quran`, dan `fetch_translation`. Untuk hadits, pakai `search_hadith` dan `fetch_hadith`. Teks Arab, terjemah, dan tautan verifikasi diambil dari hasil tool.
2. **Pisahkan dua hal.** Tulis **apa yang dikatakan pemateri** tentang dalil itu, dan terpisah darinya **teks dalil hasil verifikasi**. Pemateri sering mengutip secara makna, dan itu wajar. Catatan menunjukkan keduanya tanpa menyalahkan pemateri.
3. **Dalil yang tidak ditemukan** atau tool yang tidak tersedia: tulis rujukan sebagaimana diucapkan pemateri, beri tanda `[belum terverifikasi]`, dan jangan mengisi teks Arab dari ingatan.
4. **Extra tip dibatasi** pada konteks bahasa Arab, sejarah, atau arti istilah. Extra tip tidak memuat hukum fikih, tarjih, atau pendapat yang tidak disampaikan pemateri.

Mesin transkripsi sangat lemah pada lafaz Arab. Lafaz yang tidak terbaca ditulis `[lafaz Arab tidak jelas di transkrip]` dan dicatat di bagian 9.

---

## 1. Ikhtisar Kajian

Satu baris berisi tema, pemateri, tanggal, tempat atau penyelenggara, dan kitab yang dikaji beserta bab atau halamannya bila disebut. Lalu ringkasan 3 sampai 5 kalimat dengan pesan utama di kalimat pertama.

## 2. Peta Kajian

Daftar pokok bahasan sesuai urutan, dengan timestamp. Beri nomor 4.1, 4.2, dan seterusnya agar cocok dengan bagian 4.

## 3. Dalil yang Dikutip

Beri nomor: Dalil 1, Dalil 2, dan seterusnya. Untuk setiap dalil:

1. **Rujukan:** nama surah dan nomor ayat, atau kitab hadits dan nomornya, sebagaimana hasil verifikasi.
2. **Teks dan terjemah:** dari hasil tool, dengan tautan verifikasi yang dikembalikan tool.
3. **Yang disampaikan pemateri:** kutipan atau parafrase dengan timestamp.
4. **Status:** `terverifikasi` atau `[belum terverifikasi]`. Bila redaksi pemateri berbeda bermakna dari teks terverifikasi, tulis `⚠️ Beda redaksi:` beserta perbedaannya.

## 4. Penjelasan Pemateri Langkah demi Langkah

Bagian terpanjang. Satu subbagian per pokok bahasan, bernomor sesuai bagian 2. Rekonstruksi alur penjelasan pemateri. Kisah, perumpamaan, dan contoh dimasukkan di dalam langkah yang diilustrasikannya. Rujuk dalil dengan "lihat Dalil n", tanpa menulis ulang teksnya.

## 5. Faedah dan Amalan

Hanya faedah, pelajaran, dan amalan yang **disampaikan pemateri**, dalam format `- [ ]` dengan timestamp. Jangan menambah amalan sendiri.

## 6. Tanya Jawab

Setiap pertanyaan dengan timestamp dan jawaban pemateri. Bila jawabannya merujuk dalil, rujuk nomor dalilnya di bagian 3, dan tambahkan dalil baru ke bagian 3 bila belum ada.

## 7. Istilah

Tabel: **Istilah (transliterasi) | Arti menurut pemateri | Sumber**. Bila pemateri tidak menjelaskan artinya, isi dengan arti bahasa singkat dan akhiri dengan `(💬 Extra tip)`.

## 8. Rujukan Kitab dan Ulama yang Disebut

Daftar kitab, ulama, dan rujukan lain yang disebut pemateri, sebagaimana diucapkan, dengan timestamp. Jangan melengkapi judul atau nama yang tidak jelas dengan tebakan.

## 9. Celah Transkrip

Lafaz Arab, nama, atau rujukan yang tidak jelas di transkrip, dengan timestamp, supaya bisa dicek ke rekaman.
