import streamlit as st
import pandas as pd
from app_vukwm_bag_delivery.google_geocode import geocode_addresses

st.write("VUKM Bag delivery")


uploaded_file = st.file_uploader("Choose an excel file to upload.")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    geocode_addresses()
