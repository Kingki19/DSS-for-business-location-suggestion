import streamlit as st
import pandas as pd

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

def main():
        st.title('DSS for business location suggestion')
        with st.sidebar:
                GEMINI_API_KEY = st.text_input(
                        label = 'input your gemini api key',
                        type = 'password'
                )
                check_gemini_api_key_is_true(GEMINI_API_KEY)

main()
                
  
