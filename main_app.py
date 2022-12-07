import streamlit as st
import streamlit.components.v1 as components

st.write("Hello world!")

p = open("data/iframes/AD_bangkok_collection_simulation_five_routes_20221014.html")

height = st.sidebar.slider("Height", 200, 1500, 300, 100)
width = st.sidebar.slider("Width", 200, 1500, 600, 100)

components.html(p.read(),     height=height,
    width=width,)