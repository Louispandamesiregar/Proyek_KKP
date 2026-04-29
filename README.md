# 🏥 RS Analytics — Google Maps Review Scraper & Dashboard

Aplikasi berbasis Python yang mengintegrasikan **bot scraper ulasan Google Maps** (Selenium) dengan **dashboard analisis sentimen** interaktif (Streamlit + Plotly). Dirancang untuk keperluan Laporan Kerja Praktek (KP) — analisis kepuasan pasien rumah sakit di Bekasi.

> **Kepatuhan Hukum**: Sistem ini **tidak** mengekstrak nama akun pengguna Google Maps, sesuai **UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi (UU PDP)**.

---

## 🌟 Fitur Utama

| Fitur | Deskripsi |
|---|---|
| **Scraper Semi-Manual** | Bot Selenium mengotomasi scroll & ekstraksi; navigasi tab ulasan dilakukan manual oleh pengguna |
| **Input RS Dinamis** | 3 nama rumah sakit dapat diisi langsung di UI Streamlit — tidak perlu edit kode |
| **Analisis NPS** | Ulasan dikategorikan sebagai Promotor / Pasif / Detraktor berdasarkan rating |
| **Fokus Area Otomatis** | Keluhan dikategorikan ke 5 area: Administrasi, Tenaga Medis, Waktu Tunggu, Fasilitas, Harga |
| **Deteksi Tipe Pasien** | Mendeteksi BPJS / Asuransi / Umum dari isi teks ulasan |
| **Dashboard Interaktif** | KPI cards, donut chart, stacked bar, grouped bar komparasi antar RS |
| **Komparasi Head-to-Head** | Membandingkan % keluhan antar rumah sakit secara dinamis dari data Excel |
| **Kepatuhan UU PDP** | Nama akun Google Maps **tidak** diambil — hanya rating, tanggal, dan teks ulasan |

---

## 📋 Prasyarat

- Python **3.9+**
- Google Chrome (versi terbaru)
- Koneksi internet aktif

---

## 🛠️ Instalasi

1. **Clone repository:**
   ```bash
   git clone https://github.com/Louispandamesiregar/maps_scraper.git
   cd maps_scraper
   ```

2. **Instal dependensi:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Cara Menjalankan

```bash
streamlit run app.py
```

Browser akan otomatis terbuka ke `http://localhost:8501`.

---

## 📖 Alur Penggunaan

### 1. Control Panel Scraper
1. Buka menu **"Control Panel Scraper"** di sidebar.
2. Isi ketiga nama rumah sakit di kolom input yang tersedia *(nama harus persis seperti di Google Maps)*.
3. Klik **"▶️ Mulai Scraping"** — bot akan membuka Chrome dan menavigasi ke Google Maps.
4. Saat status berubah menjadi **"Menunggu interaksi manual"**:
   - Pindah ke jendela Chrome yang terbuka.
   - Klik tab **"Ulasan"** di halaman RS.
   - Klik **"Urutkan"** → pilih **"Terbaru"**.
5. Kembali ke Streamlit, klik **"Lanjutkan (Scroll)"**.
6. Bot akan scroll otomatis hingga **1.000 ulasan berteks**, lalu lanjut ke RS berikutnya (ulangi langkah 4–5).
7. Setelah selesai, data tersimpan di `Data_Komparasi_RS_Bekasi.xlsx`.

### 2. Dashboard Visualisasi
1. Buka menu **"Dashboard Visualisasi"** di sidebar.
2. Pilih rumah sakit dari dropdown untuk memfilter tampilan.
3. Lihat KPI, grafik distribusi, dan tabel detail ulasan.

---

## 📊 Daftar Kolom Output (Excel)

| Kolom | Keterangan |
|---|---|
| `Rumah Sakit` | Nama RS target |
| `Periode` | Format MM-YYYY (dikonversi dari tanggal relatif Google Maps) |
| `Rating Lengkap` | Teks rating dari atribut `aria-label` |
| `Tipe Pasien` | BPJS / Asuransi / Umum (dari isi ulasan) |
| `Fokus Area` | Kategori keluhan (bisa lebih dari satu, dipisah `&`) |
| `Klasifikasi NPS` | Promotor / Pasif / Detraktor |
| `Ulasan` | Teks ulasan publik |

> ⚠️ Kolom **Nama Akun** tidak ada di output — dihapus untuk kepatuhan UU PDP.

---

## 📂 Struktur Proyek

```text
maps_scraper/
├── app.py                        # UI Streamlit: Dashboard & Control Panel
├── scraper.py                    # Bot Selenium: scraping, ekstraksi & analitik
├── requirements.txt              # Daftar dependensi Python
├── README.md                     # Panduan ini
├── detail_proyek.md              # Dokumentasi teknis mendalam
├── .gitignore                    # Mengecualikan venv, __pycache__, .xlsx, dll
└── Data_Komparasi_RS_Bekasi.xlsx # Output hasil scraping (digenerate otomatis)
```

---

## 🛡️ Teknologi yang Digunakan

| Library | Fungsi |
|---|---|
| `streamlit` | Web UI & Control Panel |
| `selenium` | Otomatisasi browser Chrome |
| `webdriver-manager` | Auto-download ChromeDriver kompatibel |
| `pandas` | Transformasi & deduplication data |
| `plotly` | Visualisasi grafik interaktif |
| `openpyxl` | Simpan output ke file `.xlsx` |
| `threading` | Jalankan scraper di background thread |

---

## ⚠️ Catatan Teknis

- **Batas ulasan**: Maksimal 1.000 ulasan berteks per RS (ulasan tanpa teks diabaikan).
- **Deduplication**: Baris duplikat (`Rumah Sakit` + `Ulasan` sama) dihapus otomatis.
- **CSS Selector**: Scraper bergantung pada class CSS Google Maps. Jika Google memperbarui strukturnya, selector perlu disesuaikan.
- **Bahasa browser**: Chrome dibuka dengan `--lang=id` agar tanggal relatif muncul dalam Bahasa Indonesia.
- **Thread safety**: Log dibatasi 200 entri (FIFO) untuk mencegah memory leak.

---

Dikembangkan untuk keperluan **Laporan Kerja Praktek (KP)** — Analisis Sentimen Ulasan Rumah Sakit.