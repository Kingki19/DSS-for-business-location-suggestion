import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

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

def create_filtered_dataframe(df: pd.DataFrame, exclude_column: str) -> pd.DataFrame:
        columns_to_keep = [col for col in df.columns if col != exclude_column]
        df_filtered = pd.DataFrame(index=columns_to_keep)
        for col in columns_to_keep:
                df_filtered[col] = ""
        return df_filtered

class Manipulasi_df:
        @staticmethod
        def tambah_kolom_kriteria(df, nama_kriteria, nilai_kriteria):
                if nama_kriteria:
                        df[nama_kriteria] = nilai_kriteria
                        st.session_state.df_perbandingan_kriteria = create_filtered_dataframe(st.session_state.df, COLUMN_EXCLUDE)
                        st.experimental_rerun()
                else:
                        st.warning("Harap masukkan nama kolom baru.")

        @staticmethod
        def hapus_kolom_kriteria(df, nama_kriteria):
                if nama_kriteria:
                        if nama_kriteria == COLUMN_EXCLUDE:
                                st.warning("Harap pilih kolom lain yang ingin dihapus.")
                        else:
                                df.drop(columns=[nama_kriteria], inplace=True)
                                st.session_state.df_perbandingan_kriteria = create_filtered_dataframe(st.session_state.df, COLUMN_EXCLUDE)
                                st.experimental_rerun()
                else:
                        st.warning("Harap pilih kolom yang ingin dihapus.")

        @staticmethod
        def hapus_baris(df, baris):
                if baris in df[COLUMN_EXCLUDE].values:
                        st.session_state.df = df[df[COLUMN_EXCLUDE] != baris]
                        st.session_state.df_perbandingan_kriteria = create_filtered_dataframe(st.session_state.df, COLUMN_EXCLUDE)
                        st.experimental_rerun()
                else:
                        st.warning("Harap pilih baris yang ingin dihapus.")

        @staticmethod
        def tambah_baris(df, baris_baru):
                if all(baris_baru.values()):
                        new_row_df = pd.DataFrame([baris_baru])
                        st.session_state.df = pd.concat([df, new_row_df], ignore_index=True)
                        st.session_state.df_perbandingan_kriteria = create_filtered_dataframe(st.session_state.df, COLUMN_EXCLUDE)
                        st.experimental_rerun()
                else:
                        st.warning("Harap masukkan semua nilai untuk baris baru.")

def topsis(df: pd.DataFrame, weights: np.array):
        # Normalisasi matriks keputusan
        df_normalized = df.copy()
        for column in df.columns[1:]:
                df_normalized[column] = df[column] / np.sqrt((df[column]**2).sum())
        
        # Melakukan pembobotan pada matriks yang sudah dinormalisasi
        df_weighted = df_normalized.copy()
        for i, column in enumerate(df.columns[1:]):
                df_weighted[column] = df_weighted[column] * weights[i]

        # Menentukan solusi ideal positif dan negatif
        ideal_positive = df_weighted.max()
        ideal_negative = df_weighted.min()
        
        # Menghitung jarak ke solusi ideal positif dan negatif
        df_weighted['d_pos'] = np.sqrt(((df_weighted - ideal_positive)**2).sum(axis=1))
        df_weighted['d_neg'] = np.sqrt(((df_weighted - ideal_negative)**2).sum(axis=1))
        
        # Menghitung skor TOPSIS
        df_weighted['topsis_score'] = df_weighted['d_neg'] / (df_weighted['d_pos'] + df_weighted['d_neg'])
        
        return df_weighted[['topsis_score']].sort_values(by='topsis_score', ascending=False)

def main():
        st.title('🗺️ Sistem Pengambil Keputusan untuk Saran Lokasi Bisnis menggunakan TOPSIS')
        st.divider()
        
        # Memuat data asli
        if 'df' not in st.session_state:
                st.session_state.df = data_asli()
        if 'df_perbandingan_kriteria' not in st.session_state:
                st.session_state.df_perbandingan_kriteria = create_filtered_dataframe(st.session_state.df, COLUMN_EXCLUDE)

        # Menampilkan editor data
        st.header('1️⃣ Dataframe Alternatif')
        st.markdown("""
                > Jika ingin mengganti nilai, ganti saja isi dari dataframe di bawah untuk menyesuaikan data aslimu.  
                > Jika ingin memanipulasi dataframe, manfaatkan beberapa fungsi dibawah.
        """)
        edited_df_original = st.data_editor(st.session_state.df)
        st.markdown("### **Manipulasi Dataframe**")
        col_tambah_kriteria, col_hapus_kriteria = st.columns(2)

        with col_tambah_kriteria:
                with st.expander('Tambah Kriteria'):
                        new_column_name = st.text_input('Masukkan nama kolom baru:')
                        new_column_value = st.text_input('Masukkan nilai untuk kolom baru:')
                        if st.button("Tambah Kolom Baru"):
                                Manipulasi_df.tambah_kolom_kriteria(st.session_state.df, new_column_name, new_column_value)
        with col_hapus_kriteria:
                with st.expander('Hapus Kriteria'):
                        column_to_drop = st.selectbox('Pilih kolom yang ingin dihapus:', st.session_state.df.columns)
                        if st.button("Hapus Kolom"):
                                Manipulasi_df.hapus_kolom_kriteria(st.session_state.df, column_to_drop)

        col_tambah_baris, col_hapus_baris = st.columns(2)
        with col_hapus_baris:
                with st.expander('Hapus Baris'):
                        row_to_drop = st.selectbox('Pilih baris yang ingin dihapus (berdasarkan alternatif):', st.session_state.df[COLUMN_EXCLUDE])
                        if st.button("Hapus Baris"):
                                Manipulasi_df.hapus_baris(st.session_state.df, row_to_drop)
        with col_tambah_baris:
                with st.expander('Tambah Baris'):
                        new_row = {}
                        for col in st.session_state.df.columns:
                                new_row[col] = st.text_input(f'Masukkan nilai untuk {col}', key=f'input_{col}')
                        if st.button("Tambah Baris Baru"):
                                Manipulasi_df.tambah_baris(st.session_state.df, new_row)
        st.divider()
        
        # Dataframe kriteria
        st.header('2️⃣ Dataframe Bobot Kriteria')
        st.markdown("""
                > Harap masukkan bobot untuk setiap kriteria.
        """)
        weights = []
        for col in st.session_state.df.columns[1:]:
                weight = st.number_input(f'Bobot untuk {col}', min_value=0.0, max_value=1.0, step=0.1, value=0.5)
                weights.append(weight)
        weights = np.array(weights)
        
        st.divider()
        
        # Menghitung dan menampilkan skor TOPSIS
        st.header('3️⃣ Prioritas Akhir untuk Setiap Alternatif dengan TOPSIS')
        final_scores_df = topsis(edited_df_original, weights)
        st.write(final_scores_df)
        max_score_alternative = final_scores_df['topsis_score'].idxmax()
        st.write(f"Alternatif dengan Skor TOPSIS Tertinggi: {max_score_alternative}")

if __name__ == "__main__":
        main()

