import streamlit as st
import pandas as pd

st.write("VUKM Bag delivery")


def upload_file():
    uploaded_file = st.file_uploader("Choose an excel file to upload.")
    if uploaded_file is not None:
        df1 = pd.read_excel(uploaded_file)
        st.text(df1)


upload_file()
