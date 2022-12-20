import pandas as pd
import streamlit as st
import app_vukwm_bag_delivery.aggregates as aggregates
import streamlit as st
import pandas as pd
from app_vukwm_bag_delivery.google_geocode import geocode_addresses
import app_vukwm_bag_delivery.aggregates as aggregates
from app_vukwm_bag_delivery.osrm_tsp import sequence_routes
from app_vukwm_bag_delivery.download_to_excel import to_excel
from check_password import check_password
from generate_routes import start_routing

from upload_file_geocode import upload_and_geocode_file
from select_vehicles import select_vehicles
from routing_job_selection import stop_data_summary

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
