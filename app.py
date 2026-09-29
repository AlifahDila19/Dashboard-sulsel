import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman & Perbaikan CSS (Menyembunyikan Header Bawaan & Mengatur Jarak Judul)
st.set_page_config(page_title="Profil Ekonomi Sulsel", layout="wide")

st.markdown("""
    <style>
        /* Sembunyikan Header Bawaan Streamlit */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Jarak Atas Kontainer yang Pas Agar Judul Tidak Terpotong */
        .block-container {
            padding-top: 2.2rem !important;
            padding-bottom: 1rem !important;
            max-width: 95% !important;
        }
        
        /* Ukuran Judul Utama Rapi & Tidak Terpotong */
        h1 {
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: #1E293B !important;
            margin-top: 0rem !important;
            margin-bottom: 0.2rem !important;
            padding-top: 0rem !important;
            line-height: 1.3 !important;
        }
        h3 {
            font-size: 1.05rem !important;
            font-weight: 600 !important;
            color: #334155 !important;
            margin-top: 0.5rem !important;
            margin-bottom: 0.3rem !important;
        }
        hr {
            margin-top: 0.5rem !important;
            margin-bottom: 0.8rem !important;
        }
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.5rem !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Profil Ekonomi & Kesejahteraan Sulawesi Selatan")
st.caption("Sumber Data Resmi BPS Sulawesi Selatan (2021–2026)")
st.markdown("---")

# 2. LOAD DATASET
df_macro = pd.read_csv("dataset_macro_sulsel.csv")
df_sektor = pd.read_csv("dataset_sektor_sulsel.csv")

# Merapikan Label Sektor agar bertingkat
df_sektor_clean = df_sektor.copy()
label_map = {
    'Pertanian': 'Pertanian',
    'Industri Pengolahan': 'Industri<br>Pengolahan',
    'Perdagangan & Jasa': 'Perdagangan<br>& Jasa'
}
df_sektor_clean['Sektor_Label'] = df_sektor_clean['Sektor'].map(label_map).fillna(df_sektor_clean['Sektor'])

data_24_kab = {
    'Kabupaten_Kota': [
        'Bantaeng', 'Barru', 'Bone', 'Bulukumba', 'Enrekang', 'Gowa', 
        'Jeneponto', 'Kepulauan Selayar', 'Luwu', 'Luwu Timur', 'Luwu Utara', 
        'Maros', 'Pangkep', 'Pinrang', 'Sidrap', 'Sinjai', 
        'Soppeng', 'Takalar', 'Tana Toraja', 'Toraja Utara', 'Wajo', 
        'Makassar', 'Palopo', 'Parepare'
    ],
    'Angka_Kemiskinan_Pct': [
        8.9, 8.4, 10.5, 7.1, 12.1, 7.2, 
        13.8, 12.4, 12.3, 6.8, 13.2, 
        9.1, 13.9, 8.7, 5.1, 8.8, 
        7.5, 8.2, 11.9, 11.8, 6.9, 
        4.8, 5.2, 5.4
    ],
    'lat': [
        -5.5484, -4.4332, -4.5372, -5.5513, -3.5654, -5.3134,
        -5.5721, -6.1189, -3.0089, -2.5711, -2.3618,
        -5.0039, -4.7821, -3.7891, -3.9218, -5.2412,
        -4.3512, -5.4123, -3.0912, -2.9711, -4.1234,
        -5.1477, -2.9921, -4.0123
    ],
    'lon': [
        119.9503, 119.6231, 120.3283, 120.1927, 119.7712, 119.7431,
        119.7289, 120.4821, 120.2189, 121.2891, 120.3232,
        119.5721, 119.5512, 119.6489, 119.7891, 120.2489,
        119.8821, 119.4512, 119.8512, 119.8986, 120.0312,
        119.4327, 120.1912, 119.6289
    ]
}
df_spasial = pd.DataFrame(data_24_kab)

# 3. SIDEBAR FILTER & EXPORT
st.sidebar.header("Pengaturan Filter")
tahun_min = int(df_macro['Tahun'].min())
tahun_max = int(df_macro['Tahun'].max())
selected_years = st.sidebar.slider(
    "Pilih Periode Tahun:",
    min_value=tahun_min,
    max_value=tahun_max,
    value=(tahun_min, tahun_max)
)

list_kab = list(df_spasial['Kabupaten_Kota'].unique())
selected_kab = st.sidebar.multiselect(
    "Pilih Kabupaten / Kota:",
    options=list_kab,
    default=list_kab
)

# Filter Data
df_macro_filtered = df_macro[(df_macro['Tahun'] >= selected_years[0]) & (df_macro['Tahun'] <= selected_years[1])].copy()
df_spasial_filtered = df_spasial[df_spasial['Kabupaten_Kota'].isin(selected_kab)].copy() if selected_kab else df_spasial.copy()

latest_yr = df_macro_filtered.iloc[-1] if not df_macro_filtered.empty else df_macro.iloc[-1]

df_export = df_spasial_filtered[['Kabupaten_Kota', 'Angka_Kemiskinan_Pct']].copy()
df_export['Tahun_Acuan'] = int(latest_yr['Tahun'])
df_export['PDRB_Provinsi_Triliun'] = latest_yr['PDRB_ADHB_Triliun']
df_export['TPT_Provinsi_Pct'] = latest_yr['TPT_Pengangguran']
df_export['Pertumbuhan_Ekonomi_Provinsi_Pct'] = latest_yr['Pertumbuhan_Ekonomi']

csv_data = df_export.to_csv(index=False, sep=';', decimal=',').encode('utf-8-sig')

st.sidebar.markdown("---")
st.sidebar.subheader("Unduh Data")
st.sidebar.download_button(
    label="Unduh Data (Excel CSV)",
    data=csv_data,
    file_name="data_ekonomi_sulsel.csv",
    mime="text/csv"
)

# 4. KPI METRICS
c1, c2, c3 = st.columns(3)

c1.metric(
    label=f"PDRB ADHB ({int(latest_yr['Tahun'])})", 
    value=f"Rp {latest_yr['PDRB_ADHB_Triliun']:.1f} T", 
    delta=f"{latest_yr['Pertumbuhan_Ekonomi']:.2f}% YoY"
)

c2.metric(
    label="Tingkat Pengangguran (TPT)", 
    value=f"{latest_yr['TPT_Pengangguran']:.2f}%",
    delta="Tingkat Provinsi"
)

c3.metric(
    label="Tingkat Kemiskinan", 
    value=f"{latest_yr['Kemiskinan_Pct']:.2f}%",
    delta="Tingkat Provinsi",
    delta_color="inverse"
)

# INSIGHT EKSEKUTIF
rata_provinsi = float(latest_yr['Kemiskinan_Pct'])
max_kab = df_spasial_filtered.sort_values(by='Angka_Kemiskinan_Pct', ascending=False).iloc[0] if not df_spasial_filtered.empty else df_spasial.iloc[0]
min_kab = df_spasial_filtered.sort_values(by='Angka_Kemiskinan_Pct', ascending=True).iloc[0] if not df_spasial_filtered.empty else df_spasial.iloc[-1]

st.info(f"""
**Insight Eksekutif ({selected_years[0]}–{selected_years[1]}):**
Perekonomian Sulawesi Selatan tahun **{int(latest_yr['Tahun'])}** tumbuh **{latest_yr['Pertumbuhan_Ekonomi']:.2f}%** dengan PDRB **Rp {latest_yr['PDRB_ADHB_Triliun']:.1f} Triliun**. 
Rata-rata kemiskinan provinsi sebesar **{rata_provinsi:.2f}%**. Pada wilayah terfilter, kemiskinan tertinggi di **{max_kab['Kabupaten_Kota']} ({max_kab['Angka_Kemiskinan_Pct']}%)** dan terendah di **{min_kab['Kabupaten_Kota']} ({min_kab['Angka_Kemiskinan_Pct']}%)**.
""")

st.markdown("---")

# 5. TAB SYSTEM
tab1, tab2 = st.tabs(["Ringkasan Visual", "Tabel Data"])

with tab1:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Pertumbuhan Ekonomi vs Pengangguran")
        fig1 = px.line(
            df_macro_filtered, x='Tahun', y=['Pertumbuhan_Ekonomi', 'TPT_Pengangguran'], 
            markers=True,
            labels={'value': 'Persentase (%)', 'variable': 'Indikator', 'Pertumbuhan_Ekonomi': 'Pertumbuhan Ekonomi', 'TPT_Pengangguran': 'Pengangguran (TPT)'}
        )
        fig1.update_layout(template="plotly_white", height=280, margin=dict(l=10, r=10, t=25, b=10))
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("Kontribusi Sektor Ekonomi Utama")
        fig2 = px.bar(
            df_sektor_clean, x='Sektor_Label', y='PDRB_Miliar', color='Sektor_Label',
            text_auto='.2s',
            labels={'Sektor_Label': 'Sektor Ekonomi', 'PDRB_Miliar': 'PDRB (Miliar Rp)'}
        )
        fig2.update_layout(
            template="plotly_white", 
            height=280, 
            margin=dict(l=10, r=10, t=25, b=10), 
            showlegend=False,
            xaxis=dict(tickangle=0)
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    
    # DUA KOLOM SPASIAL
    col_map1, col_map2 = st.columns(2)

    with col_map1:
        st.subheader("Sebaran Kemiskinan di Peta Sulsel")
        
        fig_map = px.scatter_geo(
            df_spasial_filtered,
            lat='lat', lon='lon',
            color='Angka_Kemiskinan_Pct', size='Angka_Kemiskinan_Pct',
            hover_name='Kabupaten_Kota',
            hover_data={'lat': False, 'lon': False, 'Angka_Kemiskinan_Pct': ':.1f%'},
            color_continuous_scale='Reds',
            scope='world',
            labels={'Angka_Kemiskinan_Pct': 'Kemiskinan (%)'}
        )
        fig_map.update_traces(marker=dict(sizeref=0.5, sizemin=4))
        fig_map.update_geos(
            center=dict(lat=-3.8, lon=119.9),
            projection_scale=18,
            showland=True, landcolor="rgb(245, 245, 245)",
            showocean=True, oceancolor="rgb(230, 243, 255)",
            showcountries=False, showsubunits=True
        )
        fig_map.update_layout(
            template="plotly_white", 
            height=380,
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_map2:
        st.subheader("Peringkat Kemiskinan Kabupaten/Kota")
        fig3 = px.bar(
            df_spasial_filtered.sort_values(by='Angka_Kemiskinan_Pct', ascending=False), 
            x='Kabupaten_Kota', y='Angka_Kemiskinan_Pct', color='Angka_Kemiskinan_Pct',
            color_continuous_scale='Reds',
            text_auto='.1f',
            labels={'Angka_Kemiskinan_Pct': 'Kemiskinan (%)', 'Kabupaten_Kota': 'Wilayah'}
        )
        fig3.add_hline(
            y=rata_provinsi, 
            line_dash="dash", 
            line_color="darkred",
            annotation_text=f"Rata-rata Provinsi ({rata_provinsi:.2f}%)", 
            annotation_position="top right"
        )
        fig3.update_layout(
            template="plotly_white", 
            height=380,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False
        )
        st.plotly_chart(fig3, use_container_width=True)

    # 6. REKOMENDASI KEBIJAKAN DINAMIS
    st.markdown("---")
    st.subheader("Catatan & Rekomendasi Kebijakan")
    
    kab_tinggi = df_spasial_filtered[df_spasial_filtered['Angka_Kemiskinan_Pct'] > rata_provinsi]['Kabupaten_Kota'].tolist()
    teks_kab_tinggi = ", ".join(kab_tinggi) if kab_tinggi else "Tidak ada kabupaten terfilter yang berada di atas rata-rata provinsi."

    rec_col1, rec_col2 = st.columns(2)
    with rec_col1:
        st.success(f"""
        **1. Fokus Daerah Berisiko (Zona Merah Terfilter):**
        * Prioritas bantuan sosial dan infrastruktur pada daerah di atas rata-rata provinsi ({rata_provinsi:.2f}%): **{teks_kab_tinggi}**.
        """)
    with rec_col2:
        st.warning("""
        **2. Pengembangan Sektor Unggulan:**
        * Memperkuat hilirisasi pada sektor utama (**Perdagangan, Jasa, dan Pertanian**) untuk menjaga penyerapan tenaga kerja secara berkelanjutan.
        """)

with tab2:
    st.subheader("Data Kabupaten/Kota Terfilter")
    st.dataframe(df_export, use_container_width=True)
    
    st.subheader(f"Data Makro Provinsi ({selected_years[0]}–{selected_years[1]})")
    st.dataframe(df_macro_filtered, use_container_width=True)
