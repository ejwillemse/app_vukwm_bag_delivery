import pandas as pd
import streamlit as st

import app_vukwm_bag_delivery.aggregates as aggregates
from app_vukwm_bag_delivery.download_to_excel import to_excel
from app_vukwm_bag_delivery.google_geocode import geocode_addresses
from app_vukwm_bag_delivery.osrm_tsp import sequence_routes
from check_password import check_password
from generate_routes import start_routing
from routing_job_selection import stop_data_summary
from select_vehicles import select_vehicles
from upload_file_geocode import upload_and_geocode_file

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("VUKWM Bag delivery routing")

if check_password():
    upload_and_geocode_file()
    stop_data_summary()
    select_vehicles()
    start_routing()
