import streamlit as st
import pandas as pd
import google.generativeai as genai

def check_gemini_api_key_is_true(gemini_api_key:str):
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

def tambah_kolom_kriteria(df, nama_kriteria, nilai_kriteria):
        if nama_kriteria:
                df[nama_kriteria] = nilai_kriteria
                st.experimental_rerun()  # Refresh halaman untuk memperbarui DataFrame
        else:
                st.warning("Harap masukkan nama kolom baru.")

def hapus_kolom_kriteria(df, nama_kriteria):
        if nama_kriteria:
                df.drop(columns=[nama_kriteria], inplace=True)
                st.experimental_rerun()  # Refresh halaman untuk memperbarui DataFrame
        else:
                st.warning("Harap pilih kolom yang ingin dihapus.")

def hapus_baris(df, baris):
        if baris in st.session_state.df.index:
                st.session_state.df.drop(index=baris, inplace=True)
                st.experimental_rerun()  # Refresh halaman untuk memperbarui DataFrame
        else:
                st.warning("Harap pilih baris yang ingin dihapus.")

def main():
        st.title('DSS for Business Location Suggestion')   
        
        # Memuat data asli
        if 'df' not in st.session_state:
                st.session_state.df = data_asli()

        # Menampilkan editor data
        edited_df = st.data_editor(st.session_state.df, num_rows='dynamic')

        col_tambah_kriteria, col_hapus_kriteria, col_hapus_baris = st.columns(3)
        with col_tambah_kriteria:
                # Input untuk nama kolom baru
                new_column_name = st.text_input('Masukkan nama kolom baru:')
                # Input untuk nilai kolom baru
                new_column_value = st.text_input('Masukkan nilai untuk kolom baru:')
                # Tombol untuk menambahkan kolom baru
                if st.button("Tambah Kolom Baru"):
                        tambah_kolom_kriteria(st.session_state.df, new_column_name, new_column_value)
        with col_hapus_kriteria:
                # Pilih kolom untuk dihapus
                column_to_drop = st.selectbox('Pilih kolom yang ingin dihapus:', st.session_state.df.columns)
                # Tombol untuk menghapus kolom
                if st.button("Hapus Kolom"):
                        hapus_kolom_kriteria(st.session_state.df, column_to_drop)
        with col_hapus_baris:
                 # Pilih baris untuk dihapus
                row_to_drop = st.selectbox('Pilih baris yang ingin dihapus (berdasarkan indeks):', st.session_state.df.index)
                if st.button("Hapus Baris")
                        hapus_baris(st.session_state.df, row_to_drop)
        # Menampilkan DataFrame yang telah diedit
        st.write("Data setelah diedit:")
        st.write(st.session_state.df)

if __name__ == "__main__":
        main()
