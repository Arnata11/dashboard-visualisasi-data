from pathlib import Path

import numpy as np
import pandas as pd


DATASET_PATH = Path(__file__).with_name("dataset_cuaca.csv")


def buat_dataset(jumlah=600):
    rng = np.random.default_rng(42)
    kota = rng.choice(["Jakarta", "Bandung", "Surabaya", "Yogyakarta", "Bogor"], jumlah)
    kondisi = rng.choice(["Cerah", "Berawan", "Hujan"], jumlah, p=[0.4, 0.35, 0.25])
    suhu_dasar = {"Jakarta": 31, "Bandung": 24, "Surabaya": 32, "Yogyakarta": 29, "Bogor": 26}
    suhu = np.array([suhu_dasar[k] for k in kota]) + rng.normal(0, 2, jumlah)
    suhu -= np.where(kondisi == "Hujan", 2, 0)
    kelembaban = rng.normal(73, 9, jumlah) + np.where(kondisi == "Hujan", 12, 0)
    return pd.DataFrame({
        "Kota": kota,
        "Suhu (°C)": suhu.round(1),
        "Kelembaban (%)": np.clip(kelembaban, 0, 100).round(1),
        "Kondisi": kondisi,
    })


if __name__ == "__main__":
    df = buat_dataset()
    df.to_csv(DATASET_PATH, index=False)
    print(f"Dataset sintetis: {len(df)} pengamatan disimpan di {DATASET_PATH}")
    print("\nSTATISTIK SUHU DAN KELEMBABAN")
    print(df[["Suhu (°C)", "Kelembaban (%)"]].describe())
    print("\nDISTRIBUSI KOTA DAN KONDISI")
    print(df["Kota"].value_counts())
    print(df["Kondisi"].value_counts())
    print("\nRINGKASAN PER KOTA")
    print(df.groupby("Kota").agg(
        Pengamatan=("Kota", "size"), Rata_Suhu=("Suhu (°C)", "mean"),
        Rata_Kelembaban=("Kelembaban (%)", "mean")
    ).round(2))
    print("\nCATATAN SKALA DATA")
    print("Kota dan kondisi: nominal. Suhu Celsius: interval, bukan rasio.")
    print("Kelembaban: rasio, mempunyai nol absolut.")
