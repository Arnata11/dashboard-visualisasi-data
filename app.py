from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATASET_PATH = Path(__file__).with_name("dataset_penjualan.csv")
PRIMARY_COLOR = "#1D4ED8"
ACCENT_COLOR = "#F59E0B"

st.set_page_config(
    page_title="Insight Penjualan | Arwan Priyadinata",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        [data-testid="stMetric"] {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 14px;
        }
        [data-testid="stMetricLabel"] {color: #475569;}
        [data-testid="stMetricValue"] {color: #0F172A;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATASET_PATH)
    data["Tanggal"] = pd.to_datetime(data["Tanggal"], format="%d/%m/%y")
    data["Total Pendapatan"] = data["Harga (Rp)"] * data["Jumlah Terjual"]
    return data


def format_rupiah(value: float) -> str:
    return f"Rp {value:,.0f}".replace(",", ".")


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        f"File '{DATASET_PATH.name}' tidak ditemukan di folder aplikasi. "
        "Jalankan analisis_data.py terlebih dahulu."
    )
    st.stop()


with st.sidebar:
    st.title("📊 Insight Penjualan")
    st.caption("Dashboard operasional interaktif")
    st.divider()
    st.subheader("Filter Data")

    min_date = df["Tanggal"].min().date()
    max_date = df["Tanggal"].max().date()
    selected_dates = st.date_input(
        "Rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    selected_categories = st.multiselect(
        "Kategori produk",
        options=sorted(df["Kategori"].unique()),
        default=sorted(df["Kategori"].unique()),
    )
    available_products = sorted(
        df.loc[df["Kategori"].isin(selected_categories), "Produk"].unique()
    )
    selected_products = st.multiselect(
        "Produk",
        options=available_products,
        default=available_products,
    )

    st.divider()
    st.caption("Disusun oleh")
    st.markdown("**Arwan Priyadinata**  ")
    st.caption("Manajemen Informatika")

if len(selected_dates) != 2:
    st.info("Pilih tanggal awal dan akhir untuk menampilkan analisis.")
    st.stop()

start_date, end_date = pd.to_datetime(selected_dates)
filtered_df = df.loc[
    df["Tanggal"].between(start_date, end_date)
    & df["Kategori"].isin(selected_categories)
    & df["Produk"].isin(selected_products)
].copy()

st.title("Dashboard Insight Penjualan")
st.markdown(
    "Pantau performa penjualan, temukan produk unggulan, dan baca tren transaksi dalam satu tempat."
)
st.caption("Arwan Priyadinata | Manajemen Informatika")

if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan filter. Ubah pilihan filter pada sidebar.")
    st.stop()

previous_period_days = (end_date - start_date).days + 1
previous_start = start_date - pd.Timedelta(days=previous_period_days)
previous_end = start_date - pd.Timedelta(days=1)
previous_df = df.loc[
    df["Tanggal"].between(previous_start, previous_end)
    & df["Kategori"].isin(selected_categories)
    & df["Produk"].isin(selected_products)
]

current_revenue = filtered_df["Total Pendapatan"].sum()
previous_revenue = previous_df["Total Pendapatan"].sum()
revenue_delta = None if previous_revenue == 0 else (current_revenue / previous_revenue - 1)
top_product = (
    filtered_df.groupby("Produk")["Total Pendapatan"].sum().idxmax()
)

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Total Pendapatan", format_rupiah(current_revenue),
                None if revenue_delta is None else f"{revenue_delta:.1%} vs periode sebelumnya")
metric_2.metric("Total Transaksi", f"{len(filtered_df):,}")
metric_3.metric("Barang Terjual", f"{filtered_df['Jumlah Terjual'].sum():,}")
metric_4.metric("Produk Terbaik", top_product)

tab_overview, tab_trends, tab_products, tab_data = st.tabs(
    ["Ringkasan", "Tren Penjualan", "Produk & Kategori", "Data Transaksi"]
)

with tab_overview:
    daily_revenue = (
        filtered_df.groupby("Tanggal", as_index=False)["Total Pendapatan"].sum()
        .sort_values("Tanggal")
    )
    fig_revenue = px.area(
        daily_revenue,
        x="Tanggal",
        y="Total Pendapatan",
        title="Pergerakan Pendapatan Harian",
        color_discrete_sequence=[PRIMARY_COLOR],
        template="plotly_white",
    )
    fig_revenue.update_layout(yaxis_title="Pendapatan (Rp)", xaxis_title=None, hovermode="x unified")
    st.plotly_chart(fig_revenue, use_container_width=True)

    chart_left, chart_right = st.columns(2)
    category_revenue = (
        filtered_df.groupby("Kategori", as_index=False)["Total Pendapatan"].sum()
        .sort_values("Total Pendapatan", ascending=False)
    )
    with chart_left:
        fig_category = px.pie(
            category_revenue,
            names="Kategori",
            values="Total Pendapatan",
            hole=0.55,
            title="Kontribusi Pendapatan per Kategori",
            color_discrete_sequence=px.colors.qualitative.Safe,
        )
        fig_category.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_category, use_container_width=True)
    with chart_right:
        st.subheader("Sorotan Performa")
        total_products = filtered_df["Produk"].nunique()
        average_order = filtered_df["Total Pendapatan"].mean()
        best_category = category_revenue.iloc[0]["Kategori"]
        st.info(f"**{best_category}** menjadi kategori dengan pendapatan tertinggi pada periode terpilih.")
        st.write(f"Rata-rata nilai transaksi: **{format_rupiah(average_order)}**")
        st.write(f"Produk aktif dalam hasil filter: **{total_products} produk**")

with tab_trends:
    trend_metric = st.radio(
        "Tampilkan tren berdasarkan",
        ["Pendapatan", "Jumlah Terjual"],
        horizontal=True,
    )
    value_column = "Total Pendapatan" if trend_metric == "Pendapatan" else "Jumlah Terjual"
    y_label = "Pendapatan (Rp)" if trend_metric == "Pendapatan" else "Jumlah Barang"
    monthly_trend = (
        filtered_df.set_index("Tanggal")
        .groupby("Kategori")[value_column]
        .resample("ME")
        .sum()
        .reset_index()
    )
    fig_trend = px.line(
        monthly_trend,
        x="Tanggal",
        y=value_column,
        color="Kategori",
        markers=True,
        title=f"Tren Bulanan: {trend_metric}",
        template="plotly_white",
    )
    fig_trend.update_layout(yaxis_title=y_label, xaxis_title=None, hovermode="x unified")
    st.plotly_chart(fig_trend, use_container_width=True)

with tab_products:
    left_column, right_column = st.columns(2)
    product_performance = (
        filtered_df.groupby("Produk", as_index=False)
        .agg(
            Pendapatan=("Total Pendapatan", "sum"),
            Jumlah_Terjual=("Jumlah Terjual", "sum"),
        )
        .rename(columns={"Jumlah_Terjual": "Jumlah Terjual"})
        .sort_values("Pendapatan")
    )
    with left_column:
        fig_products = px.bar(
            product_performance,
            x="Pendapatan",
            y="Produk",
            orientation="h",
            text_auto=".2s",
            title="Peringkat Produk berdasarkan Pendapatan",
            color="Pendapatan",
            color_continuous_scale="Blues",
            template="plotly_white",
        )
        fig_products.update_layout(coloraxis_showscale=False, yaxis_title=None, xaxis_title="Pendapatan (Rp)")
        st.plotly_chart(fig_products, use_container_width=True)
    with right_column:
        fig_histogram = px.histogram(
            filtered_df,
            x="Harga (Rp)",
            color="Kategori",
            nbins=25,
            barmode="overlay",
            opacity=0.75,
            title="Sebaran Harga Produk",
            color_discrete_sequence=px.colors.qualitative.Safe,
            template="plotly_white",
        )
        fig_histogram.update_layout(xaxis_title="Harga (Rp)", yaxis_title="Jumlah Transaksi")
        st.plotly_chart(fig_histogram, use_container_width=True)

with tab_data:
    st.caption(f"Menampilkan {len(filtered_df):,} transaksi sesuai filter yang dipilih.")
    display_df = filtered_df.sort_values("Tanggal", ascending=False).copy()
    display_df["Tanggal"] = display_df["Tanggal"].dt.strftime("%d %b %Y")
    display_df["Harga (Rp)"] = display_df["Harga (Rp)"].map(format_rupiah)
    display_df["Total Pendapatan"] = display_df["Total Pendapatan"].map(format_rupiah)
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.download_button(
        "Unduh data sesuai filter (CSV)",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="data_penjualan_terfilter.csv",
        mime="text/csv",
    )
