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
        # df_download = df.copy()
        # df_download["Site Latitude"] = df_download["latitude"]
        # df_download["Site Longitude"] = df_download["longitude"]
        # df_download = df_download.drop(columns=["latitude", "longitude"])
        # df_xlsx = to_excel(df_download)
        # st.download_button(
        #     "Press to Download",
        #     data=df_xlsx,
        #     file_name=f"{file_name.replace('.xlsx', '')}_geocoded.xlsx",
        # )
        st.session_state.stop_data = df


st.title("VUKM Bag delivery")

if check_password():
    main_stream_app()

if "stop_data" in st.session_state:
    data_options = st.session_state.stop_data.copy()
    date_range = data_options.assign(
        collection_date=pd.to_datetime(
            data_options["Required Date"], dayfirst=True
        ).dt.strftime(
            "%Y-%m-%d",
        )
    )

    frac_na_dates = (
        (
            date_range.assign(nan_reg=date_range["Registration No"].isna())
            .groupby(["collection_date"])
            .agg(
                n_stops=("collection_date", "count"),
                n_unassigned=("nan_reg", "sum"),
            )
        )
        .reset_index()
        .rename(
            columns={
                "collection_date": "Collection date",
                "n_stops": "Total number of stops",
                "n_unassigned": "Stops not assigned to a vehicle",
            }
        )
    )

    frac_na_dates["Fraction of stops not assigned"] = (
        frac_na_dates["Stops not assigned to a vehicle"]
        / frac_na_dates["Total number of stops"]
    ).round(2)
    st.write("Total number of stops and unassigned stops for delivery days:")
    st.dataframe(frac_na_dates)

    min_fraction_cutoff = st.slider(
        "Maximum allowed fraction of unassigned stops", 0.0, 1.0, 0.25
    )
    min_stop_cutoff = st.slider("Minimum required number of stops", 0, 100, 25)

    allowed_dates = (frac_na_dates["Total number of stops"] >= min_stop_cutoff) & (
        frac_na_dates["Fraction of stops not assigned"] <= min_fraction_cutoff
    )

    unique_dates = (
        frac_na_dates.loc[allowed_dates]["Collection date"].sort_values().unique()
    )
    delivery_date = st.multiselect(
        "Select a delivery date",
        unique_dates,
        default=[unique_dates.max()],
    )
    date_filter = date_range.loc[date_range["collection_date"].isin(delivery_date)]
    if date_filter.shape[0] > 0:
        date_filter = date_filter.assign(
            tansport_area_num=date_filter["Transport Area Code"].str[:-1].astype(int)
        ).sort_values(["collection_date", "Registration No", "tansport_area_num"])
        vehicle_delivery_summary = (
            date_filter.groupby(["Registration No"])
            .agg(
                n_stops=("Registration No", "count"),
                assigned_zones=("tansport_area_num", "unique"),
            )
            .reset_index()
        ).rename(columns={"n_stops": "Total number of stops"})
        vehicle_summary = (
            date_filter.groupby(["Registration No", "Product Name"])
            .agg(
                n_stops=("Registration No", "count"),
                n_boxes=("Quantity", "sum"),
            )
            .reset_index()
        ).rename(
            columns={
                "n_stops": "Number of deliveries",
                "n_boxes": "Number of boxes",
                "assigned_zones": "Transport zone number",
            }
        )
        st.write("Delivery stops assigned to each vehicle")
        st.dataframe(vehicle_delivery_summary)
        st.write("Number of stops per boxes type and number of boxes per vehicle")
        vehicle_filter = st.multiselect(
            "Select vehicles:",
            vehicle_delivery_summary["Registration No"].unique(),
            default=vehicle_delivery_summary["Registration No"].unique(),
        )
        vehicle_summary_limit = vehicle_summary.loc[
            vehicle_summary["Registration No"].isin(vehicle_filter)
        ]
        st.dataframe(vehicle_summary_limit)
