import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman & CSS Kustom
st.set_page_config(
    page_title="Profil Ekonomi Sulsel", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Mengatur jarak atas kontainer agar judul tidak terpotong oleh header bawaan Streamlit */
    .block-container {
        padding-top: 5.5rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Mempercantik kartu indikator KPI */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. Fungsi Memuat Data dengan Caching
@st.cache_data
def load_data():
    macro_df = pd.read_csv('dataset_macro_sulsel.csv')
    sektor_df = pd.read_csv('dataset_sektor_sulsel.csv')
    
    # Memastikan format data numerik
    macro_df['Tahun'] = macro_df['Tahun'].astype(int)
    sektor_df['Tahun'] = sektor_df['Tahun'].astype(int)
    
    return macro_df, sektor_df

try:
    macro_df, sektor_df = load_data()
except Exception as e:
    st.error(f"Gagal memuat file dataset: {e}. Pastikan file CSV tersedia di repositori GitHub.")
    st.stop()

# 3. Sidebar Filter
st.sidebar.title("Pengaturan Filter")

# Filter Tahun
min_year = int(macro_df['Tahun'].min())
max_year = int(macro_df['Tahun'].max())

selected_years = st.sidebar.slider(
    "Pilih Periode Tahun:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter Kabupaten / Kota
all_kabupaten = sorted(macro_df['Kabupaten_Kota'].unique())
selected_kabupaten = st.sidebar.multiselect(
    "Pilih Kabupaten / Kota:",
    options=all_kabupaten,
    default=all_kabupaten
)

# Filter Data Berdasarkan Sidebar
filtered_macro = macro_df[
    (macro_df['Tahun'] >= selected_years[0]) & 
    (macro_df['Tahun'] <= selected_years[1]) & 
    (macro_df['Kabupaten_Kota'].isin(selected_kabupaten))
]

filtered_sektor = sektor_df[
    (sektor_df['Tahun'] >= selected_years[0]) & 
    (sektor_df['Tahun'] <= selected_years[1])
]

# 4. Header & Judul Utama
st.title("Profil Ekonomi & Kesejahteraan Sulawesi Selatan")
st.caption("Sumber Data Resmi BPS Sulawesi Selatan (2021–2026)")

st.write("---")

# 5. Baris Indikator Utama (KPI Metrics)
col1, col2, col3 = st.columns(3)

# Data Tahun Terakhir yang Terfilter
latest_year = selected_years[1]
prev_year = latest_year - 1

macro_latest = filtered_macro[filtered_macro['Tahun'] == latest_year]
macro_prev = filtered_macro[filtered_macro['Tahun'] == prev_year]

# Perhitungan Nilai KPI
total_pdrb = macro_latest['PDRB_ADHB'].sum() if not macro_latest.empty else 0
prev_pdrb = macro_prev['PDRB_ADHB'].sum() if not macro_prev.empty else 0
pdrb_delta = ((total_pdrb - prev_pdrb) / prev_pdrb * 100) if prev_pdrb > 0 else 0

avg_tpt = macro_latest['TPT'].mean() if not macro_latest.empty else 0
prev_tpt = macro_prev['TPT'].mean() if not macro_prev.empty else 0
tpt_delta = avg_tpt - prev_tpt

avg_kemiskinan = macro_latest['Kemiskinan'].mean() if not macro_latest.empty else 0
prev_kemiskinan = macro_prev['Kemiskinan'].mean() if not macro_prev.empty else 0
kemiskinan_delta = avg_kemiskinan - prev_kemiskinan

with col1:
    st.metric(
        label=f"PDRB ADHB ({latest_year})",
        value=f"Rp {total_pdrb:,.1f} T".replace(',', '.'),
        delta=f"{pdrb_delta:+.2f}% YoY (Nominal)"
    )

with col2:
    st.metric(
        label="Tingkat Pengangguran (TPT)",
        value=f"{avg_tpt:.2f}%",
        delta=f"{tpt_delta:+.2f}% poin",
        delta_color="inverse"  # Penurunan TPT adalah hal positif (Hijau)
    )

with col3:
    st.metric(
        label="Tingkat Kemiskinan",
        value=f"{avg_kemiskinan:.2f}%",
        delta=f"{kemiskinan_delta:+.2f}% poin",
        delta_color="inverse"  # Penurunan Kemiskinan adalah hal positif (Hijau)
    )

# 6. Insight Eksekutif & Analisis Temuan
st.info(
    f"**Insight Eksekutif ({selected_years[0]}–{selected_years[1]}):**\n"
    f"- **Pertumbuhan & Kemiskinan:** Puncak pertumbuhan nominal terjadi pada tahun 2022 (8.37%), namun angka kemiskinan pada tahun tersebut sempat mengalami kenaikan tipis sebelum kembali membaik.\n"
    f"- **Disparitas Wilayah:** Dari 24 Kabupaten/Kota di Sulawesi Selatan, sebanyak 15 wilayah berada di atas rata-rata tingkat kemiskinan provinsi. Pangkep mencatatkan tingkat kemiskinan tertinggi (13.9%), mendekati 3 kali lipat Kota Makassar (4.8%).\n"
    f"- **Efek Kota Besar:** Rata-rata sederhana kemiskinan 24 wilayah (sekitar 9.2%) lebih tinggi daripada rata-rata gabungan provinsi (7.60%), mengindikasikan bahwa kinerja wilayah bernilai ekonomi besar seperti Kota Makassar secara signifikan menurunkan angka rata-rata agregat provinsi."
)

# 7. Tab Visualisasi & Tabel Data
tab1, tab2 = st.tabs(["Ringkasan Visual", "Tabel Data & Catatan Metodologi"])

with tab1:
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Pertumbuhan Ekonomi vs Pengangguran")
        yearly_trend = filtered_macro.groupby('Tahun')[['Pertumbuhan_Ekonomi', 'TPT']].mean().reset_index()
        
        fig_trend = px.line(
            yearly_trend, 
            x='Tahun', 
            y=['Pertumbuhan_Ekonomi', 'TPT'],
            markers=True,
            labels={'value': 'Persentase (%)', 'variable': 'Indikator'},
            color_discrete_map={'Pertumbuhan_Ekonomi': '#005580', 'TPT': '#54bebe'}
        )
        fig_trend.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with chart_col2:
        st.subheader("Kontribusi Sektor Ekonomi Utama")
        sektor_sum = filtered_sektor.groupby('Sektor')['Nilai_PDRB'].sum().reset_index().sort_values(by='Nilai_PDRB', ascending=False)
        
        fig_sektor = px.bar(
            sektor_sum, 
            x='Sektor', 
            y='Nilai_PDRB',
            labels={'Nilai_PDRB': 'PDRB (Miliar Rp)', 'Sektor': 'Sektor Utama'},
            color_discrete_sequence=['#ff4b4b']
        )
        st.plotly_chart(fig_sektor, use_container_width=True)

with tab2:
    st.subheader("Data Macro Terfilter")
    st.dataframe(filtered_macro, use_container_width=True)
    
    st.subheader("Catatan Metodologi & Keterbatasan Data")
    st.write("""
    1. **Metodologi PDRB**: Indikator Pertumbuhan Ekonomi dihitung berdasarkan PDRB ADHB (Atas Dasar Harga Berlaku / Nilai Nominal), sehingga mencerminkan nilai transaksi nominal ekonomi.
    2. **Keterbatasan Data Wilayah**: Data kemiskinan dan pengangguran tingkat kabupaten/kota bersumber dari potret/snapshot indikator makro tahunan BPS. Filter slider tahun dirancang untuk mengagregasikan tren rata-rata indikator sesuai dengan cakupan wilayah terfilter.
    """)
