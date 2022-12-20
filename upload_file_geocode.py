import streamlit as st
import pandas as pd
from app_vukwm_bag_delivery.google_geocode import geocode_addresses
from app_vukwm_bag_delivery.aggregates import get_area_num


def stream_geocode_addresses(df):
    with st.spinner("Geocoding missing lat-lon addresses"):
        df = geocode_addresses(df, st.secrets["google_maps_api"], test=False)
    return df


@st.cache()
def check_upload(df):
    st.session_state.geocoding = False


def upload_and_geocode_file():
    st.subheader("Upload bag-delivery file")
    with st.expander("Instructions"):
        st.markdown(
            """
        Step 1: Upload a bag-delivery excel file.\n
        Step 2: The application will then geocode missing latitude and longitude coordinates using google-maps and show the results.\n
        Step 3: Choose a delivery day to generate routes for, taking into acount that stops already have to be assigned to vehicles.\n
        Step 4: Select one or more vehicles to generate routes for. We recommend choosing all assigned vehicles.\n
        Step 5: Click on the generate route button, and job sequences for each vehicle will be generated.\n
        Step 6: Download the results as an Excel file.
        """
        )
    uploaded_file = st.file_uploader("Choose an excel file to upload.")
    if uploaded_file is not None:
        st.session_state.file_name = uploaded_file.name
        df_upload = pd.read_excel(uploaded_file)
        check_upload(df_upload)
        st.session_state.input_columns = df_upload.columns
        if "geocoding" not in st.session_state or st.session_state.geocoding is False:
            st.session_state.df = stream_geocode_addresses(df_upload.copy())
            st.session_state.geocoding = True
        if st.session_state.geocoding is True and "df" in st.session_state:
            df = st.session_state.df.copy()
            with st.expander(
                "Some addresses did not have lat-lon coordinates and were geocoded. Click here to view the results."
            ):
                st.write(
                    f"The following {df['geocoded'].sum()} addresses were geocoded"
                )
                st.dataframe(df.loc[df["geocoded"]])
                st.map(df.loc[df["geocoded"]])
            st.session_state.stop_data = df
