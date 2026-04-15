# Laporan Detail Proyek: Google Maps Scraper & Sentiment Dashboard (RS Analytics)

Dokumen ini memberikan penjelasan teknis mendalam mengenai arsitektur, logika, dan cara kerja sistem analisis ulasan rumah sakit yang telah dikembangkan.

## 1. Deskripsi Proyek
**RS Analytics** adalah aplikasi berbasis Python yang mengintegrasikan bot scraper ulasan Google Maps dengan dashboard visualisasi data. Sistem ini dirancang untuk memantau performa rumah sakit berdasarkan ulasan publik, mengkategorikan keluhan secara otomatis, dan memberikan wawasan strategis melalui metrik **Net Promoter Score (NPS)**.

---

## 2. Arsitektur Teknologi (Stack)
Proyek ini dibangun menggunakan teknologi modern berbasis Python:
*   **Aplikasi Web (UI)**: [Streamlit](https://streamlit.io/) — Digunakan untuk membangun antarmuka dashboard dan panel kontrol scraper secara cepat dan reaktif.
*   **Bot Scraper**: [Selenium WebDriver](https://www.selenium.dev/) — Digunakan untuk mengotomatisasi interaksi browser (Chrome) dalam mengambil data ulasan.
*   **Manajemen Browser**: [WebDriver Manager](https://pypi.org/project/webdriver-manager/) — Memastikan driver Chrome selalu terupdate secara otomatis.
*   **Pengolahan Data**: [Pandas](https://pandas.pydata.org/) — Digunakan untuk membersihkan, memfilter, dan menganalisis data mentah hasil scraping.
*   **Visualisasi Data**: [Plotly Express](https://plotly.com/python/) — Menghasilkan grafik interaktif seperti Pie Chart, Bar Chart, dan grafik komparatif.
*   **Penyimpanan**: [Excel (OpenPyXL)](https://openpyxl.readthedocs.io/) — Database lokal praktis dalam format `.xlsx`.

---

## 3. Struktur File & Folder
Struktur proyek dirancang secara modular:
```text
Proyek_KP/
├── app.py              # File utama (UI Dashboard & Logika State Jamak)
├── scraper.py          # Mesin Bot (Logika Selenium & Ekstraksi Data)
├── requirements.txt    # Daftar dependensi library Python
├── README.md           # Panduan instalasi dan penggunaan dasar
├── detail_proyek.md     # Laporan teknis mendalam (File ini)
├── .gitignore          # Daftar file yang dikecualikan dari Git (venv, cache)
└── Data_Komparasi_RS_Bekasi.xlsx  # Database hasil penarikan data (Output)
```

---

## 4. Alur Proses Sistem (Workflow)
Sistem bekerja melalui lima tahap utama:
1.  **Inisialisasi**: Pengguna menjalankan `streamlit run app.py`.
2.  **Scraping (Control Panel)**: 
    *   Bot membuka browser Google Maps ke target RS.
    *   Bot menunggu interaksi manual (klik tab Ulasan & Terbaru).
    *   Bot melakukan *Infinite Scroll* secara otomatis hingga mencapai target data.
3.  **Ekstraksi**: Selenium menyuntikkan JavaScript ke halaman untuk mengambil nama akun, rating, tanggal, dan teks ulasan tanpa memungut balasan dari pemilik RS.
4.  **Analisis Data (Preprocessing)**: 
    *   Sistem menghitung periode waktu (Bulan-Tahun).
    *   Sistem melakukan klasifikasi NPS dan Fokus Area berdasarkan teks ulasan.
5.  **Visualisasi (Dashboard)**: Data dimuat ke grafik interaktif untuk analisis manajemen.

---

## 5. Logika Utama yang Digunakan

### A. Mekanisme Scraping Semi-Manual
Berbeda dengan bot murni yang mudah diblokir, sistem ini menggunakan metode **Hybrid**:
*   **WebDriverWait**: Digunakan untuk memastikan halaman muat sempurna sebelum bot berinteraksi.
*   **Sync Logic**: Menggunakan `threading.Event()` untuk menghubungkan UI Streamlit dengan Bot yang berjalan di background.
*   **Human-Like Scrolling**: Menggunakan `time.sleep` dengan durasi acak (`random.uniform`) agar aktivitas bot terlihat natural oleh sistem keamanan Google.

### B. Algoritma Analisis Sentimen (Rating)
Sistem menggunakan standar **Net Promoter Score (NPS)**:
*   **Promotor**: Rating 4-5 (Pasien Puas/Loyal).
*   **Pasif**: Rating 3 (Pasien Netral).
*   **Detraktor**: Rating 1-2 (Pasien Kecewa - Sumber Titik Lemah).
*   **NPS Score**: Dikalkulasi dengan rumus: `% Promotor - % Detraktor`.

### C. Klasifikasi Fokus Area (Keyword Mapping)
Sistem melakukan pemindaian kata kunci pada teks ulasan untuk memetakan kategori keluhan:
*   **Administrasi**: kasir, daftar, pendaftaran, admin.
*   **Sikap Medis**: dokter, perawat, suster, ramah, jutek.
*   **Waktu Tunggu**: lama, antri, nunggu, lambat.
*   **Fasilitas**: bersih, ruang, parkir, ac, toilet.
*   **Harga**: mahal, biaya, bayar.

### D. Konversi Periode Waktu
Karena Google Maps menggunakan teks relatif (misal: "2 bulan lalu"), sistem menggunakan **Regex** dan logika tanggal untuk mengonversinya menjadi format bulan-tahun yang statis (`MM-YYYY`) agar bisa divisualisasikan dalam grafik tren.

---

## 6. Fitur Dashboard (Metrik Utama)
Dashboard menampilkan data secara dinamis berdasarkan rumah sakit yang dipilih:
*   **KPI Cards**: Menghitung Total Ulasan, Skor NPS (Live), dan jumlah masing-masing kategori.
*   **Pie Chart**: Menampilkan distribusi "Titik Lemah" dominan untuk perbaikan fasilitas.
*   **Bar Chart**: Membandingkan tingkat kepuasan antar tipe pasien (Umum/BPJS/Asuransi).
*   **HTML Custom Table**: Menampilkan detail ulasan secara utuh (tidak terpotong) dengan kemampuan scrolling internal.

---

## 7. Kesimpulan
Proyek ini menggabungkan kekuatan **Otomatisasi (Selenium)** dan **Analisis Data (Pandas)** untuk memberikan solusi intelijen bisnis bagi pihak rumah sakit dalam mengevaluasi layanan mereka secara objektif berdasarkan suara pasien di publik.
