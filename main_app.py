import streamlit as st
import pandas as pd
from app_vukwm_bag_delivery.google_geocode import geocode_addresses
from app_vukwm_bag_delivery.download_to_excel import to_excel


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Please enter the app password to proceed:",
            type="password",
            on_change=password_entered,
            key="password",
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True


def stream_geocode_addresses(df):
    with st.spinner("Geocoding missing lat-lon addresses"):
        df = geocode_addresses(df, st.secrets["google_maps_api"], test=True)
    return df


def main_stream_app():
    with st.expander("Instructions"):
        st.markdown(
            """
        Step 1: Upload a bag-delivery excel file.\n
        Step 2: The application will then geocode missing latitude and longitude coordinates using google-maps and show the results.\n
        Step 3: Click on `"Press to Download"` to download the missing latitude and longitude addresses added.
        """
        )
    uploaded_file = st.file_uploader("Choose an excel file to upload.")
    if uploaded_file is not None:
        file_name = uploaded_file.name
        df = pd.read_excel(uploaded_file)
        df = stream_geocode_addresses(df)
        if df["geocoded"].any():
            with st.expander(
                "Some addresses did not have lat-lon coordinates and were geocoded. The results can be viewed here"
            ):
                st.write(
                    f"The following {df['geocoded'].sum()} addresses were geocoded"
                )
                st.dataframe(df.loc[df["geocoded"]])
                st.map(df.loc[df["geocoded"]])
        df_download = df.copy()
        df_download["Site Latitude"] = df_download["latitude"]
        df_download["Site Longitude"] = df_download["longitude"]
        df_download = df_download.drop(columns=["latitude", "longitude"])
        df_xlsx = to_excel(df_download)
        st.download_button(
            "Press to Download",
            data=df_xlsx,
            file_name=f"{file_name.replace('.xlsx', '')}_geocoded.xlsx",
        )


st.title("VUKM Bag delivery")

if check_password():
    main_stream_app()
