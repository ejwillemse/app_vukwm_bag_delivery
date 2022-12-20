import streamlit as st
import pandas as pd
from app_vukwm_bag_delivery.google_geocode import geocode_addresses
import app_vukwm_bag_delivery.aggregates as aggregates
from app_vukwm_bag_delivery.osrm_tsp import sequence_routes
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
        df = geocode_addresses(df, st.secrets["google_maps_api"], test=False)
    return df


@st.cache()
def check_upload(df):
    st.session_state.geocoding = False


def main_stream_app():
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
            st.subheader("Geocoding results")
            with st.expander(
                "Some addresses did not have lat-lon coordinates and were geocoded. Click here to view the results."
            ):
                st.write(
                    f"The following {df['geocoded'].sum()} addresses were geocoded"
                )
                st.dataframe(df.loc[df["geocoded"]])
                st.map(df.loc[df["geocoded"]])
            st.session_state.stop_data = df


st.set_page_config(layout="wide")
st.title("VUKWM Bag delivery")

if check_password():
    main_stream_app()

if "stop_data" in st.session_state:
    st.subheader("Delivery summaries")
    stop_data = st.session_state.stop_data.copy()
    stop_data = aggregates.date_to_string(stop_data)
    day_summary = aggregates.get_day_summary(stop_data)
    st.write("Total number of stops and unassigned stops for delivery days:")
    st.dataframe(day_summary)

    max_fraction_cutoff = st.slider(
        "Maximum allowed fraction of unassigned stops", 0.0, 1.0, 0.25
    )
    min_stop_cutoff = st.slider("Minimum required number of stops", 0, 100, 25)

    unique_dates = aggregates.get_unique_filtered_dates(
        day_summary, max_fraction_cutoff, min_stop_cutoff
    )
    if unique_dates.shape[0] > 0:
        delivery_date = st.selectbox(
            "Select a delivery date",
            unique_dates,
        )
        stop_data_filter = stop_data.loc[
            stop_data["collection_date"].isin([delivery_date])
        ]
    else:
        stop_data_filter = pd.DataFrame()

    if stop_data_filter.shape[0] > 0:
        route_summary = aggregates.calc_route_summary(stop_data_filter)
        route_product_summary = aggregates.calc_route_product_summary(stop_data_filter)

        st.write("Deliveries assigned to each vehicle")
        st.dataframe(route_summary)

        vehicle_filter = st.multiselect(
            "Select vehicles for further inspection:",
            route_summary["Registration No"].unique(),
            default=route_summary["Registration No"].unique(),
        )
        st.write("Number of deliveries per box type and number of boxes per vehicle")
        route_product_summary_filtered = route_product_summary.loc[
            route_product_summary["Registration No"].isin(vehicle_filter)
        ]
        st.dataframe(route_product_summary_filtered)
        st.session_state.route_stops = stop_data_filter.copy()
        st.session_state.route_summary = route_summary.copy()
        st.session_state.route_product_summary_filtered = (
            route_product_summary_filtered.copy()
        )

if "route_stops" in st.session_state:
    st.subheader("Sequence deliveries for assigned vehicles")
    if st.button("Generate route sequences"):
        route_stops = st.session_state.route_stops.copy()
        n_vehicles = route_stops["Registration No"].nunique()
        with st.spinner(
            f"Generating delivery sequences for the {n_vehicles} selected vehicles..."
        ):
            results = sequence_routes(route_stops, ports=st.secrets["osrm_ports"][0])
            assigned_stops = results[0]
            results_summary = results[-1]
            tsp_route_summary = (
                (
                    st.session_state.route_product_summary_filtered.copy()
                    .groupby(["Registration No"])
                    .agg(
                        n_deliveries=("Number of deliveries", "sum"),
                        n_boxes=("Number of boxes", "sum"),
                        product_types=("Product Name", "unique"),
                    )
                    .rename(
                        columns={
                            "n_deliveries": "Number of deliveries",
                            "n_boxes": "Number of boxes",
                            "product_types": "Products",
                        }
                    )
                )
                .reset_index()
                .merge(results_summary)
                .merge(
                    st.session_state.route_summary[
                        ["Registration No", "Assigned zone numbers"]
                    ]
                )
            )[
                [
                    "Registration No",
                    "Number of deliveries",
                    "Number of boxes",
                    "Total route distance (km)",
                    "Total route travel time (h)",
                    "Assigned zone numbers",
                    "Products",
                    "geometry",
                ]
            ]
            st.session_state.tsp_route_summary = tsp_route_summary
            st.session_state.assigned_stops = assigned_stops

    if "tsp_route_summary" in st.session_state:
        st.subheader("Route summary")
        st.dataframe(st.session_state.tsp_route_summary.drop(columns=["geometry"]))
        st.subheader("Sequenced orders")
    if "assigned_stops" in st.session_state:
        vehicle_filter = st.multiselect(
            "Select vehicles for inspection and download:",
            st.session_state.assigned_stops["Registration No"].unique(),
            default=st.session_state.assigned_stops["Registration No"].unique(),
        )
        assigned_vehicle_stops = st.session_state.assigned_stops.loc[
            st.session_state.assigned_stops["Registration No"].isin(vehicle_filter)
        ]
        df_download = assigned_vehicle_stops.copy().rename(
            columns={"route_sequence": "Route sequence"}
        )
        df_download["Site Latitude"] = df_download["latitude"]
        df_download["Site Longitude"] = df_download["longitude"]
        df_download = df_download[
            st.session_state.input_columns.tolist() + ["geocoded", "Route sequence"]
        ]

        st.dataframe(df_download)
        df_xlsx = to_excel(df_download)
        st.download_button(
            "Press to Download",
            data=df_xlsx,
            file_name=f"{st.session_state.file_name.replace('.xlsx', '')}_sequenced.xlsx",
        )
