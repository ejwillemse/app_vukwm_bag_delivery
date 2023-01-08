import pandas as pd
import streamlit as st

import app_vukwm_bag_delivery.aggregates as aggregates
import app_vukwm_bag_delivery.presenters.load_input_data as load_input_data
from app_vukwm_bag_delivery.download_to_excel import to_excel
from app_vukwm_bag_delivery.generate_routes import start_routing
from app_vukwm_bag_delivery.google_geocode import geocode_addresses
from app_vukwm_bag_delivery.osrm_tsp import sequence_routes
from app_vukwm_bag_delivery.return_session_staus import (
    return_side_bar,
    return_side_short,
)
from app_vukwm_bag_delivery.select_vehicles import select_vehicles
from check_password import check_password
from routing_job_selection import stop_data_summary
from upload_file_geocode import upload_and_geocode_file

st.set_page_config(
    layout="wide",
    page_title="Home",
    initial_sidebar_state="expanded",
)

st.title("Bag delivery routing")

if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line


st.sidebar.header("Session status")
status_text = st.sidebar.empty()
status_text.markdown(return_side_short())

with st.expander("Instructions"):
    st.markdown(
        """
    Perform the following steps to edit vehicle information and select the vehicles to be routed. If no vehicles are selected, it is assumed that the entire fleet is available for routing.

    * Step 1: Inspect the vehicle information in the table.
    * Step 2: Edit the vehicle informaiton where required.
    * Step 3: Select active vehicles by clicking on the boxes next to the vehicle ID.
    * Step 4: Click on "Update" to load the vehicles.
    """
    )

if "stop_data" not in st.session_state:
    with st.spinner(f"Initiating session and loading data..."):
        load_input_data.load_data()

st.markdown(return_side_bar())
status_text.markdown(return_side_short())
# upload_and_geocode_file()
# stop_data_summary()
# select_vehicles()
# start_routing()
