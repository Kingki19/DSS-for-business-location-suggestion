import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import rankdata

# KONSTANTA
COLUMN_EXCLUDE = 'alternatif'

# KONFIGURASI HALAMAN
st.set_page_config(
    page_title="SPK-TOPSIS Lokasi Bisnis",
    layout="wide",
)

def data_asli() -> pd.DataFrame:
    df = pd.DataFrame({
        'alternatif': ['Lokasi 1', 'Lokasi 2', 'Lokasi 3'],
        'jarak_pusat_km': [1, 2, 4],
        'harga_sewa_pertahun': [3_000_000, 1_800_000, 1_200_000],
        'jarak_perumahan_km': [3, 4, 3]
    })
    return df

def topsis(df: pd.DataFrame, weights: np.ndarray) -> pd.DataFrame:
    # Normalisasi Matriks Keputusan
    scaler = MinMaxScaler()
    normalized_matrix = scaler.fit_transform(df.iloc[:, 1:])
    
    # Pembobotan Matriks Keputusan
    weighted_matrix = normalized_matrix * weights
    
    # Menentukan Solusi Ideal Positif dan Negatif
    ideal_positive = np.max(weighted_matrix, axis=0)
    ideal_negative = np.min(weighted_matrix, axis=0)
    
    # Menghitung Jarak ke Solusi Ideal Positif dan Negatif
    distance_positive = np.sqrt(((weighted_matrix - ideal_positive)**2).sum(axis=1))
    distance_negative = np.sqrt(((weighted_matrix - ideal_negative)**2).sum(axis=1))
    
    # Menghitung Skor Preferensi untuk Setiap Alternatif
    scores = distance_negative / (distance_positive + distance_negative)
    df['topsis_score'] = scores
    df['rank'] = rankdata(-scores, method='min')
    
    return df

def main():
    st.title('🗺️ Sistem Pengambil Keputusan untuk Saran Lokasi Bisnis menggunakan TOPSIS')
    st.divider()
    
    # Memuat data asli
    if 'df' not in st.session_state:
        st.session_state.df = data_asli()
    
    # Menampilkan editor data
    st.header('1️⃣ Dataframe Alternatif')
    st.markdown("""
        > Jika ingin mengganti nilai, ganti saja isi dari dataframe di bawah untuk menyesuaikan data aslimu.  
        > Jika ingin memanipulasi dataframe, manfaatkan beberapa fungsi dibawah.
    """)
    edited_df_original = st.data_editor(st.session_state.df)
    st.divider()
    
    # Input bobot kriteria
    st.header('2️⃣ Input Bobot Kriteria')
    st.markdown("""
        > Masukkan bobot untuk setiap kriteria di bawah ini.  
    """)
    weights = []
    for col in edited_df_original.columns[1:]:
        weight = st.number_input(f'Bobot untuk {col}', min_value=0.0, max_value=1.0, step=0.01, value=0.5)
        weights.append(weight)
    
    weights = np.array(weights)
    st.divider()
    
    # Menghitung dan menampilkan hasil TOPSIS
    st.header('3️⃣ Hasil Perhitungan TOPSIS')
    try:
        final_scores_df = topsis(edited_df_original, weights)
        st.write(final_scores_df)
    except Exception as e:
        st.error(f"Terjadi kesalahan dalam perhitungan TOPSIS: {e}")

if __name__ == "__main__":
    main()
