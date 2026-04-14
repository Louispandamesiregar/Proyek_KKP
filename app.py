import streamlit as st
import pandas as pd
import os
import threading
import time
import plotly.express as px
from scraper import full_batch_scraper

# Konfigurasi halaman utama Streamlit
st.set_page_config(page_title="RS Analytics", page_icon="🏥", layout="wide")

# ======================================================================
# MANAJEMEN STATE GLOBAL UNTUK SCRAPER
# Menggunakan cache_resource agar state tetap bertahan antar interaksi
# ======================================================================
@st.cache_resource
def get_scraper_state():
    return {
        "is_running": False,
        "completed": False,
        "waiting_for_user": False,
        "logs": [],
        "wait_event": threading.Event()
    }

scraper_state = get_scraper_state()

def scraper_logger(msg):
    """Menerima pesan log dari scraper dan menyimpannya ke state global."""
    scraper_state["logs"].append(msg)
    if len(scraper_state["logs"]) > 200:
        scraper_state["logs"].pop(0)

def minta_lanjut_dari_pengguna():
    """Mem-pause thread scraper sampai pengguna menekan tombol Lanjutkan di UI."""
    scraper_state["waiting_for_user"] = True
    scraper_state["wait_event"].wait()
    scraper_state["wait_event"].clear()
    scraper_state["waiting_for_user"] = False

def jalankan_scraper():
    """Fungsi utama scraper yang dijalankan di thread terpisah."""
    scraper_state["is_running"] = True
    scraper_state["completed"] = False
    scraper_state["waiting_for_user"] = False
    scraper_state["logs"] = []

    scraper_logger("Menyiapkan bot scraper Google Maps...")
    try:
        full_batch_scraper(
            status_callback=scraper_logger,
            wait_callback=minta_lanjut_dari_pengguna
        )
        scraper_logger("✅ Proses scraper selesai dan data telah disimpan!")
    except Exception as e:
        scraper_logger(f"❌ Terjadi Error: {str(e)}")
    finally:
        scraper_state["is_running"] = False
        scraper_state["completed"] = True

# ======================================================================
# SIDEBAR NAVIGASI
# ======================================================================
st.sidebar.title("🏥 RS Analytics")
st.sidebar.markdown("Sistem Analisis Sentimen Rumah Sakit")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navigasi", ["Dashboard Visualisasi", "Control Panel Scraper"])

# ======================================================================
# HALAMAN 1: DASHBOARD VISUALISASI DATA
# ======================================================================
if menu == "Dashboard Visualisasi":
    st.title("📊 Dashboard Visualisasi Data")

    # CSS kustom untuk kartu metrik KPI
    st.markdown("""
        <style>
        .metric-card {
            background-color: #1e1e1e;
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            border: 1px solid #333;
            margin-bottom: 20px;
        }
        .metric-title {
            font-size: 14px;
            color: #bdc3c7;
            text-transform: uppercase;
            font-weight: bold;
            letter-spacing: 1px;
        }
        .metric-value {
            font-size: 38px;
            font-weight: 800;
            margin: 10px 0;
            color: #ffffff;
        }
        .val-green { color: #2ecc71; }
        .val-yellow { color: #f1c40f; }
        .val-red { color: #e74c3c; }
        </style>
    """, unsafe_allow_html=True)

    file_path = 'Data_Komparasi_RS_Bekasi.xlsx'

    if not os.path.exists(file_path):
        st.warning("⚠️ Data belum tersedia. Silakan jalankan scraper terlebih dahulu di menu 'Control Panel Scraper'.")
    else:
        df = pd.read_excel(file_path)

        # --- Pilihan Rumah Sakit ---
        daftar_rs = df['Rumah Sakit'].unique().tolist()
        rs_pilihan = st.selectbox("🏗️ Pilih Rumah Sakit untuk Dianalisis:", daftar_rs, index=0)

        # --- Data Khusus Rumah Sakit Pilihan ---
        df_pilihan = df[df['Rumah Sakit'] == rs_pilihan]

        total_ulasan = len(df_pilihan)
        promotor = len(df_pilihan[df_pilihan['Klasifikasi NPS'] == 'Promotor (Kekuatan)'])
        pasif = len(df_pilihan[df_pilihan['Klasifikasi NPS'] == 'Pasif (Netral)'])
        detraktor = len(df_pilihan[df_pilihan['Klasifikasi NPS'] == 'Detraktor (Titik Lemah)'])

        # Hitung NPS Score
        nps_score = 0
        if total_ulasan > 0:
            nps_score = round(((promotor / total_ulasan) - (detraktor / total_ulasan)) * 100)

        # --- Kartu Metrik KPI ---
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Total Ulasan</div><div class="metric-value">{total_ulasan}</div></div>', unsafe_allow_html=True)
        with col2:
            nps_color = "#2ecc71" if nps_score > 0 else "#e74c3c" if nps_score < 0 else "#f1c40f"
            st.markdown(f'<div class="metric-card"><div class="metric-title">Skor NPS</div><div class="metric-value" style="color: {nps_color};">{nps_score}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Promotor</div><div class="metric-value val-green">{promotor}</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Pasif</div><div class="metric-value val-yellow">{pasif}</div></div>', unsafe_allow_html=True)
        with col5:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Detraktor</div><div class="metric-value val-red">{detraktor}</div></div>', unsafe_allow_html=True)

        st.write("")
        st.markdown("---")
        st.write("")

        # --- Baris Grafik 1: Pie Chart + Bar Chart ---
        c_chart1, c_chart2 = st.columns([1, 1.5])

        with c_chart1:
            st.subheader("Distribusi Area Titik Lemah (Detraktor)")
            df_lemah = df_pilihan[df_pilihan['Klasifikasi NPS'] == 'Detraktor (Titik Lemah)']
            if not df_lemah.empty:
                pie_fig = px.pie(
                    df_lemah, names='Fokus Area', hole=0.45,
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                pie_fig.update_traces(textposition='inside', textinfo='percent+label')
                pie_fig.update_layout(
                    margin=dict(t=20, b=20, l=0, r=0),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                )
                st.plotly_chart(pie_fig, width='stretch')
            else:
                st.info("Tidak ada data detraktor ditemukan.")

        with c_chart2:
            st.subheader("Tingkat Kepuasan Berdasarkan Tipe Pasien")
            pivot_pasien = pd.crosstab(df_pilihan['Tipe Pasien'], df_pilihan['Klasifikasi NPS'])
            for kolom in ['Promotor (Kekuatan)', 'Pasif (Netral)', 'Detraktor (Titik Lemah)']:
                if kolom not in pivot_pasien.columns:
                    pivot_pasien[kolom] = 0

            pivot_reset = pivot_pasien.reset_index()
            df_melt = pivot_reset.melt(
                id_vars=['Tipe Pasien'],
                value_vars=['Promotor (Kekuatan)', 'Pasif (Netral)', 'Detraktor (Titik Lemah)'],
                var_name='Klasifikasi', value_name='Jumlah'
            )

            bar_fig = px.bar(
                df_melt, x='Tipe Pasien', y='Jumlah', color='Klasifikasi',
                color_discrete_map={
                    'Promotor (Kekuatan)': '#2ecc71',
                    'Pasif (Netral)': '#f1c40f',
                    'Detraktor (Titik Lemah)': '#e74c3c'
                }, text_auto=True
            )
            bar_fig.update_layout(
                margin=dict(t=20, b=20, l=0, r=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="", yaxis_title="Total Ulasan"
            )
            st.plotly_chart(bar_fig, width='stretch')

        st.write("")
        st.markdown("---")
        st.write("")

        # --- Grafik Komparasi Head-to-Head Antar RS ---
        st.subheader("Komparasi Titik Lemah Antar RS (Berdasarkan Persentase Keluhan)")

        df_semua_lemah = df[df['Klasifikasi NPS'] == 'Detraktor (Titik Lemah)']
        total_per_rs = df['Rumah Sakit'].value_counts().to_dict()
        pivot_kelemahan = pd.crosstab(df_semua_lemah['Fokus Area'], df_semua_lemah['Rumah Sakit'])

        komparasi_data = []
        daftar_rs_lengkap = [
            'Primaya Hospital Bekasi Barat',
            'RSUD dr. Chasbullah Abdulmadjid',
            'RS Hermina Bekasi'
        ]

        for rs in daftar_rs_lengkap:
            if rs in pivot_kelemahan.columns:
                total_rs = total_per_rs.get(rs, 1)
                for area in pivot_kelemahan.index:
                    persen = round((pivot_kelemahan.at[area, rs] / total_rs) * 100, 1)
                    komparasi_data.append({
                        "Rumah Sakit": rs, "Fokus Area": area, "Persentase (%)": persen
                    })

        if komparasi_data:
            df_comp = pd.DataFrame(komparasi_data)
            comp_fig = px.bar(
                df_comp, x="Fokus Area", y="Persentase (%)",
                color="Rumah Sakit", barmode="group", text_auto='.1f'
            )
            comp_fig.update_layout(
                margin=dict(t=30, b=20, l=0, r=0),
                plot_bgcolor='rgba(0,0,0,0.02)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="", yaxis_title="Persentase Keluhan (%)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(comp_fig, width='stretch')
        else:
            st.info("Belum cukup data untuk komparasi persentase titik lemah.")

        st.markdown("---")

        # --- Tabel Detail Ulasan ---
        st.subheader("Tabel Peta Kekuatan & Detail Titik Lemah")

        # Fungsi untuk merender tabel HTML dengan teks ulasan lengkap
        def render_tabel_ulasan(dataframe):
            if dataframe.empty:
                st.info("Tidak ada data untuk ditampilkan.")
                return

            baris_html = ""
            for _, row in dataframe.iterrows():
                baris_html += f"""<tr>
                    <td>{row.get('Periode','')}</td>
                    <td>{row.get('Nama Akun','')}</td>
                    <td>{row.get('Tipe Pasien','')}</td>
                    <td>{row.get('Fokus Area','')}</td>
                    <td class="kolom-ulasan">{row.get('Ulasan','')}</td>
                </tr>"""

            html_lengkap = f"""
            <style>
            .tabel-ulasan {{
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
                font-family: sans-serif;
            }}
            .tabel-ulasan th {{
                background-color: #2c3e50;
                color: white;
                padding: 10px 12px;
                text-align: left;
                border: 1px solid #444;
                position: sticky;
                top: 0;
                z-index: 1;
            }}
            .tabel-ulasan td {{
                padding: 10px 12px;
                border: 1px solid #ddd;
                vertical-align: top;
                color: #333;
            }}
            .tabel-ulasan td.kolom-ulasan {{
                max-width: 550px;
                white-space: normal;
                word-wrap: break-word;
                line-height: 1.6;
            }}
            .tabel-ulasan tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .tabel-ulasan tr:hover {{
                background-color: #eef2f7;
            }}
            </style>
            <div style="max-height: 500px; overflow-y: auto; border: 1px solid #ddd; border-radius: 8px;">
            <table class="tabel-ulasan">
            <thead><tr>
                <th>Periode</th><th>Nama Akun</th><th>Tipe Pasien</th><th>Fokus Area</th><th>Ulasan</th>
            </tr></thead>
            <tbody>{baris_html}</tbody>
            </table></div>
            """
            st.components.v1.html(html_lengkap, height=520, scrolling=True)

        pilihan_tabel = st.radio(
            "Tampilkan tabel:", 
            ["Detail Keluhan (Titik Lemah)", "Peta Kekuatan (Promotor)"],
            horizontal=True
        )

        if pilihan_tabel == "Detail Keluhan (Titik Lemah)":
            render_tabel_ulasan(df_lemah[['Periode', 'Nama Akun', 'Tipe Pasien', 'Fokus Area', 'Ulasan']])
        else:
            df_kuat = df_pilihan[df_pilihan['Klasifikasi NPS'] == 'Promotor (Kekuatan)']
            render_tabel_ulasan(df_kuat[['Periode', 'Nama Akun', 'Tipe Pasien', 'Fokus Area', 'Ulasan']])


# ======================================================================
# HALAMAN 2: CONTROL PANEL SCRAPER
# ======================================================================
elif menu == "Control Panel Scraper":
    st.title("🤖 Control Panel Scraper")
    st.write("Jalankan bot untuk mengambil data ulasan terbaru dari Google Maps, lalu dirangkum ke dalam file Excel secara otomatis.")

    st.markdown("---")

    # Area indikator status dan tombol aksi
    col_btn, col_status = st.columns([1, 3])

    with col_status:
        if scraper_state["waiting_for_user"]:
            st.warning("⏳ Status: Menunggu interaksi manual Anda di browser Chrome.")
        elif scraper_state["is_running"]:
            st.info("🔄 Status: Sedang Berjalan (Memproses Data...)")
        elif scraper_state["completed"]:
            st.success("✅ Status: Selesai!")
        else:
            st.write("💤 Status: Idle (Siap Dijalankan)")

    with col_btn:
        if scraper_state["waiting_for_user"]:
            if st.button("Lanjutkan (Scroll)", type="primary"):
                scraper_state["wait_event"].set()
                st.rerun()
        elif scraper_state["is_running"]:
            st.button("Sedang Berjalan...", disabled=True)
        else:
            if st.button("▶️ Mulai Scraping", type="primary"):
                scraper_state["wait_event"].clear()
                thread = threading.Thread(target=jalankan_scraper)
                thread.start()
                st.rerun()

    st.markdown("### Terminal Log")

    # Styling kotak terminal log
    st.markdown("""
        <style>
        .terminal {
            background-color: #1e1e1e;
            color: #00ff00;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            height: 400px;
            overflow-y: auto;
            border: 1px solid #444;
        }
        </style>
    """, unsafe_allow_html=True)

    log_text = "<br>".join([f"&gt; {msg}" for msg in scraper_state["logs"]])
    if not log_text:
        log_text = "&gt; Menunggu perintah..."

    st.markdown(f'<div class="terminal">{log_text}</div>', unsafe_allow_html=True)

    # Auto-refresh selama scraper aktif (polling setiap 1.5 detik)
    if scraper_state["is_running"] or scraper_state["waiting_for_user"]:
        time.sleep(1.5)
        st.rerun()