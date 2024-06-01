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


def main():
        st.title('DSS for business location suggestion')   
        # Memuat data asli
        df = data_asli()
        
        # Menampilkan editor data
        edited_df = st.data_editor(df)
        
        # Input untuk nama kolom baru
        new_column_name = st.text_input('Masukkan nama kolom baru:')
        
        # Input untuk nilai kolom baru
        new_column_value = st.text_input('Masukkan nilai untuk kolom baru:')
        
        # Tombol untuk menambahkan kolom baru
        if st.button("Tambah Kolom Baru"):
                if new_column_name:
                        edited_df[new_column_name] = new_column_value
                        st.write("Data setelah penambahan kolom:")
                        st.write(edited_df)
                else:
                        st.warning("Harap masukkan nama kolom baru.")
        
        # Menampilkan DataFrame yang telah diedit
        st.write("Data setelah diedit:")
        st.write(edited_df)

if __name__ == "__main__":
        main()
                
  
