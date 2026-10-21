from pathlib import Path

import numpy as np
import pandas as pd


DATASET_PATH = Path(__file__).with_name("dataset_mahasiswa.csv")


def buat_dataset(jumlah=500):
    rng = np.random.default_rng(42)
    semester = rng.integers(1, 9, size=jumlah)
    return pd.DataFrame({
        "Jurusan": rng.choice(
            ["Sistem Informasi", "Manajemen", "Manajemen Informatika", "Teknik Informatika"],
            size=jumlah,
        ),
        "Semester": semester,
        "IPK": np.clip(rng.normal(3.25, 0.45, size=jumlah), 0, 4).round(2),
        "Usia": 18 + (semester - 1) // 2 + rng.integers(0, 3, size=jumlah),
    })


if __name__ == "__main__":
    df = buat_dataset()
    df.to_csv(DATASET_PATH, index=False)
    print(f"Dataset sintetis: {len(df)} mahasiswa disimpan di {DATASET_PATH}")
    print("\nSTATISTIK IPK DAN USIA")
    print(df[["IPK", "Usia"]].describe())
    print("\nDISTRIBUSI JURUSAN (NOMINAL)")
    print(df["Jurusan"].value_counts())
    print("\nDISTRIBUSI SEMESTER (ORDINAL)")
    print(df["Semester"].value_counts().sort_index())
    print("\nRINGKASAN PER JURUSAN")
    print(df.groupby("Jurusan").agg(
        Jumlah=("IPK", "size"), Rata_IPK=("IPK", "mean"), Rata_Usia=("Usia", "mean")
    ).round(2))
    print("\nCALON OUTLIER BERDASARKAN ATURAN 1.5 IQR")
    for kolom in ["IPK", "Usia"]:
        q1, q3 = df[kolom].quantile([0.25, 0.75])
        iqr = q3 - q1
        outliers = df.loc[(df[kolom] < q1 - 1.5 * iqr) | (df[kolom] > q3 + 1.5 * iqr)]
        print(f"{kolom}: {len(outliers)} baris; bukan otomatis kesalahan data.")
