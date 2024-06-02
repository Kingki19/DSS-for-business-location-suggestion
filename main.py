import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
from scipy.stats import rankdata

COLUMN_EXCLUDE = 'alternatif'

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
                'alternatif': ['Lokasi 1', 'Lokasi 2'],
                'jarak_km': [1, 2],
                'harga_sewa_pertahun': [3_000_000, 1_800_000]
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

def ahp(df):
        weights_matrix = df.astype(float).values
        eigvals, eigvecs = np.linalg.eig(weights_matrix)
        max_eigval = np.max(eigvals)
        eigvec = eigvecs[:, np.argmax(eigvals)].real
        weights = eigvec / np.sum(eigvec)
        return weights

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

        col_tambah_kriteria, col_hapus_kriteria, col_hapus_baris, col_tambah_baris = st.columns(4)

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

        # Menghitung bobot kriteria menggunakan AHP
        st.header('Bobot Kriteria')
        try:
                weights = ahp(edited_df_kriteria)
                st.write(weights)
                st.write(type(weights))
        except Exception as e:
                st.error(f"Terjadi kesalahan dalam perhitungan bobot: {e}")
                return

        # Mengalikan bobot dengan nilai kriteria di edited_df
        st.header('Skor Alternatif')
        try:
                st.write(len(weights))
                st.write(len(st.session_state.df.columns) - 1)
                if len(weights) != len(st.session_state.df.columns) - 1:  # Jumlah bobot tidak sesuai dengan jumlah kolom, dikurangi 1 untuk COLUMN_EXCLUDE
                        raise ValueError("Jumlah bobot tidak sesuai dengan jumlah kolom yang akan dihitung.")
            
                for i, col in enumerate(st.session_state.df.columns):
                        if col != COLUMN_EXCLUDE:
                                st.session_state.df[col] = st.session_state.df[col].astype(float) * weights[i]
                st.write(st.session_state.df)
        except ValueError as ve:
                st.error(f"Terjadi kesalahan dalam perhitungan skor: {ve}")
        except Exception as e:
                st.error(f"Terjadi kesalahan dalam perhitungan skor: {e}")


if __name__ == "__main__":
        main()
