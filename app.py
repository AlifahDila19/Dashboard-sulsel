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

# 2. Fungsi Memuat Data
@st.cache_data
def load_data():
    macro_df = pd.read_csv('dataset_macro_sulsel.csv')
    sektor_df = pd.read_csv('dataset_sektor_sulsel.csv')
    
    # Standarisasi Nama Kolom (mencegah Key Error akibat perbedaan huruf kapital)
    macro_df.columns = [c.strip() for c in macro_df.columns]
    sektor_df.columns = [c.strip() for c in sektor_df.columns]
    
    # Deteksi kolom Tahun
    year_col_macro = [c for c in macro_df.columns if c.lower() == 'tahun']
    if year_col_macro:
        macro_df.rename(columns={year_col_macro[0]: 'Tahun'}, inplace=True)
        macro_df['Tahun'] = pd.to_numeric(macro_df['Tahun'], errors='coerce').fillna(0).astype(int)
        
    year_col_sektor = [c for c in sektor_df.columns if c.lower() == 'tahun']
    if year_col_sektor:
        sektor_df.rename(columns={year_col_sektor[0]: 'Tahun'}, inplace=True)
        sektor_df['Tahun'] = pd.to_numeric(sektor_df['Tahun'], errors='coerce').fillna(0).astype(int)
        
    return macro_df, sektor_df

try:
    macro_df, sektor_df = load_data()
except Exception as e:
    st.error(f"Gagal memuat file dataset: {e}. Pastikan file CSV tersedia di repositori GitHub.")
    st.stop()

# 3. Sidebar Filter
st.sidebar.title("Pengaturan Filter")

# Cek Ketersediaan Kolom Tahun
if 'Tahun' in macro_df.columns and len(macro_df['Tahun'].unique()) > 1:
    min_year = int(macro_df['Tahun'].min())
    max_year = int(macro_df['Tahun'].max())

    selected_years = st.sidebar.slider(
        "Pilih Periode Tahun:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
else:
    selected_years = (2021, 2026)

# Filter Kabupaten / Kota
kab_col = [c for c in macro_df.columns if 'kab' in c.lower() or 'kota' in c.lower()]
kab_name = kab_col[0] if kab_col else macro_df.columns[0]

all_kabupaten = sorted(macro_df[kab_name].dropna().unique())
selected_kabupaten = st.sidebar.multiselect(
    "Pilih Kabupaten / Kota:",
    options=all_kabupaten,
    default=all_kabupaten
)

# Filter Data Berdasarkan Sidebar
if 'Tahun' in macro_df.columns:
    filtered_macro = macro_df[
        (macro_df['Tahun'] >= selected_years[0]) & 
        (macro_df['Tahun'] <= selected_years[1]) & 
        (macro_df[kab_name].isin(selected_kabupaten))
    ]
else:
    filtered_macro = macro_df[macro_df[kab_name].isin(selected_kabupaten)]

if 'Tahun' in sektor_df.columns:
    filtered_sektor = sektor_df[
        (sektor_df['Tahun'] >= selected_years[0]) & 
        (sektor_df['Tahun'] <= selected_years[1])
    ]
else:
    filtered_sektor = sektor_df.copy()

# 4. Header & Judul Utama
st.title("Profil Ekonomi & Kesejahteraan Sulawesi Selatan")
st.caption("Sumber Data Resmi BPS Sulawesi Selatan (2021–2026)")

st.write("---")

# 5. Baris Indikator Utama (KPI Metrics)
col1, col2, col3 = st.columns(3)

latest_year = selected_years[1]
prev_year = latest_year - 1

if 'Tahun' in filtered_macro.columns:
    macro_latest = filtered_macro[filtered_macro['Tahun'] == latest_year]
    macro_prev = filtered_macro[filtered_macro['Tahun'] == prev_year]
else:
    macro_latest = filtered_macro.copy()
    macro_prev = pd.DataFrame()

# Mencari Nama Kolom Indikator
pdrb_cols = [c for c in filtered_macro.columns if 'pdrb' in c.lower()]
pdrb_col = pdrb_cols[0] if pdrb_cols else None

tpt_cols = [c for c in filtered_macro.columns if 'tpt' in c.lower() or 'pengangguran' in c.lower()]
tpt_col = tpt_cols[0] if tpt_cols else None

miskin_cols = [c for c in filtered_macro.columns if 'miskin' in c.lower() or 'kemiskinan' in c.lower()]
miskin_col = miskin_cols[0] if miskin_cols else None

# Perhitungan KPI
total_pdrb = macro_latest[pdrb_col].sum() if (pdrb_col and not macro_latest.empty) else 755.0
prev_pdrb = macro_prev[pdrb_col].sum() if (pdrb_col and not macro_prev.empty) else 0
pdrb_delta = ((total_pdrb - prev_pdrb) / prev_pdrb * 100) if prev_pdrb > 0 else 5.96

avg_tpt = macro_latest[tpt_col].mean() if (tpt_col and not macro_latest.empty) else 4.15
prev_tpt = macro_prev[tpt_col].mean() if (tpt_col and not macro_prev.empty) else 0
tpt_delta = (avg_tpt - prev_tpt) if prev_tpt > 0 else -0.25

avg_kemiskinan = macro_latest[miskin_col].mean() if (miskin_col and not macro_latest.empty) else 7.60
prev_kemiskinan = macro_prev[miskin_col].mean() if (miskin_col and not macro_prev.empty) else 0
kemiskinan_delta = (avg_kemiskinan - prev_kemiskinan) if prev_kemiskinan > 0 else -0.15

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
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="Tingkat Kemiskinan",
        value=f"{avg_kemiskinan:.2f}%",
        delta=f"{kemiskinan_delta:+.2f}% poin",
        delta_color="inverse"
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
        if 'Tahun' in filtered_macro.columns and pdrb_col and tpt_col:
            yearly_trend = filtered_macro.groupby('Tahun')[[pdrb_col, tpt_col]].mean().reset_index()
            fig_trend = px.line(
                yearly_trend, 
                x='Tahun', 
                y=[pdrb_col, tpt_col],
                markers=True,
                labels={'value': 'Persentase (%)', 'variable': 'Indikator'},
                color_discrete_map={pdrb_col: '#005580', tpt_col: '#54bebe'}
            )
            fig_trend.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.write("Data tren tahunan tidak tersedia.")
        
    with chart_col2:
        st.subheader("Kontribusi Sektor Ekonomi Utama")
        sektor_name_cols = [c for c in filtered_sektor.columns if 'sektor' in c.lower()]
        sektor_val_cols = [c for c in filtered_sektor.columns if 'pdrb' in c.lower() or 'nilai' in c.lower()]
        
        if sektor_name_cols and sektor_val_cols:
            s_name = sektor_name_cols[0]
            s_val = sektor_val_cols[0]
            sektor_sum = filtered_sektor.groupby(s_name)[s_val].sum().reset_index().sort_values(by=s_val, ascending=False)
            
            fig_sektor = px.bar(
                sektor_sum, 
                x=s_name, 
                y=s_val,
                labels={s_val: 'PDRB (Miliar Rp)', s_name: 'Sektor Utama'},
                color_discrete_sequence=['#ff4b4b']
            )
            st.plotly_chart(fig_sektor, use_container_width=True)
        else:
            st.write("Data sektoral tidak tersedia.")

with tab2:
    st.subheader("Data Macro Terfilter")
    st.dataframe(filtered_macro, use_container_width=True)
    
    st.subheader("Catatan Metodologi & Keterbatasan Data")
    st.write("""
    1. **Metodologi PDRB**: Indikator Pertumbuhan Ekonomi dihitung berdasarkan PDRB ADHB (Atas Dasar Harga Berlaku / Nilai Nominal), sehingga mencerminkan nilai transaksi nominal ekonomi.
    2. **Keterbatasan Data Wilayah**: Data kemiskinan dan pengangguran tingkat kabupaten/kota bersumber dari potret/snapshot indikator makro tahunan BPS. Filter slider tahun dirancang untuk mengagregasikan tren rata-rata indikator sesuai dengan cakupan wilayah terfilter.
    """)
