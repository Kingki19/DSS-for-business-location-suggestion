import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
from scipy.stats import rankdata
from sklearn.preprocessing import MinMaxScaler

# KONSTANTA
COLUMN_EXCLUDE = 'alternatif'
INDEKS_ACAK = [0,0,0.58,0.90,1.12,1.24,1.32,1.41,1.45,1.49,1.51,1.48,1.56,1.57,1.59]

def check_gemini_api_key_is_true(gemini_api_key: str):
        st.info("If you don't have Gemini API Key, go to link below:", icon="ℹ️")
        st.markdown(f"""
                [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
        """)
        if len(gemini_api_key) != 0:
                try:
                        genai.configure(api_key=gemini_api_key)
                        model = genai.GenerativeModel('gemini-pro')
                        response = model.generate_content("Hello")
                        st.success("Gemini API key is valid!")
                except Exception as e:
                        st.warning(e)

def data_asli() -> pd.DataFrame:
        df = pd.DataFrame({
                'alternatif': ['Lokasi 1', 'Lokasi 2', 'Lokasi 3'],
                'jarak_km': [1, 2, 4],
                'harga_sewa_pertahun': [3_000_000, 1_800_000, 1_200_000],
                'jarak_perumahan_km': [3, 4, 3]
        })
        return df

def create_filtered_dataframe(df: pd.DataFrame, exclude_column: str) -> pd.DataFrame:
        # Mengambil semua nama kolom kecuali 'exclude_column'
        columns_to_keep = [col for col in df.columns if col != exclude_column]

        # Membuat DataFrame baru dengan satu kolom 'index_column' yang berisi nama kolom sesuai urutan
        df_filtered = pd.DataFrame(index=columns_to_keep)

        # Menambahkan kolom yang sesuai dengan df kecuali COLUMN_EXCLUDE
        for col in columns_to_keep:
                df_filtered[col] = ""

        return df_filtered

class Manipulasi_df:
        @staticmethod
        def tambah_kolom_kriteria(df, nama_kriteria, nilai_kriteria):
                if nama_kriteria:
                        df[nama_kriteria] = nilai_kriteria
                        st.session_state.df_perbandingan_kriteria = create_filtered_dataframe(st.session_state.df, COLUMN_EXCLUDE)
                        st.experimental_rerun()  # Refresh halaman untuk memperbarui DataFrame
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
                                st.experimental_rerun()  # Refresh halaman untuk memperbarui DataFrame
                else:
                        st.warning("Harap pilih kolom yang ingin dihapus.")

        @staticmethod
        def hapus_baris(df, baris):
                if baris in df[COLUMN_EXCLUDE].values:
                        st.session_state.df = df[df[COLUMN_EXCLUDE] != baris]
                        st.session_state.df_perbandingan_kriteria = create_filtered_dataframe(st.session_state.df, COLUMN_EXCLUDE)
                        st.experimental_rerun()  # Refresh halaman untuk memperbarui DataFrame
                else:
                        st.warning("Harap pilih baris yang ingin dihapus.")

        @staticmethod
        def tambah_baris(df, baris_baru):
                if all(baris_baru.values()):
                        new_row_df = pd.DataFrame([baris_baru])
                        st.session_state.df = pd.concat([df, new_row_df], ignore_index=True)
                        st.session_state.df_perbandingan_kriteria = create_filtered_dataframe(st.session_state.df, COLUMN_EXCLUDE)
                        st.experimental_rerun()  # Refresh halaman untuk memperbarui DataFrame
                else:
                        st.warning("Harap masukkan semua nilai untuk baris baru.")

def ahp(df: pd.DataFrame):
        # Mengubah nilai-nilai dalam DataFrame menjadi tipe data float dan mengubahnya menjadi matriks numpy
        weights_matrix = df.astype(float).values
        # Menghitung nilai eigen dan vektor eigen dari matriks bobot
        eigvals, eigvecs = np.linalg.eig(weights_matrix)
        # Menentukan nilai eigen maksimum
        max_eigval = np.max(eigvals)
        # Mengambil vektor eigen yang berasosiasi dengan nilai eigen maksimum
        eigvec = eigvecs[:, np.argmax(eigvals)].real
        # Menghitung bobot dengan membagi vektor eigen dengan jumlah total elemen dalam vektor eigen
        weights = eigvec / np.sum(eigvec)
        # Membuat DataFrame baru untuk menampilkan bobot dengan indeks yang sama seperti DataFrame asli
        weights_df = pd.DataFrame(weights, index=df.index, columns=['Bobot'])
        # Mengembalikan DataFrame yang berisi bobot
        return weights_df

def calculate_consistency_ratio(df: pd.DataFrame) -> float:
        # Langkah 1: Mengonversi DataFrame menjadi numpy array
        matrix = df.astype(float).values
        n = len(matrix)
        
        # Langkah 2: Menghitung eigenvector dan nilai eigen maksimum (λ_max)
        eigenvalues, eigenvectors = np.linalg.eig(matrix)
        max_eigenvalue = np.max(eigenvalues)
        principal_eigenvector = eigenvectors[:, np.argmax(eigenvalues)]
        principal_eigenvector = principal_eigenvector / principal_eigenvector.sum()  # Normalisasi

        # Langkah 3: Menghitung Indeks Konsistensi (CI)
        CI = (max_eigenvalue - n) / (n - 1)
        
        # Langkah 4: Menghitung Rasio Konsistensi (CR) menggunakan Indeks Acak (RI)
        # Tabel nilai RI untuk ukuran matriks tertentu
        RI_dict = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        RI = RI_dict.get(n, 1.49)  # Default ke 1.49 jika ukuran matriks di luar tabel RI
        if RI == 0:
                st.warning("Kriteria hanya bisa minimal 3, jika kurang dari itu maka akan error dan menghasilkan nilai NaN")
        CR = CI / RI
        return CR

# Fungsi untuk membuat matriks perbandingan berpasangan
def pairwise_comparison(values):
        size = len(values)
        comparison_matrix = np.zeros((size, size))
        for i in range(size):
                for j in range(size):
                        comparison_matrix[i, j] = values[i] / values[j]
        return comparison_matrix

# Fungsi untuk menghitung bobot prioritas
def calculate_priority(comparison_matrix):
        eigvals, eigvecs = np.linalg.eig(comparison_matrix)
        max_eigval_index = np.argmax(eigvals)
        max_eigvec = eigvecs[:, max_eigval_index]
        priorities = max_eigvec / np.sum(max_eigvec)
        return priorities.real

def calculate_final_priority(weights_df: pd.DataFrame, priorities_dict: dict) -> pd.DataFrame:
        # Mendapatkan nama kriteria dari indeks DataFrame bobot kriteria
        criteria_names = weights_df.index
        
        # Menghitung prioritas akhir untuk setiap alternatif
        final_priorities = {}
        for alt in priorities_dict['alternatif']:
                final_priority = 0
                for criterion in criteria_names:
                        col_weight = weights_df.loc[criterion, 'Bobot']  # Mengakses bobot kriteria menggunakan indeks
                        col_priorities_key = f'prioritas_{criterion}'  # Kunci yang digunakan dalam priorities_dict
                        priorities_array = priorities_dict[col_priorities_key]  # Mengambil array prioritas dari priorities_dict
                        alt_index = int(alt.split()[1])  # Mendapatkan indeks alternatif dari string alternatif
                        st.write(f"Alt Index: {alt_index}")  # Cetak nilai Alt Index untuk memeriksanya
                        try:
                                alt_priority = float(priorities_array[alt_index])  # Mengambil nilai prioritas alternatif dari array prioritas
                                final_priority += alt_priority * col_weight
                        except IndexError as e:
                                st.write(f"IndexError: {e}")
                                st.write(f"Prioritas Array: {priorities_array}")
                                st.write(f"Alt Index: {alt_index}")
                                return
                
                final_priorities[alt] = final_priority
        
        # Membuat DataFrame untuk menampilkan prioritas akhir
        final_priorities_df = pd.DataFrame(final_priorities.values(), index=final_priorities.keys(), columns=['Prioritas Akhir'])
        return final_priorities_df




def main():
        st.title('DSS for Business Location Suggestion')

        # Memuat data asli
        if 'df' not in st.session_state:
                st.session_state.df = data_asli()
        if 'df_perbandingan_kriteria' not in st.session_state:
                st.session_state.df_perbandingan_kriteria = create_filtered_dataframe(st.session_state.df, COLUMN_EXCLUDE)

        # Menampilkan editor data
        st.header('Dataframe Alternatif')
        edited_df_original = st.data_editor(st.session_state.df)

        col_tambah_kriteria, col_hapus_kriteria = st.columns(2)

        with col_tambah_kriteria:
                with st.expander('Tambah Kriteria'):
                        # Input untuk nama kolom baru
                        new_column_name = st.text_input('Masukkan nama kolom baru:')
                        # Input untuk nilai kolom baru
                        new_column_value = st.text_input('Masukkan nilai untuk kolom baru:')
                        # Tombol untuk menambahkan kolom baru
                        if st.button("Tambah Kolom Baru"):
                                Manipulasi_df.tambah_kolom_kriteria(st.session_state.df, new_column_name, new_column_value)
        with col_hapus_kriteria:
                with st.expander('Hapus Kriteria'):
                        # Pilih kolom untuk dihapus
                        column_to_drop = st.selectbox('Pilih kolom yang ingin dihapus:', st.session_state.df.columns)
                        # Tombol untuk menghapus kolom
                        if st.button("Hapus Kolom"):
                                Manipulasi_df.hapus_kolom_kriteria(st.session_state.df, column_to_drop)

        col_tambah_baris, col_hapus_baris = st.columns(2)
        with col_hapus_baris:
                with st.expander('Hapus Baris'):
                        # Pilih baris untuk dihapus
                        row_to_drop = st.selectbox('Pilih baris yang ingin dihapus (berdasarkan alternatif):', st.session_state.df[COLUMN_EXCLUDE])
                        if st.button("Hapus Baris"):
                                Manipulasi_df.hapus_baris(st.session_state.df, row_to_drop)
        with col_tambah_baris:
                with st.expander('Tambah Baris'):
                        # Input untuk menambah baris baru
                        new_row = {}
                        for col in st.session_state.df.columns:
                                new_row[col] = st.text_input(f'Masukkan nilai untuk {col}', key=f'input_{col}')
                        # Tombol untuk menambahkan baris baru
                        if st.button("Tambah Baris Baru"):
                                Manipulasi_df.tambah_baris(st.session_state.df, new_row)

        # Dataframe kriteria
        st.header('Dataframe Perbandingan Kriteria')
        edited_df_kriteria = st.data_editor(st.session_state.df_perbandingan_kriteria)

        # Validasi bahwa semua nilai di edited_df_kriteria telah diisi
        if edited_df_kriteria.isnull().values.any():
                st.warning("Harap isi semua nilai dalam dataframe perbandingan kriteria.")
                return

        # Menghitung bobot kriteria menggunakan AHP dan rasio konsistensi
        st.header('Bobot Kriteria dan Konsistensi Rasio')
        col_bobot, col_consistency_ratio = st.columns(2)
        with col_bobot:
                try:
                        weights_df = ahp(edited_df_kriteria)
                        st.write(weights_df)
                        # st.write(type(weights))
                except Exception as e:
                        st.error(f"Terjadi kesalahan dalam perhitungan bobot: {e}")
                        return
        with col_consistency_ratio:
                rasio_konsisten = calculate_consistency_ratio(edited_df_kriteria)
                ambang_batas = 1
                st.write(f"Rasio konsistensi: {rasio_konsisten:.5f}")
                st.write(f"Ambang batas: {ambang_batas}")
                if rasio_konsisten < ambang_batas:
                        st.write('Matriks di samping konsisten')
                else:
                        st.write('Matriks di samping tidak konsisten')
                        
        st.header('Pairwise Comparison untuk setiap alternatif di setiap kriteria')
        # Loop melalui setiap kriteria kecuali kolom 'alternatif'
        priorities_dict = {'alternatif': edited_df_original['alternatif']}
        with st.expander("Tekan untuk melihat hasilnya"):
                for column in edited_df_original.columns[1:]:
                        values = edited_df_original[column].values
                        comparison_matrix = pairwise_comparison(values)
                        priorities = calculate_priority(comparison_matrix)
                        priorities_dict[f'prioritas_{column}'] = priorities
                        col_1, col_2 = st.columns(2)
                        with col_1:
                                st.write(f"Matriks Perbandingan Berpasangan {column}:\n", comparison_matrix)
                        with col_2:
                                st.write(f"\nPrioritas {column}:\n", priorities)

        # Menghitung dan menampilkan prioritas akhir
        st.header('Prioritas Akhir untuk Setiap Alternatif')
        st.write(weights_df)
        st.write(priorities_dict)
        final_priorities_df = calculate_final_priority(weights_df, priorities_dict)
        st.write(final_priorities_df)


if __name__ == "__main__":
        main()
