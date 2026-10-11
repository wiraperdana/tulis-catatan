# Template mode `kuliah`

Tujuan: mahasiswa yang tidak hadir bisa mempelajari semua yang diajarkan dari catatan ini saja.

**Extra tip:** boleh, hanya di bagian 8 dan untuk istilah yang tidak didefinisikan dosen di bagian 4.

**Pembagian kerja antarbagian.** Istilah didefinisikan di bagian 4. Penjelasan ada di bagian 5. Rumus ditulis di bagian 6. Bagian lain merujuk nomornya dan tidak mengulang penjelasan.

---

## 1. Ikhtisar Sesi

Satu baris berisi mata kuliah, topik, tanggal, dosen, dan durasi bila diketahui. Lalu ringkasan 4 sampai 6 kalimat yang menyampaikan pesan utama sesi lebih dulu. Tutup dengan 3 sampai 5 poin terpenting.

## 2. Sinyal Ujian, Tugas, dan Pengumuman

Hanya yang **diucapkan dosen secara eksplisit**. Jangan menyimpulkan sendiri materi apa yang mungkin keluar.

1. Setiap penyebutan ujian, kuis, atau tingkat kepentingan ("ini penting", "ini keluar", "ingat ini", "perhatikan"), dikutip singkat dengan timestamp, dalam format `- [ ]`. Tambahkan poin yang diulang dosen lebih dari sekali.
2. Tugas, tenggat, bacaan wajib, dan perubahan jadwal. Salin tanggal, jam, dan cara pengumpulan persis seperti diucapkan.

Bila tidak ada, tulis `Tidak ada yang disebutkan.`

## 3. Peta Kuliah

Daftar topik sesuai urutan pembahasan, satu baris per topik dengan timestamp mulai. Maksimal dua tingkat. Beri nomor 5.1, 5.2, dan seterusnya agar cocok dengan bagian 5. Tandai topik yang menurut dosen akan dilanjutkan di sesi berikutnya.

## 4. Istilah Kunci

Tabel tiga kolom: **Istilah | Definisi satu baris menurut dosen | Sumber**. Urut abjad. Definisi saja, tanpa penjelasan. Bila dosen tidak mendefinisikannya, tulis definisi singkat dan akhiri dengan `(💬 Extra tip)`.

## 5. Penjelasan Dosen Langkah demi Langkah

Bagian terpanjang. Satu subbagian per topik, bernomor sesuai bagian 3.

1. Rekonstruksi alur penalaran dosen sesuai urutan dan logikanya, sebagai langkah bernomor atau paragraf pendek.
2. Pertahankan setiap detail, syarat, pengecualian, dan peringatan yang disebut dosen.
3. Masukkan contoh, studi kasus, dan analogi **di dalam langkah yang diilustrasikannya**, lengkap dengan angka dan detailnya.
4. Isi slide yang relevan diintegrasikan dengan label `[Slide n]`.
5. Jangan mendefinisikan ulang istilah dari bagian 4. Rujuk rumus dengan "lihat Rumus n".

## 6. Rumus, Algoritma, dan Kode

Beri nomor: Rumus 1, Rumus 2, dan seterusnya. Untuk setiap item:

1. Tulis sekali dalam LaTeX display atau blok kode.
2. Jelaskan arti setiap simbol atau variabel.
3. Satu atau dua kalimat tentang kapan dan mengapa dipakai, menurut dosen.
4. Label sumber: `[Slide n]`, atau `(rekonstruksi dari ucapan, cek dengan slide)`.

## 7. Tanya Jawab Kelas

Setiap pertanyaan dengan timestamp, siapa yang bertanya (mahasiswa atau dosen), dan jawabannya. Bila jawabannya sudah tercakup di bagian 5, tulis satu baris dan "lihat 5.x". Tandai pertanyaan yang tidak terjawab atau ditunda.

## 8. Bagian Sulit, Terburu-buru, atau Terlewat

Bagian yang menunjukkan tanda kesulitan atau ketidaklengkapan: ditanyakan mahasiswa, disebut sulit oleh dosen, dikoreksi atau diulang dosen, dikebut karena waktu, atau dilewati dan dijadikan bahan belajar mandiri.

Untuk setiap item: satu baris tentang apa yang terjadi dan mengapa ia ditandai, lalu `💬 Extra tip:` berisi penjelasan yang ramah pemula, dengan analogi sederhana bila membantu.

## 9. Isi Slide yang Tidak Dibahas

Hanya bila ada lampiran slide. Daftar slide atau bagian materi yang tidak disinggung sama sekali di transkrip, dengan nomor slide dan ringkasan satu baris. Bila tidak ada lampiran, hapus bagian ini dan geser nomor bagian berikutnya.

## 10. Celah Transkrip dan Rujukan Visual

1. Bagian yang tidak jelas, terpotong, atau kemungkinan salah transkrip, dengan timestamp.
2. Isi visual yang ditunjuk dosen tapi tidak dibacakan ("seperti terlihat di slide ini"), supaya pembaca bisa mengeceknya di slide.
