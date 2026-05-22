# Sistem RAG Hukum Indonesia dengan Query Reformulation (Double-Hop)

Proyek ini adalah implementasi sistem **Retrieval-Augmented Generation (RAG)** tingkat lanjut yang dirancang khusus untuk menjawab pertanyaan hukum Indonesia. Sistem ini menggunakan metode **"Double-Hop"** dan **Query Reformulation** untuk meningkatkan akurasi pencarian dokumen dan relevansi jawaban.

Saat ini didukung oleh **Qwen 3 32B (via Groq)** untuk kecepatan dan kecerdasan analisis, serta **Google Gemini-2.5-Flash** sebagai alternatif.

## 🚀 Fitur Utama & Pencapaian

1.  **Double-Hop Retrieval Logic**: Melakukan pencarian dua kali (Konteks Awal -> Reformulasi -> Pencarian Presisi).
2.  **Query Reformulation (Bahasa Awam -> Hukum)**: Menggunakan LLM untuk menerjemahkan pertanyaan pengguna seperti *"Bos potong gaji seenaknya"* menjadi kueri hukum standar.
    *   **Hasil Evaluasi**: Mencapai **100% Hit Rate** pada dataset pengujian bahasa sehari-hari.
3.  **Cross-Encoder Reranking**: Mengurutkan ulang dokumen untuk memastikan regulasi yang paling relevan muncul diposisi #1.
4.  **UI Interaktif**: Menggunakan **Streamlit** untuk antarmuka chat yang responsif.
5.  **Cloud Deployment**: Siap dideploy ke **Modal** untuk skalabilitas serverless.

## 🔄 Alur Kerja (End-to-End Flow)

1.  **Hop 1: Pencarian Awal (Context Gathering)**
    *   Sistem mencari dokumen kasar di Vector DB menggunakan pertanyaan asli.
2.  **Reasoning & Reformulation**
    *   **Qwen 3 32B** menganalisis hasil pencarian (Top 3).
    *   Mereformulasi pertanyaan awam menjadi pertanyaan hukum baku.
3.  **Hop 2: Pencarian Presisi (Precision Search)**
    *   Sistem mencari ulang menggunakan *Query Reformulasi*.
    *   Dokumen di-rerank menggunakan model Cross-Encoder (Top 8).
4.  **Generation (Pembuatan Jawaban)**
    *   **Qwen 3 32B** menyusun jawaban berdasarkan dokumen hukum terpilih, menyertakan dasar hukum dan interpretasi.

## 🛠️ Teknologi yang Digunakan

*   **Language**: Python 3.10+
*   **LLM Utama**: **Qwen 3 32B** (via Groq API)
*   **LLM Alternatif**: **Gemini 2.5 Flash** (Google)
*   **Embedding**: Google Text-Embedding-004
*   **Vector Database**: FAISS (CPU)
*   **Frontend**: Streamlit
*   **Deployment**: Modal (Serverless)

## 📂 Struktur Proyek

```text
legal-rag-system/
├── data/
│   ├── kategori_hukumonline_sample.json      # Dataset artikel hukum
│   └── eval_datasets/               # Dataset evaluasi 
|       ├── evaluation_dataset.json  # Evaluasi Hit Rate & MRR
|       └── ragas_input.json         # Evaluasi Faithfllnes & Relevance 
├── src/
│   ├── evaluation/                  # Script evaluasi
│   ├── config.py                    # Konfigurasi API
│   ├── ingestion.py                 # Indexing & Metadata
│   ├── rag_engine.py                # Core Logic (Reformulation + Rerank)
│   ├── generate_eval_data.py        # Generator Data Evaluasi (Layman Style)
│   └── evaluation.py                # Script Pengujian (Retrieval Only)
├── app.py                           # Frontend Streamlit
├── main.py                          # CLI Version
├── modal_app.py                     # Modal Deployment Config
└── requirements.txt                 # Dependensi Python
```

## 💻 Cara Menjalankan

### Prasyarat
*   Python 3.10+
*   API Key: **Groq API Key** (untuk Qwen) dan **Google API Key** (untuk Embedding).

### 1. Setup Lokal (Streamlit)
```powershell
# 1. Clone & Masuk Folder
git clone https://github.com/JHIA/query-reformulation-rag.git
cd query-reformulation-rag

# 2. Setup Venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install
pip install -r requirements.txt

# 4. Setup .env
# Buat file .env dan isi:
# GOOGLE_API_KEY=...
# GROQ_API_KEY=...
# LLM_PROVIDER=groq
# GROQ_MODEL=qwen/qwen-2.5-32b-instruct

# 5. Jalankan
streamlit run app.py
```

### 2. Deployment ke Modal (Serverless)
```powershell
# 1. Setup Modal
pip install modal
modal setup

# 2. Upload Volume (Index FAISS)
modal volume create rag-storage
modal volume put -f rag-storage faiss_index data/faiss_index

# 3. Deploy
modal deploy modal_app.py
```

## 📊 Laporan Evaluasi Lengkap

**Tanggal:** 26 Desember 2025

### 1. Ringkasan
Tujuan pengujian ini adalah menjawab pertanyaan: **"Jika ada orang bertanya pakai bahasa sehari-hari (curhat), apakah sistem bisa menemukan pasal atau aturan hukum yang benar?"**.

### 2. Metodologi
Kami merancang skenario pengujian yang ketat untuk menghindari bias evaluasi:
1. Pembuatan Soal (Dataset Generation):
Menggunakan AI yang dipersona sebagai "Orang Awam" untuk men-generate pertanyaan natural (natural language queries) dengan gaya bahasa sehari-hari dari 15 kategori hukum berbeda.

2. Penilaian Ketepatan Retrieval (Hit Rate & MRR):
Kami menilai performa pencarian dokumen menggunakan dua metrik utama:
- Hit Rate (Recall@K): Apakah dokumen hukum yang relevan berhasil ditemukan di dalam daftar hasil pencarian teratas (Top-K).
- MRR (Mean Reciprocal Rank): Seberapa tinggi peringkat (ranking) dokumen relevan pertama yang muncul, untuk mengukur efisiensi pengguna dalam menemukan jawaban tanpa scrolling jauh.

3. Penilaian Kualitas Generasi (LLM-as-a-Judge):
Kami menggunakan skenario LLM-as-a-Judge untuk mengevaluasi dua aspek kualitas jawaban:
- Faithfulness: Mengukur apakah jawaban sistem murni bersumber dari dokumen konteks yang ditemukan (untuk mendeteksi halusinasi).
- Answer Relevancy: Mengukur apakah jawaban tersebut relevan dan menjawab inti pertanyaan pengguna.

### 3.1  Penilaian Ketepatan Retrieval (Hit Rate & MRR)
Berikut adalah 15 pertanyaan "bahasa awam" yang diujikan, lengkap dengan transformasi Query dan perbandingan performa (AI vs Tanpa AI):

| Topik | Curhatan User (Input) | Query Reformulasi (AI) | Dokumen Target (Jawaban) | Rank (AI) | Perubahan (vs Raw) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Bisnis** | *"Gimana cara ngurus izin jual beli BBM?"* | *"Prosedur dan persyaratan pengurusan izin usaha perdagangan BBM menurut UU Migas"* | Izin Usaha untuk Kegiatan Jual Beli BBM | **#1** | ➖ Stabil |
| **HAM** | *"Napi dibully di penjara, ada hukum yang lindungi?"* | *"Perlindungan hukum terhadap narapidana korban kekerasan/perundungan di Lapas"* | Perlindungan Terhadap Napi Korban Bullying | **#1** | ➖ Stabil |
| **Hukum** | *"Bedanya perlindungan vs penegakan hukum apa?"* | *"Perbedaan Konseptual Antara Perlindungan Hukum dan Penegakan Hukum"* | Pengertian Perlindungan Hukum dan Penegakan Hukum | **#1** | ➖ Stabil |
| **Hak Cipta** | *"Barang dijual orang lain tanpa izin, lapor pakai apa?"* | *"Penegakan hukum atas pelanggaran hak distribusi eksklusif (UU 7/2014 Pasal 11)"* | Penegakan Hukum Pelanggaran Hak Distribusi | **#1** | ➖ Stabil |
| **Keluarga** | *"Suami sering talak lisan, itu cerai beneran?"* | *"Status Perkawinan Setelah Talak Lisan dalam Hukum Islam & Keabsahannya"* | Status Perkawinan Jika Sering Ditalak Lisan | **#1** | ➖ Stabil |
| **Negara** | *"Hak warga negara di mata hukum apa aja?"* | *"Hak warga negara dalam bidang hukum (UUD 1945 & UU No. 39/1999)"* | 11 Hak Warga Negara dalam Bidang Hukum | **#1** | 🔼 **NAIK (2 -> 1)** |
| **Kerja** | *"Anak kecil boleh kerja nggak?"* | *"Ketentuan hukum izin kerja & perlindungan bagi pekerja anak (UU Ketenagakerjaan)"* | Perlindungan Hukum untuk Pekerja Anak | **#1** | 🔼 **NAIK (2 -> 1)** |
| **Bola** | *"Aturan pemain bola asing di Indonesia gimana?"* | *"Syarat hukum dan regulasi bagi Pemain Sepak Bola Asing di Liga Indonesia"* | Aturan tentang Pemain Sepak Bola Asing | **#2** | 🔻 Turun (1 -> 2) |
| **Perdata** | *"Maksudnya 'Renvoi' dalam putusan MA apa?"* | *"Dasar Hukum dan Tata Cara Renvoi Putusan Mahkamah Agung"* | Dasar Hukum dan Tata Cara Renvoi Putusan MA | **#1** | ➖ Stabil |
| **Laundry** | *"Baju ilang di laundry, wajib ganti rugi?"* | *"Kewajiban ganti rugi pemilik laundry atas hilangnya barang konsumen (UU Perlindungan Konsumen)"* | Ganti Rugi Laundry Jika Baju Hilang | **#1** | ➖ Stabil |
| **Tanah** | *"Tanah wakaf boleh dijual lagi nggak?"* | *"Status hukum peralihan/penjualan tanah wakaf oleh nadhir (UU No. 41/2004)"* | Hukum Menjual Tanah Wakaf | **#2** | 🔻 Turun (1 -> 2) |
| **Narkoba** | *"Syarat rehabilitasi narkoba gimana?"* | *"Syarat dan Prosedur Permohonan Rehabilitasi Hukum Tersangka Narkoba"* | Syarat dan Prosedur Rehabilitasi | **#1** | ➖ Stabil |
| **Profesi** | *"Pengacara kebal hukum nggak?"* | *"Hak imunitas advokat vs tuntutan pidana (UU Advokat)"* | Apakah Advokat Dapat Dituntut Pidana? | **#1** | ➖ Stabil |
| **UMKM** | *"Startup boleh kelola pasar tradisional?"* | *"Legalitas perusahaan startup mengelola pasar tradisional (Perpres 112/2007)"* | Pengelolaan Pasar Tradisional oleh Startup | **#1** | ➖ Stabil |
| **ITE** | *"Sebarin lagu parodi ngehina orang kena pasal?"* | *"Tindakan hukum menyebarkan lagu parodi bermuatan penghinaan (UU ITE & KUHP)"* | Hukum Menyebarkan Lagu Bermuatan Penghinaan | **#1** | 🔼 **NAIK (2 -> 1)** |

### 3.2 Penilaian Kualitas Generasi (LLM-as-a-Judge)
Selain evaluasi sistem otomatis, kami melakukan **LLM as a Judge Simulation** terhadap 15 sampel dengan kriteria penilaian **Faithfulness** dan **Answer Relevancy**. Dataset lengkap dengan jawaban LLM dapat dilihat di folder `eval_datasets/ragas_input.json`

## 📊 Detail Evaluasi Per Sampel

### 1. Izin Usaha Jual Beli BBM
> **Pertanyaan:** "Gimana sih caranya ngurus izin kalau mau buka usaha jual beli BBM? Ribet nggak ya?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Jawaban mengutip PP No. 28/2025 dan PP No. 36/2004 secara akurat dari context. Tidak ada info tambahan yang mengada-ada.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Jawaban langsung merespons keluhan "ribet nggak" dengan penjelasan tentang OSS dan klasifikasi risiko. Sangat solutif.

### 2. Perlindungan Napi Korban Bullying
> **Pertanyaan:** "Kalau ada napi yang dibully... ada hukum yang ngelindungin mereka nggak sih?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Jawaban secara presisi mengutip UU No. 22 Tahun 2022 Pasal 3 huruf b dan c dari context yang tersedia.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Langsung menjawab "Ya, ada hak perlindungan", sesuai intent user yang mencari kepastian.

### 3. Perlindungan Hukum vs Penegakan Hukum
> **Pertanyaan:** "Sebenernya apa sih bedanya perlindungan hukum sama penegakan hukum?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Definisi diambil tepat dari pendapat ahli (Philipus M. Hadjon, Jimly Asshiddiqie) yang ada di dokumen. Perbedaan preventif/represif dijelaskan dengan baik.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Struktur jawaban menggunakan tabel perbandingan sangat membantu menjawab kebingungan user.

### 4. Pelanggaran Hak Distribusi Eksklusif
> **Pertanyaan:** "Misal aku punya hak tunggal... ada orang lain ikut jualan tanpa izin, bisa dilaporin pakai hukum apa?"

- **Faithfulness:** ⭐⭐⭐⭐ (4/5)
  - *Analisis:* Jawaban menyebutkan sanksi pidana Pasal 100 UU Merek. Meskipun ada dasar hukumnya di satu dokumen, dokumen lain dalam context secara eksplisit menyebutkan *"tidak mengatur sanksi terhadap pihak tidak resmi"* (untuk kasus reseller barang asli). Jawaban AI kurang menangkap nuansa pengecualian ini, sehingga skor dikurangi sedikit karena generalisasi.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Jawaban komprehensif mencakup opsi pidana dan perdata sesuai keinginan user untuk "melapor".

### 5. Status Talak Lisan
> **Pertanyaan:** "Suami sering banget bilang talak... cuma lisan doang, status nikahnya cerai beneran atau nggak?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Jawaban tegas mengutip Pasal 39 UU Perkawinan dan KHI bahwa perceraian hanya sah di depan pengadilan. Sangat setia pada dokumen.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Langsung menenangkan kegelisahan user dengan jawaban "Status Perkawinan Tetap Sah".

### 6. 11 Hak Warga Negara
> **Pertanyaan:** "Hak-hak kita di mata hukum itu apa aja sih? Katanya ada 11 ya?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Jawaban merinci poin 1-11 dengan sangat rapi sesuai context dokumen yang memang membahas 11 hak tersebut. Akurasi 100%.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Format listicle (poin-poin) sangat cocok untuk pertanyaan jenis ini.

### 7. Pekerja Anak
> **Pertanyaan:** "Anak kecil di bawah umur itu sebenernya boleh kerja nggak sih?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Jawaban menjelaskan nuansa hukum dengan tepat: *"Dilarang, TAPI ada pengecualian (usia 13-15 untuk pekerjaan ringan)"*. Ini diambil akurat dari UU Ketenagakerjaan di context.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Menjawab keraguan "boleh nggak sih" dengan penjelasan bersyarat yang mudah dipahami.

### 8. Pemain Bola Asing
> **Pertanyaan:** "Pemain bola asing... aturannya gimana?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Menggabungkan info dari UU Keolahragaan, UU Ketenagakerjaan, dan Peraturan PSSI yang tersebar di chunks berbeda menjadi satu jawaban utuh. Synthesis skill yang baik.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Relevan, mencakup izin kerja (IMTA) dan regulasi olahraga.

### 9. Renvoi Putusan MA
> **Pertanyaan:** "Maksudnya 'Renvoi' dalam putusan MA itu apa sih?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Definisi Renvoi sebagai perbaikan kesalahan tulis (clerical error) diambil tepat dari Perma No. 6 Tahun 2022 di context.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Menjelaskan istilah teknis hukum dengan bahasa yang tidak terlalu kaku.

### 10. Ganti Rugi Laundry
> **Pertanyaan:** "Kalau baju ilang pas lagi di-laundry, pemilik wajib ganti rugi nggak?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Mengutip Pasal 19 UU Perlindungan Konsumen tentang kewajiban ganti rugi dalam 7 hari. Sangat akurat sesuai dokumen.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Sangat memihak konsumen sesuai pertanyaan user, memberikan langkah konkret (klaim BPSK).

### 11. Jual Tanah Wakaf
> **Pertanyaan:** "Tanah yang udah diwakafin itu boleh dijual lagi nggak sih?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Jawaban tegas **"DILARANG"** berdasarkan Pasal 40 UU Wakaf. Menyebutkan sanksi pidana 5 tahun (Pasal 67) yang ada di context.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Jawaban langsung to the point tanpa berbelit-belit.

### 12. Rehabilitasi Tersangka Narkoba
> **Pertanyaan:** "Kalau tersangka narkoba mau minta rehabilitasi, syarat sama prosedurnya gimana?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Menjelaskan prosedur Praperadilan (Pasal 77 KUHAP) dan syarat khusus (asesmen) yang ada di dokumen.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Alur prosedur dijelaskan step-by-step (Pengajuan -> Pemeriksaan -> Putusan 7 hari).

### 13. Imunitas Advokat & Notaris
> **Pertanyaan:** "Pengacara atau notaris itu kebal hukum nggak sih?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Membedakan dengan jelas: Advokat punya imunitas terbatas (Pasal 16 UU Advokat), Notaris **TIDAK** punya (UU Jabatan Notaris). Pembedaan ini diambil tepat dari context.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Menjawab mitos "kebal hukum" dengan fakta hukum yang berimbang.

### 14. Startup Kelola Pasar Tradisional
> **Pertanyaan:** "Bisa nggak sih perusahaan startup gitu ngelola pasar tradisional?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Mengutip Perpres 112/2007 Pasal 4 yang membolehkan swasta mengelola pasar. Syarat kemitraan UMKM juga disertakan sesuai dokumen.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Jawaban "Bisa, dengan syarat..." sangat pas menjawab keraguan user.

### 15. Lagu Parodi Penghinaan
> **Pertanyaan:** "Kalau iseng nyebarin lagu parodi yang isinya ngehina orang, itu bisa kena pasal hukum nggak ya?"

- **Faithfulness:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Mengutip Pasal 27A UU ITE (terbaru 2024) tentang menyerang kehormatan. Menjelaskan unsur "sengaja" dan sanksi 2 tahun penjara sesuai context.
- **Relevancy:** ⭐⭐⭐⭐⭐ (5/5)
  - *Analisis:* Menjawab kekhawatiran "iseng" dengan penjelasan unsur "niat" (mens rea) dalam hukum pidana.

### 4. Hasil & Kesimpulan

Pengujian pada langkah 3.1 dan 3.2 melibatkan 4 metrik yaitu

1. Faithfulness: Mengukur konsistensi faktual jawaban yang dihasilkan sistem terhadap konteks dokumen yang diberikan (untuk mendeteksi halusinasi).
2. Answer Relevancy: Mengukur tingkat relevansi jawaban sistem terhadap pertanyaan pengguna (user query).
3. Hit Rate (Recall@K): Mengukur peluang sistem menemukan setidaknya satu dokumen yang relevan dalam daftar top-k hasil pencarian.
4. MRR (Mean Reciprocal Rank): Mengukur akurasi peringkat sistem dengan memberikan bobot lebih tinggi jika dokumen relevan muncul di urutan teratas

Hasil pengujian adalah sebagai berikut:

| Metrik | Skor | Predikat |
| :--- | :--- | :--- |
| **Faithfulness** | **98.6%** | Sangat Andal |
| **Relevancy** | **100%** | Sangat Relevan |
| **Hit Rate** | **100%** | Sangat Efektif |
| **MRR (tanpa query reformulation)** | **90%** | Presisi Tinggi |
| **MRR (dengan query reformulation)** | **93%** | Presisi Tinggi |

Sistem ini menunjukkan kematangan yang luar biasa dalam 3 aspek utama:

1.  **Context Understanding:** Sistem mampu memilah informasi yang relevan dari chunks dokumen yang panjang dan kompleks.
2.  **Regulatory Compliance:** Sistem sangat patuh pada aturan hukum terbaru (contoh: mengutip UU ITE 2024 dengan benar).
3.  **User Intent Alignment:** Kemampuan reformulasi query terbukti **sukses**. Jawaban yang dihasilkan benar-benar "nyambung" dengan pertanyaan bahasa sehari-hari dengan meningkatkan akurasi dan ketepatan ranking, bridging the gap between layman language and legal terminology.

---

### 5. Identifikasi Celah & Keterbatasan
Sebagai bentuk transparansi akademik, kami mencatat keterbatasan berikut:

1.  **Cakupan Data Terbatas**:
    *   Database hanya berisi **15 kategori hukum** dengan **~50 artikel per kategori** (~750 total). Skor 100% berlaku untuk lingkup data ini, namun perlu pengujian lebih luas untuk skala nasional.
    
2.  **Privasi Data**:
    *   Sistem bergantung pada API Pihak Ketiga (Groq/Google), sehingga data pertanyaan dikirim keluar. Tidak disarankan untuk kasus sangat rahasia tanpa enkripsi tambahan atau model On-Premise.

3.  **Ketergantungan Infrastruktur**:
    *   Bergantung penuh pada uptime API Cloud. Jika API down, sistem tidak memiliki fallback lokal.

---
