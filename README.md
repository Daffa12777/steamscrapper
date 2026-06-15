# 🎮 Steam Game Type Classifier

> **Tugas Besar Machine Learning** — Klasifikasi jenis game Steam ke 3 kategori berdasarkan mode pemain (Singleplayer / Multiplayer / Hybrid) menggunakan supervised learning, dilengkapi web app deployment dengan Streamlit.

🔗 **Live Demo:** _isi link Streamlit Cloud kamu di sini_

---

## 👥 Identitas Kelompok

| Nama | NIM |
|------|-----|
| _isi nama_ | _isi NIM_ |
| _isi nama_ | _isi NIM_ |
| _isi nama_ | _isi NIM_ |

**Mata Kuliah:** _isi nama mata kuliah_
**Kelas:** _isi kelas_
**Dosen Pengampu:** _isi nama dosen_

---

## 📊 Tentang Project

Project ini membangun model **klasifikasi multi-kelas** untuk memprediksi **jenis game Steam** berdasarkan metadata-nya (harga, umur, OS support, controller support, jumlah review, kategori Steam).

Target klasifikasi dibagi menjadi **3 tier** berdasarkan kolom `Number Of Players`:

| Kelas | Deskripsi | Contoh |
|-------|-----------|--------|
| 🎯 **Singleplayer** | Game khusus untuk solo | The Witcher 3, Stardew Valley, indie story-driven |
| 👥 **Multiplayer** | Game khusus multipemain (PvP/Co-op/Online) | Counter-Strike 2, Dota 2, Valorant |
| 🔄 **Hybrid** | Game dengan mode solo + multiplayer | Elden Ring, Minecraft, Terraria |

### Tujuan Project
- Mengotomatisasi klasifikasi jenis game tanpa membaca deskripsi konten
- Mempelajari pola karakteristik tiap jenis game di marketplace Steam
- Mengaplikasikan workflow supervised learning end-to-end (EDA → preprocessing → modeling → deployment)

---

## 🗂️ Dataset

- **Sumber:** Web scraping dari [Steam Store](https://store.steampowered.com) (script: `steamscrapper/Scrapper2.py`)
- **Jumlah data:** 1.130 baris × 13 kolom asli (19 kolom setelah feature engineering)
- **Kategori scrape:** Top Sellers, Most Played, New Releases, Upcoming Releases
- **Periode snapshot:** Juni 2026

### Kolom Dataset

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `AppID` | numeric | ID unik game di Steam |
| `Name` | text | Nama game |
| `Published Date` | date | Tanggal rilis |
| `Original Price` | numeric | Harga asli (Rp) |
| `Discount Price` | numeric | Harga setelah diskon |
| `Discount %` | percent | Persentase diskon |
| `Reviews Count` | numeric | Jumlah ulasan |
| `Reviews Positive` | percent | % ulasan positif |
| `Review Label` | category | Label sentimen Steam |
| `Search Filter` | category (multi) | Kategori filter Steam (multi-label) |
| `Number Of Players` | category (multi) | Mode pemain → **sumber target** |
| `Controller Support` | category (multi) | Dukungan controller |
| `OS` | category (multi) | Sistem operasi yang didukung |

---

## 📁 Struktur Folder

```
KELOMPOK1/
├── .streamlit/
│   └── config.toml                       # Konfigurasi tema Streamlit
├── dataset/
│   └── games_all.csv                     # Dataset hasil scraping
├── model/
│   ├── model_game_type.pkl               # Model Random Forest terlatih
│   └── model_meta.pkl                    # Metadata: feature columns & labels
├── steamscrapper/
│   └── Scrapper2.py                      # Script scraping Steam Store
├── app.py                                # Streamlit web app
├── Tugas_Besar_ML_JenisGame.ipynb        # Notebook ML lengkap
├── requirements.txt                      # Dependencies
└── README.md
```

---

## 🤖 Pipeline Machine Learning

Alur lengkap ada di notebook `Tugas_Besar_ML_JenisGame.ipynb`:

### 1. Load & Eksplorasi Data
Membaca CSV, cek tipe data, nilai kosong, deskripsi statistik.

### 2. EDA — 39 Insight
- Statistik dasar (harga, diskon, review, tahun rilis)
- Distribusi target jenis game
- Analisis kolom baru (OS, Controller, Number Of Players)
- **Relasi karakteristik dengan tiap jenis game:**
  - Game **Multiplayer** dominan **gratis (48.7%)** & Windows-only
  - Game **Singleplayer** paling disukai komunitas (% positif 86.6%)
  - Game **Hybrid** di tengah-tengah, paling banyak (48.5% data)
- Korelasi numerik (umur ↔ diskon = 0.61)

### 3. Cleaning & Feature Engineering
- Parsing teks → numerik (harga, diskon, tanggal)
- Imputasi median untuk nilai kosong
- Fitur turunan: `is_free`, `has_discount`, `game_age_days`, `name_len`
- One-hot encoding multi-value: `OS`, `Controller Support`, `Search Filter`

### 4. Standarisasi & Feature Selection
- **StandardScaler** untuk mean 0, std 1
- **Mutual Information** mengukur informativitas tiap fitur

### 5. Split Data
- **Train-test split 80:20** dengan stratifikasi (karena 1 game = 1 baris, tidak butuh group-aware split)

### 6. Penanganan Imbalance — SMOTE
Kelas Multiplayer minoritas (10.7%) → SMOTE oversampling **hanya pada train set**.

### 7. Model Building & Comparison
5 algoritma klasifikasi dibandingkan:
- Logistic Regression
- Decision Tree
- K-Nearest Neighbors
- **Random Forest** ✅ (terbaik)
- Gradient Boosting

### 8. Hyperparameter Tuning
GridSearchCV + 5-fold StratifiedKFold, scoring `f1_macro`. Tuning:
- `n_estimators`, `max_depth`, `min_samples_leaf`, `max_features`

### 9. Evaluasi
Accuracy, F1-macro/weighted, Precision, Recall, Confusion Matrix, feature importance, cek overfitting.

### 10. Export Model
joblib (.pkl) → siap untuk deployment Streamlit.

---

## 📈 Hasil Akhir Model

| Metrik | Skor | Catatan |
|--------|------|---------|
| Akurasi test | **59.4%** | Di atas baseline tebak-mayoritas (48.5%) |
| F1-macro | **0.56** | Jauh di atas baseline macro (~0.22) |
| F1-weighted | 0.60 | |
| Train accuracy | 99.9% | Overfitting ringan, sudah dikontrol via tuning |

### Performa per Kelas

| Kelas | Precision | Recall | F1-score | Support |
|-------|-----------|--------|----------|---------|
| Singleplayer | 0.62 | 0.66 | 0.64 | 91 |
| Multiplayer | 0.38 | 0.50 | 0.43 | 24 |
| Hybrid | 0.64 | 0.56 | 0.60 | 109 |

**Fitur paling berpengaruh:** umur game, harga asli, harga diskon, panjang nama, controller support.

---

## 🚀 Cara Menjalankan

### 1. Setup Environment

```bash
# Clone repo
git clone https://github.com/USERNAME/steamscrapper.git
cd steamscrapper

# Install dependencies
pip install -r requirements.txt
```

### 2. Jalankan Notebook (training & analisis)

Buka `Tugas_Besar_ML_JenisGame.ipynb` di Jupyter / VS Code, **Run All Cells**. File `.pkl` akan ter-generate otomatis di folder `model/`.

### 3. Jalankan Web App

```bash
streamlit run app.py
```

App akan terbuka di `http://localhost:8501`. Isi karakteristik game di form → klik **Jalankan Klasifikasi** → lihat hasil + probabilitas + analisis kontekstual.

---

## 🌐 Deployment

App di-deploy menggunakan **Streamlit Community Cloud** (gratis, tanpa server sendiri).

### Cara deploy
1. Push project ke GitHub (public repo)
2. Buka [share.streamlit.io](https://share.streamlit.io)
3. Login dengan GitHub → klik **New app**
4. Pilih repo → set main file: `app.py`
5. **Advanced settings** → Python version: **3.13**
6. Klik **Deploy** (~5 menit untuk build pertama)

App auto-redeploy setiap kali ada `git push` ke `main`.

---

## 🛠️ Tech Stack

| Komponen | Tool |
|----------|------|
| Bahasa | Python 3.13 |
| ML Library | scikit-learn 1.8, imbalanced-learn (SMOTE) |
| Data Processing | pandas, numpy |
| Visualisasi | matplotlib, seaborn |
| Web App | Streamlit 1.39+ |
| Model Persistence | joblib |
| Deployment | Streamlit Community Cloud |

---

## 📌 Temuan Penting

1. **Tidak ada duplikasi** di dataset baru (1130 game unik), berbeda dari iterasi sebelumnya yang punya duplikasi parah lintas kategori. Tidak butuh group-aware split.

2. **Pattern karakteristik jenis game** sangat jelas:
   - Multiplayer = gratis, Windows-only, popularitas tinggi, komunitas kritis
   - Singleplayer = berbayar, full controller, komunitas puas
   - Hybrid = di tengah-tengah, kelas mayoritas

3. **Multi-label encoding** diperlukan untuk kolom yang berisi multi-value (OS, Controller, Search Filter) — setiap kategori jadi fitur biner terpisah.

4. **SMOTE krusial** untuk kelas Multiplayer minoritas (hanya 119 sampel) — tanpa balancing, F1-macro turun signifikan.

5. **Akurasi 59% terdengar rendah, tapi jujur:** baseline tebak-mayoritas cuma 48.5%, dan F1-macro 0.56 vs baseline 0.22 → model **beneran belajar pola**, bukan asal nebak Hybrid.

---

## 🎯 Keterbatasan Model

- Model hanya membaca **metadata publik** (harga, OS, controller, review count, kategori)
- **Genre, gameplay, story, elemen sosial tidak terukur** — game dengan metadata mirip bisa punya gameplay yang sangat berbeda
- Kelas Multiplayer sulit diprediksi karena sampelnya cuma 119 (10.7%)
- Hasil prediksi adalah **referensi analitik**, bukan keputusan final

---

## 📄 Lisensi & Atribusi

Project ini dibuat untuk keperluan akademik (Tugas Besar Machine Learning).
Data dari Steam Store dimiliki oleh Valve Corporation.
Scraping dilakukan dengan menghormati `robots.txt` dan rate limit Steam.

---

---

