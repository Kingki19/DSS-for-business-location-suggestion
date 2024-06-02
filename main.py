import streamlit as st
import pandas as pd
import google.generativeai as genai

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
        
def create_filtered_dataframe(df:pd.DataFrame, exclude_column:str) -> pd.DataFrame :
        # Mengambil semua nama kolom kecuali 'exclude_column'
        columns_to_keep = [col for col in df.columns if col != exclude_column]

        # Membuat DataFrame baru dengan kolom yang diinginkan
        df_filtered = df[columns_to_keep].copy()

        # Menambahkan kolom indeks yang berisi nama-nama kolom
        df_filtered['index_column'] = columns_to_keep

        # Menjadikan 'index_column' sebagai indeks
        # df_filtered.set_index('index_column', inplace=True)

        return df_filtered
        
class Manipulasi_df:
        def tambah_kolom_kriteria(df, nama_kriteria, nilai_kriteria):
                if nama_kriteria:
                        df[nama_kriteria] = nilai_kriteria
                        st.experimental_rerun()  # Refresh halaman untuk memperbarui DataFrame
                else:
                        st.warning("Harap masukkan nama kolom baru.")
        
        def hapus_kolom_kriteria(df, nama_kriteria):
                if nama_kriteria:
                        if nama_kriteria == COLUMN_EXCLUDE:
                                st.warning("Harap pilih kolom lain yang ingin dihapus.")
                        else:
                                df.drop(columns=[nama_kriteria], inplace=True)
                                st.experimental_rerun()  # Refresh halaman untuk memperbarui DataFrame
                else:
                        st.warning("Harap pilih kolom yang ingin dihapus.")
        
        def hapus_baris(df, baris):
                if baris in st.session_state.df[COLUMN_EXCLUDE].values:
                        st.session_state.df[st.session_state.df[COLUMN_EXCLUDE] != baris]
                        # st.session_state.df.drop(index=baris, inplace=True)
                        st.experimental_rerun()  # Refresh halaman untuk memperbarui DataFrame
                else:
                        st.warning("Harap pilih baris yang ingin dihapus.")
        
        def tambah_baris(df, baris_baru):
                if all(baris_baru.values()):
                        new_row_df = pd.DataFrame([baris_baru])
                        st.session_state.df = pd.concat([df, new_row_df], ignore_index=True)
                        st.experimental_rerun()  # Refresh halaman untuk memperbarui DataFrame
                else:
                        st.warning("Harap masukkan semua nilai untuk baris baru.")

def main():
        st.title('DSS for Business Location Suggestion')   
        
        # Memuat data asli
        if 'df' not in st.session_state:
                st.session_state.df = data_asli()
        if 'df_perbandingan_kriteria' not in st.session_state:
                st.session_state.df_perbandingan_kriteria = create_filtered_dataframe(st.session_state.df, COLUMN_EXCLUDE)

        # Menampilkan editor data
        st.header('Dataframe Alternatif')
        edited_df = st.data_editor(st.session_state.df)

        col_tambah_kriteria, col_hapus_kriteria, col_hapus_baris, col_tambah_baris = st.columns(4)
       
        with col_tambah_kriteria:
                with st.popover('tambah kriteria'):
                        # Input untuk nama kolom baru
                        new_column_name = st.text_input('Masukkan nama kolom baru:')
                        # Input untuk nilai kolom baru
                        new_column_value = st.text_input('Masukkan nilai untuk kolom baru:')
                        # Tombol untuk menambahkan kolom baru
                        if st.button("Tambah Kolom Baru"):
                                Manipulasi_df.tambah_kolom_kriteria(st.session_state.df, new_column_name, new_column_value)
        
        with col_hapus_kriteria:
                with st.popover('hapus kriteria'):
                        # Pilih kolom untuk dihapus
                        column_to_drop = st.selectbox('Pilih kolom yang ingin dihapus:', st.session_state.df.columns)
                        # Tombol untuk menghapus kolom
                        if st.button("Hapus Kolom"):
                                Manipulasi_df.hapus_kolom_kriteria(st.session_state.df, column_to_drop)
        
        with col_hapus_baris:
                with st.popover('hapus baris'):
                        # Pilih baris untuk dihapus
                        row_to_drop = st.selectbox('Pilih baris yang ingin dihapus (berdasarkan alternatif):', st.session_state.df[COLUMN_EXCLUDE])
                        if st.button("Hapus Baris"):
                                Manipulasi_df.hapus_baris(st.session_state.df, row_to_drop)
        
        with col_tambah_baris:
                with st.popover('tambah baris'):
                        # Input untuk menambah baris baru
                        new_row = {}
                        for col in st.session_state.df.columns:
                                new_row[col] = st.text_input(f'Masukkan nilai untuk {col}', key=f'input_{col}')
                        # Tombol untuk menambahkan baris baru
                        if st.button("Tambah Baris Baru"):
                                Manipulasi_df.tambah_baris(st.session_state.df, new_row)
        
        # Menampilkan DataFrame yang telah diedit
        st.write("Data setelah diedit:")
        st.write(st.session_state.df)

if __name__ == "__main__":
        main()
