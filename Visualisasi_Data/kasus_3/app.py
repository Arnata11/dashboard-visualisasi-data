from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATASET_PATH = Path(__file__).with_name("dataset_cuaca.csv")
SUHU = "Suhu (°C)"
KELEMBABAN = "Kelembaban (%)"

st.set_page_config(page_title="Pengamatan Cuaca", page_icon="🌦️", layout="wide")
st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem;}
    [data-testid="stMetric"] {
        background-color: #F8FAFC !important;
        border: 1px solid #CBD5E1;
        border-radius: 12px;
        padding: 12px;
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricDelta"],
    [data-testid="stMetricDelta"] div {
        color: #0F172A !important;
        opacity: 1 !important;
    }
    [data-testid="stMetricLabel"] svg,
    [data-testid="stMetricDelta"] svg {
        fill: #0F172A !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    data = pd.read_csv(DATASET_PATH)
    data[SUHU] = pd.to_numeric(data[SUHU], errors="coerce")
    data[KELEMBABAN] = pd.to_numeric(data[KELEMBABAN], errors="coerce")
    return data.dropna(subset=["Kota", SUHU, KELEMBABAN, "Kondisi"])


try:
    df = load_data()
except FileNotFoundError:
    st.error("Dataset belum tersedia. Jalankan `python analisis_data.py` terlebih dahulu.")
    st.stop()

with st.sidebar:
    st.title("🌦️ Pengamatan Cuaca")
    st.caption("Analisis kota, kondisi, suhu, dan kelembaban")
    st.divider()
    cities = st.multiselect("Kota", sorted(df["Kota"].unique()), default=sorted(df["Kota"].unique()))
    conditions = st.multiselect("Kondisi", sorted(df["Kondisi"].unique()), default=sorted(df["Kondisi"].unique()))
    suhu_range = st.slider("Rentang suhu (°C)", float(df[SUHU].min()), float(df[SUHU].max()), (float(df[SUHU].min()), float(df[SUHU].max())), 0.1)
    humidity_range = st.slider("Rentang kelembaban (%)", 0.0, 100.0, (float(df[KELEMBABAN].min()), float(df[KELEMBABAN].max())), 0.1)
    st.divider()
    st.caption("Disusun oleh")
    st.markdown("**Arwan Priyadinata**")
    st.caption("Manajemen Informatika")

filtered = df.loc[
    df["Kota"].isin(cities) & df["Kondisi"].isin(conditions)
    & df[SUHU].between(*suhu_range) & df[KELEMBABAN].between(*humidity_range)
].copy()

st.title("Dashboard Pengamatan Cuaca")
st.markdown("Bedah Kasus 3: membandingkan kondisi cuaca, suhu, dan kelembaban antar kota.")
st.caption("Data sintetis untuk pembelajaran, bukan pengamatan cuaca aktual.")

if filtered.empty:
    st.warning("Tidak ada pengamatan yang cocok. Ubah pilihan filter di sidebar.")
    st.stop()

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Total Pengamatan", f"{len(filtered):,}")
metric_2.metric("Rata-rata Suhu", f"{filtered[SUHU].mean():.1f} °C")
metric_3.metric("Rata-rata Kelembaban", f"{filtered[KELEMBABAN].mean():.1f}%")
metric_4.metric("Kondisi Terbanyak", filtered["Kondisi"].mode().iloc[0])

tab_summary, tab_numeric, tab_detail = st.tabs(["Ringkasan", "Suhu & Kelembaban", "Data Pengamatan"])

with tab_summary:
    st.subheader("Ringkasan Pengamatan")
    st.write(f"Terdapat **{len(filtered):,} pengamatan** dari **{filtered['Kota'].nunique()} kota**. Suhu berkisar antara **{filtered[SUHU].min():.1f} °C** dan **{filtered[SUHU].max():.1f} °C**, sedangkan kelembaban berkisar **{filtered[KELEMBABAN].min():.1f}% sampai {filtered[KELEMBABAN].max():.1f}%**.")
    left, right = st.columns(2)
    with left:
        city_counts = filtered["Kota"].value_counts().rename_axis("Kota").reset_index(name="Jumlah")
        st.plotly_chart(px.bar(city_counts, x="Kota", y="Jumlah", text_auto=True, title="Jumlah Pengamatan per Kota", color="Kota", template="plotly_white"), use_container_width=True)
    with right:
        condition_counts = filtered["Kondisi"].value_counts().rename_axis("Kondisi").reset_index(name="Jumlah")
        st.plotly_chart(px.pie(condition_counts, names="Kondisi", values="Jumlah", hole=0.5, title="Komposisi Kondisi Cuaca"), use_container_width=True)
    summary = filtered.groupby("Kota", as_index=False).agg(
        Pengamatan=("Kota", "size"), Rata_Suhu=(SUHU, "mean"), Rata_Kelembaban=(KELEMBABAN, "mean")
    ).round(2)
    st.dataframe(summary, use_container_width=True, hide_index=True)
    st.info("Kota dan kondisi adalah data nominal. Suhu Celsius merupakan skala interval: 20 °C bukan dua kali lebih panas dari 10 °C. Kelembaban memiliki skala rasio dan nol absolut.")

with tab_numeric:
    variable = st.radio("Variabel yang dianalisis", [SUHU, KELEMBABAN], horizontal=True)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(px.histogram(filtered, x=variable, nbins=25, title=f"Distribusi {variable}", color_discrete_sequence=["#2563EB"], template="plotly_white"), use_container_width=True)
    with right:
        st.plotly_chart(px.box(filtered, x="Kota", y=variable, color="Kota", points="outliers", title=f"Sebaran {variable} per Kota", template="plotly_white"), use_container_width=True)
    st.plotly_chart(px.scatter(filtered, x=SUHU, y=KELEMBABAN, color="Kondisi", hover_data=["Kota"], opacity=0.6, title="Hubungan Suhu dan Kelembaban", template="plotly_white"), use_container_width=True)
    st.caption("Titik di luar whisker box plot adalah calon outlier, bukan otomatis kesalahan data. Hubungan suhu dan kelembaban pada grafik bukan bukti sebab-akibat.")

with tab_detail:
    st.caption(f"Menampilkan {len(filtered):,} pengamatan sesuai filter.")
    st.dataframe(filtered.sort_values(["Kota", "Kondisi"]), use_container_width=True, hide_index=True)
    st.download_button("Unduh data terfilter (CSV)", filtered.to_csv(index=False).encode("utf-8"), "pengamatan_cuaca_terfilter.csv", "text/csv")
