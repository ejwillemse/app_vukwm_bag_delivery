import streamlit as st

from check_password import check_password

if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line
