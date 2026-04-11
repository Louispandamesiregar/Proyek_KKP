# 🏥 Google Maps Scraper & Sentiment Dashboard (RS Bekasi 2025)

Proyek ini adalah alat otomatisasi untuk mengambil ulasan dari Google Maps menggunakan Selenium dan memvisualisasikannya ke dalam dashboard analisis sentimen menggunakan Streamlit dan Plotly.

## 🌟 Fitur Utama
* **Scraper Semi-Manual**: Mengambil ulasan secara real-time dari Google Maps dengan kontrol via web UI.
* **Analisis Sentimen & Fokus Area**: Mengkategorikan ulasan berdasarkan NPS (Promotor/Pasif/Detraktor) dan fokus area keluhan (Pelayanan, Fasilitas, Harga, dll).
* **Dashboard Interaktif**: Visualisasi KPI dan grafik perbandingan kompetitor menggunakan Plotly.
* **Komparasi Head-to-Head**: Membandingkan persentase keluhan antar rumah sakit.

## 📋 Prasyarat
Sebelum menjalankan, pastikan Anda telah menginstal:
* Python 3.x
* Google Chrome Browser

## 🛠️ Instalasi
1. Clone repository ini:
   ```bash
   git clone https://github.com/Louispandamesiregar/maps_scraper.git
   cd maps_scraper
   ```

2. Instal pustaka yang diperlukan:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Cara Menjalankan
Jalankan aplikasi Streamlit:
```bash
streamlit run app.py
```
Browser akan otomatis terbuka ke `http://localhost:8501`.

### Alur Penggunaan
1. Buka menu **Control Panel Scraper** di sidebar.
2. Klik tombol **▶️ Mulai Scraping** untuk membuka browser Google Maps.
3. Buka jendela Chrome yang muncul, klik tab **Ulasan**, lalu urutkan berdasarkan **Terbaru**.
4. Kembali ke web UI, klik tombol **Lanjutkan (Scroll)** untuk memulai pengambilan data otomatis.
5. Setelah selesai, buka menu **Dashboard Visualisasi** untuk melihat hasil analisis.

## 📊 Daftar Rumah Sakit yang Dipantau
1. **Primaya Hospital Bekasi Barat** (Target Utama)
2. RSUD dr. Chasbullah Abdulmadjid
3. RS Hermina Bekasi

## 📂 Struktur Proyek
| File | Deskripsi |
|---|---|
| `app.py` | Aplikasi utama Streamlit (Dashboard + Control Panel Scraper) |
| `scraper.py` | Script Selenium untuk scraping ulasan Google Maps |
| `requirements.txt` | Daftar dependensi Python |

Dikembangkan untuk keperluan Laporan Kerja Praktek (KP).