from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
import pandas as pd
import re
import urllib.parse
import random

# ======================================================================
# DAFTAR RUMAH SAKIT YANG AKAN DI-SCRAPE
# ======================================================================
daftar_rs = [
    "Primaya Hospital Bekasi Barat",
    "RSUD dr. Chasbullah Abdulmadjid",
    "RS Hermina Bekasi"
]

# ======================================================================
# FUNGSI SCROLL OTOMATIS
# Menggulir panel ulasan hingga mencapai target 1000 ulasan
# ======================================================================
def fungsi_scroll_otomatis(driver, status_callback):
    jumlah_sebelumnya = 0
    stuck_counter = 0

    while True:
        try:
            jumlah_sekarang = driver.execute_script("""
                let reviews = document.querySelectorAll('.jftiEf');
                if(reviews.length > 0) {
                    let last_review = reviews[reviews.length - 1];
                    last_review.scrollIntoView(false);

                    let parent = last_review.parentElement;
                    while(parent) {
                        if(parent.scrollHeight > parent.clientHeight) {
                            parent.scrollTop = parent.scrollHeight;
                            break;
                        }
                        parent = parent.parentElement;
                    }
                }
                return reviews.length;
            """)

            if jumlah_sekarang >= 1000:
                status_callback(f"🎯 Target 1000 ulasan tercapai ({jumlah_sekarang} termuat). Berhenti menggulir.")
                break

            if jumlah_sekarang == jumlah_sebelumnya:
                stuck_counter += 1
                if stuck_counter > 3:
                    # Jika stuck, coba scroll mundur lalu maju kembali
                    driver.execute_script("""
                        let reviews = document.querySelectorAll('.jftiEf');
                        if(reviews.length > 0) {
                            let parent = reviews[0].parentElement;
                            while(parent) {
                                if(parent.scrollHeight > parent.clientHeight) {
                                    parent.scrollTop = parent.scrollTop - 500;
                                    setTimeout(() => { parent.scrollTop = parent.scrollHeight; }, 200);
                                    break;
                                }
                                parent = parent.parentElement;
                            }
                        }
                    """)
                    time.sleep(0.5)
                    stuck_counter = 0
            else:
                stuck_counter = 0

            jumlah_sebelumnya = jumlah_sekarang
            if jumlah_sekarang % 50 == 0 or stuck_counter > 0:
                status_callback(f"⚡ Bot menggulir... ({jumlah_sekarang} data termuat)")

        except Exception:
            pass

        time.sleep(random.uniform(0.7, 1.2))


# ======================================================================
# FUNGSI ANALITIK
# ======================================================================
def tentukan_fokus(teks):
    """Mengkategorikan ulasan ke dalam fokus area berdasarkan kata kunci."""
    teks_lower = str(teks).lower()
    kategori = []

    kw_admin = ['kasir', 'daftar', 'resepsionis', 'admin', 'pendaftaran', 'berkas', 'prosedur', 'telepon', 'cs']
    kw_medis = ['dokter', 'perawat', 'suster', 'bidan', 'ramah', 'kasar', 'arogan', 'jutek', 'sombong', 'tindak', 'medis', 'diagnosa', 'empati']
    kw_tat = ['lama', 'lambat', 'antri', 'nunggu', 'tunggu', 'jam', 'lelet', 'cepat']
    kw_fasilitas = ['kamar', 'ruang', 'parkir', 'bersih', 'toilet', 'fasilitas', 'gedung', 'ac', 'panas', 'bau', 'kotor', 'lift']
    kw_harga = ['mahal', 'murah', 'harga', 'biaya', 'tagihan', 'bayar', 'gratis']

    if any(kata in teks_lower for kata in kw_admin): kategori.append('Administrasi & Front Office')
    if any(kata in teks_lower for kata in kw_medis): kategori.append('Sikap Tenaga Medis')
    if any(kata in teks_lower for kata in kw_tat): kategori.append('Waktu Tunggu (TAT)')
    if any(kata in teks_lower for kata in kw_fasilitas): kategori.append('Fasilitas & Lingkungan')
    if any(kata in teks_lower for kata in kw_harga): kategori.append('Harga / Biaya')

    return ' & '.join(kategori) if kategori else 'Umum / Lainnya'


def deteksi_nps(rating_str):
    """Mengklasifikasikan rating menjadi Promotor / Pasif / Detraktor (standar NPS)."""
    try:
        rating_angka = float(rating_str.split()[0].replace(',', '.'))
    except Exception:
        rating_angka = 3.0

    if rating_angka >= 4:
        return "Promotor (Kekuatan)"
    elif rating_angka <= 2:
        return "Detraktor (Titik Lemah)"
    else:
        return "Pasif (Netral)"


def deteksi_tipe_pasien(teks):
    """Mendeteksi apakah pasien menggunakan BPJS, Asuransi, atau Umum berdasarkan isi ulasan."""
    teks_lower = str(teks).lower()
    if any(kata in teks_lower for kata in ['bpjs', 'kis', 'rujukan', 'pemerintah']):
        return 'BPJS'
    elif any(kata in teks_lower for kata in ['asuransi', 'inhealth', 'admedika', 'reimburse']):
        return 'Asuransi'
    else:
        return 'Umum / Tidak Disebutkan'


def konversi_ke_periode(tanggal_teks):
    """Mengkonversi teks waktu relatif (misal '2 bulan lalu') menjadi format MM-YYYY."""
    teks = str(tanggal_teks).lower()
    bulan_mundur = 0

    if any(x in teks for x in ['hari', 'minggu', 'detik', 'menit', 'jam', 'baru']):
        bulan_mundur = 0
    elif 'bulan' in teks:
        bulan_mundur = 1 if 'sebulan' in teks else int(re.search(r'\d+', teks).group()) if re.search(r'\d+', teks) else 0
    elif 'tahun' in teks:
        bulan_mundur = 12 if 'setahun' in teks else int(re.search(r'\d+', teks).group()) * 12 if re.search(r'\d+', teks) else 12

    sekarang = datetime.now()
    total_bulan_sekarang = (sekarang.year * 12) + sekarang.month
    total_bulan_target = total_bulan_sekarang - bulan_mundur
    target_tahun = total_bulan_target // 12
    target_bulan = total_bulan_target % 12
    if target_bulan == 0:
        target_tahun -= 1
        target_bulan = 12
    return f"{target_bulan:02d}-{target_tahun}"


# ======================================================================
# FUNGSI UTAMA SCRAPER
# ======================================================================
def full_batch_scraper(status_callback=print, wait_callback=None):
    """
    Menjalankan proses scraping ulasan Google Maps secara semi-manual.
    Bot membuka browser, menavigasi ke halaman RS, lalu menunggu pengguna
    mengklik tab 'Ulasan' dan mengurutkan 'Terbaru' secara manual.
    Setelah pengguna mengkonfirmasi, bot melakukan scroll otomatis
    dan mengekstrak data ulasan.
    """
    semua_hasil_scraping = []

    status_callback("Menyiapkan browser...")
    options = webdriver.ChromeOptions()
    options.add_argument('--lang=id')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()

    try:
        for nama_rs in daftar_rs:
            status_callback(f"\n==================================================")
            status_callback(f"🎯 TARGET SAAT INI: {nama_rs}")
            status_callback(f"==================================================")

            status_callback("🧭 Membuka Google Maps dan mencari rumah sakit...")
            url_pencarian = f"https://www.google.com/maps?q={urllib.parse.quote(nama_rs + ' Bekasi')}"
            driver.get(url_pencarian)
            time.sleep(5)

            # --- Mode Semi-Manual ---
            status_callback("💬 Mode Semi-Manual Diaktifkan.")
            status_callback(">>> TUGAS ANDA: Buka Chrome yang baru saja terbuka, klik tab 'Ulasan', lalu klik 'Terbaru'. <<<")

            if wait_callback:
                status_callback("⏳ Menunggu Anda berinteraksi dengan browser Google Maps...")
                status_callback("🔔 Setelah Anda menekan 'Terbaru' di Maps, klik tombol 'Lanjutkan' di sini.")
                wait_callback()
            else:
                input("Tekan ENTER di terminal jika Anda sudah menekan tab ulasan dan terbaru...")

            status_callback("🚀 Memulai pengguliran otomatis untuk mencari hingga 1000 ulasan...")
            fungsi_scroll_otomatis(driver, status_callback)

            status_callback("🔬 Mengekstrak isi ulasan...")

            # Klik tombol 'Selengkapnya' agar teks ulasan terbuka penuh
            try:
                driver.execute_script("document.querySelectorAll('button.w8nwRe').forEach(b => b.click());")
                time.sleep(random.uniform(1.2, 2.0))
            except Exception:
                pass

            # Ekstraksi data ulasan menggunakan JavaScript
            data_mentah = driver.execute_script("""
                let hasil = [];
                let reviews = document.querySelectorAll('.jftiEf');
                for(let item of reviews) {
                    try {
                        let nama = item.querySelector('.d4r55') ? item.querySelector('.d4r55').innerText : '';
                        let rating = item.querySelector('.kvMYJc') ? item.querySelector('.kvMYJc').getAttribute('aria-label') : '';
                        let tanggal = item.querySelector('.rsqaWe') ? item.querySelector('.rsqaWe').innerText : '';
                        let teks = item.querySelector('.MyEned .wiI7pd') ? item.querySelector('.MyEned .wiI7pd').innerText : '';

                        if(teks.trim() !== '') {
                            hasil.push({
                                'Nama Akun': nama,
                                'Rating Lengkap': rating,
                                'Tanggal Mentah': tanggal,
                                'Ulasan': teks
                            });
                        }
                    } catch(e) {}
                }
                return hasil;
            """)

            for baris in data_mentah:
                baris['Rumah Sakit'] = nama_rs
                semua_hasil_scraping.append(baris)

            status_callback(f"✅ Selesai mengekstrak {nama_rs}.")

        # --- Pengolahan Data Akhir ---
        status_callback("\nProses pengolahan data akhir dimulai...")
        if semua_hasil_scraping:
            df = pd.DataFrame(semua_hasil_scraping)
            df['Periode'] = df['Tanggal Mentah'].apply(konversi_ke_periode)
            df['Fokus Area'] = df['Ulasan'].apply(tentukan_fokus)
            df['Klasifikasi NPS'] = df['Rating Lengkap'].apply(deteksi_nps)
            df['Tipe Pasien'] = df['Ulasan'].apply(deteksi_tipe_pasien)

            df_final = df[['Rumah Sakit', 'Nama Akun', 'Periode', 'Rating Lengkap',
                           'Tipe Pasien', 'Fokus Area', 'Klasifikasi NPS', 'Ulasan']]

            # Batasi maksimal 1000 ulasan per rumah sakit
            hasil_sampling = []
            for rs_nama in df_final['Rumah Sakit'].unique():
                df_per_rs = df_final[df_final['Rumah Sakit'] == rs_nama]
                n_sample = min(len(df_per_rs), 1000)
                hasil_sampling.append(df_per_rs.head(n_sample))

            df_sampled = pd.concat(hasil_sampling).reset_index(drop=True)

            file_name = 'Data_Komparasi_RS_Bekasi.xlsx'
            df_sampled.to_excel(file_name, index=False)
            status_callback(f"🔥 BERHASIL! Total {len(df_sampled)} ulasan disimpan ke '{file_name}'.")

    finally:
        driver.quit()
        status_callback("Browser ditutup.")


if __name__ == "__main__":
    full_batch_scraper(print)