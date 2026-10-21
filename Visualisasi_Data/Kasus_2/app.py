from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATASET_PATH = Path(__file__).with_name("dataset_mahasiswa.csv")

st.set_page_config(page_title="Profil Mahasiswa", page_icon="🎓", layout="wide")
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
    data["Semester"] = pd.to_numeric(data["Semester"], errors="coerce").astype("Int64")
    data["IPK"] = pd.to_numeric(data["IPK"], errors="coerce")
    data["Usia"] = pd.to_numeric(data["Usia"], errors="coerce")
    return data.dropna(subset=["Jurusan", "Semester", "IPK", "Usia"])


def format_number(value):
    return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


try:
    df = load_data()
except FileNotFoundError:
    st.error("Dataset belum tersedia. Jalankan `python analisis_data.py` terlebih dahulu.")
    st.stop()

with st.sidebar:
    st.title("🎓 Profil Mahasiswa")
    st.caption("Analisis data kategorik, ordinal, dan numerik")
    st.divider()
    majors = st.multiselect("Jurusan", sorted(df["Jurusan"].unique()), default=sorted(df["Jurusan"].unique()))
    semesters = st.multiselect("Semester", sorted(df["Semester"].unique()), default=sorted(df["Semester"].unique()))
    ipk_range = st.slider("Rentang IPK", 0.0, 4.0, (float(df["IPK"].min()), float(df["IPK"].max())), 0.01)
    age_range = st.slider("Rentang usia", int(df["Usia"].min()), int(df["Usia"].max()), (int(df["Usia"].min()), int(df["Usia"].max())))
    st.divider()
    st.caption("Disusun untuk analisis profil mahasiswa")
    st.markdown(
        "<div style='margin-top: 4rem; padding-top: 1rem; border-top: 1px solid #CBD5E1;'>"
        "<small>Dibuat oleh</small><br><strong>Arwan Priyadinata</strong><br>"
        "<small>Manajemen Informatika</small></div>",
        unsafe_allow_html=True,
    )

filtered = df.loc[
    df["Jurusan"].isin(majors)
    & df["Semester"].isin(semesters)
    & df["IPK"].between(ipk_range[0], ipk_range[1])
    & df["Usia"].between(age_range[0], age_range[1])
].copy()

st.title("Dashboard Profil Mahasiswa")
st.markdown("Memahami komposisi jurusan, jenjang semester, distribusi IPK, dan rentang usia mahasiswa.")
st.caption("Data sintetis untuk pembelajaran, bukan data mahasiswa asli.")

if filtered.empty:
    st.warning("Tidak ada data yang cocok dengan filter. Silakan ubah pilihan di sidebar.")
    st.stop()

avg_ipk = filtered["IPK"].mean()
top_major = filtered["Jurusan"].value_counts().index[0]
metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Total Mahasiswa", f"{len(filtered):,}")
metric_2.metric("Rata-rata IPK", format_number(avg_ipk))
metric_3.metric("Rata-rata Usia", f"{filtered['Usia'].mean():.1f} tahun")
metric_4.metric("Jurusan Terbanyak", top_major)

tab_summary, tab_numeric, tab_detail = st.tabs(["Ringkasan", "IPK & Usia", "Data Mahasiswa"])

with tab_summary:
    st.subheader("Ringkasan Profil Mahasiswa")
    st.write(
        f"Berdasarkan filter yang dipilih, terdapat **{len(filtered):,} mahasiswa** "
        f"dari **{filtered['Jurusan'].nunique()} jurusan** dan "
        f"**{filtered['Semester'].nunique()} tingkat semester**. "
        f"Rata-rata IPK adalah **{format_number(filtered['IPK'].mean())}**, "
        f"sedangkan rentang usia berada pada **{int(filtered['Usia'].min())} sampai "
        f"{int(filtered['Usia'].max())} tahun**."
    )
    left, right = st.columns(2)
    major_counts = filtered["Jurusan"].value_counts().rename_axis("Jurusan").reset_index(name="Jumlah")
    with left:
        fig_major = px.bar(
            major_counts.sort_values("Jumlah"), x="Jumlah", y="Jurusan", orientation="h",
            title="Jumlah Mahasiswa per Jurusan", text_auto=True, color="Jumlah",
            color_continuous_scale="Blues", template="plotly_white",
        )
        fig_major.update_layout(coloraxis_showscale=False, yaxis_title=None)
        st.plotly_chart(fig_major, use_container_width=True)
        st.dataframe(major_counts, use_container_width=True, hide_index=True)
    with right:
        semester_counts = filtered["Semester"].value_counts().sort_index().rename_axis("Semester").reset_index(name="Jumlah")
        semester_counts["Semester"] = semester_counts["Semester"].astype(str)
        fig_semester = px.bar(
            semester_counts, x="Semester", y="Jumlah", title="Distribusi Semester Berurutan",
            text_auto=True, color="Jumlah", color_continuous_scale="Teal", template="plotly_white",
        )
        fig_semester.update_layout(coloraxis_showscale=False, xaxis_title="Semester (ordinal)")
        st.plotly_chart(fig_semester, use_container_width=True)
        st.dataframe(semester_counts, use_container_width=True, hide_index=True)
    st.info("Jurusan adalah data nominal, sedangkan semester diperlakukan sebagai data ordinal karena memiliki urutan 1 sampai 8.")

with tab_numeric:
    left, right = st.columns(2)
    with left:
        fig_ipk = px.histogram(filtered, x="IPK", nbins=20, marginal="box", title="Distribusi IPK dan Box Plot", color_discrete_sequence=["#2563EB"], template="plotly_white")
        fig_ipk.update_layout(xaxis_title="IPK", yaxis_title="Jumlah Mahasiswa")
        st.plotly_chart(fig_ipk, use_container_width=True)
    with right:
        fig_age = px.histogram(filtered, x="Usia", nbins=max(5, filtered["Usia"].nunique()), marginal="box", title="Distribusi Usia dan Box Plot", color_discrete_sequence=["#F59E0B"], template="plotly_white")
        fig_age.update_layout(xaxis_title="Usia (tahun)", yaxis_title="Jumlah Mahasiswa")
        st.plotly_chart(fig_age, use_container_width=True)
    box_variable = st.radio("Bandingkan sebaran per jurusan", ["IPK", "Usia"], horizontal=True)
    st.plotly_chart(px.box(filtered, x="Jurusan", y=box_variable, color="Jurusan", points="outliers", title=f"Sebaran {box_variable} per Jurusan", template="plotly_white"), use_container_width=True)
    st.caption("IPK bersifat kontinu. Usia pada dataset dicatat dalam tahun bulat (diskret). Titik di luar whisker box plot adalah calon outlier menurut aturan 1,5 IQR, bukan otomatis kesalahan data.")

with tab_detail:
    st.caption(f"Menampilkan {len(filtered):,} mahasiswa sesuai filter.")
    st.dataframe(filtered.sort_values(["Semester", "Jurusan"]), use_container_width=True, hide_index=True)
    st.download_button("Unduh data terfilter (CSV)", filtered.to_csv(index=False).encode("utf-8"), "profil_mahasiswa_terfilter.csv", "text/csv")
