import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path

DATASET_PATH = Path(__file__).with_name('dataset_penjualan.csv')

# 1. GENERASI DATA SINTESIS
np.random.seed(42)
random.seed(42)

# Mengembangkan katalog berdasarkan sampel "Laptop" dan "Buku"
katalog = {
    'Elektronik': [('Laptop', 8500000), ('Smartphone', 4500000), ('Monitor', 2500000)],
    'Pendidikan': [('Buku', 75000), ('Alat Tulis', 35000), ('Tas Ransel', 250000)],
    'Aksesoris': [('Mouse', 150000), ('Keyboard', 350000), ('Headset', 450000)]
}

data = []
start_date = datetime(2024, 1, 1)

for _ in range(1000):
    kategori = random.choice(list(katalog.keys()))
    produk, base_price = random.choice(katalog[kategori])
    
    # Variasi harga agar histogram lebih dinamis
    harga = round(int(base_price * random.uniform(0.85, 1.15)), -3)
    jumlah_terjual = np.random.randint(5, 150)
    
    # Tanggal acak dalam rentang 1 tahun (format dd/mm/yy)
    days_offset = np.random.randint(0, 365)
    tanggal = start_date + timedelta(days=days_offset)
    
    data.append([produk, kategori, harga, jumlah_terjual, tanggal.strftime('%d/%m/%y')])

# Membuat DataFrame
df = pd.DataFrame(data, columns=['Produk', 'Kategori', 'Harga (Rp)', 'Jumlah Terjual', 'Tanggal'])
df.to_csv(DATASET_PATH, index=False)
print(f"1000 Data sintesis berhasil dibuat dan disimpan sebagai '{DATASET_PATH.name}'\n")

# 2. ANALISIS DATA DETIL
print("--- RINGKASAN DATA (INFO) ---")
print(df.info(), "\n")

print("--- STATISTIK DESKRIPTIF KATA KUNCI NUMERIK ---")
print(df[['Harga (Rp)', 'Jumlah Terjual']].describe(), "\n")

# Konversi tanggal untuk analisis tren
df['Tanggal'] = pd.to_datetime(df['Tanggal'], format='%d/%m/%y')
df['Total Pendapatan'] = df['Harga (Rp)'] * df['Jumlah Terjual']

print("--- ANALISIS KINERJA KATEGORI ---")
kategori_perf = df.groupby('Kategori').agg({
    'Jumlah Terjual': 'sum',
    'Total Pendapatan': 'sum'
}).sort_values(by='Total Pendapatan', ascending=False)
print(kategori_perf, "\n")

print("--- ANALISIS TREN PENJUALAN BULANAN ---")
tren_bulanan = df.resample('ME', on='Tanggal')['Total Pendapatan'].sum()
print(tren_bulanan)
