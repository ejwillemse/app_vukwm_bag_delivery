import sys

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, "./")

from app_vukwm_bag_delivery.views.render_unassigned_stops_map import (
    return_order_map_html,
)
from app_vukwm_bag_delivery.views.summarise_inputs import calc_route_product_summary

STOP_VIEW_COLUMNS = [
    "Ticket No",
    "Customer Bk",
    "Site Bk",
    "Site Name",
    "Transport Area Code",
    "Product Name",
    "Quantity",
    "Created Date",
    "Required Date",
    "Notes",
    "on hold",
    "Schedule ID",
    "Scheduled Date",
    "Completed Date",
    "Registration No",
    "Site Address1",
    "Site Address2",
    "Site Address3",
    "Site Address4",
    "Site Address5",
    "Site Post Town",
    "Site Post Code",
    "Site Latitude",
    "Site Longitude",
    "Site Address",
    "transport_area_number",
    "Product description",
    "Total boxes",
]
STOP_VIEW_COLUMNS_RENAME = {"transport_area_number": "Transport Area"}


def set_page_config():
    st.set_page_config(
        layout="wide",
        page_title="Review Jobs Data",
        initial_sidebar_state="expanded",
    )
    st.title("Review delivery jobs")


def view_instructions():
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


def check_previous_steps_completed():
    if "stop_data" not in st.session_state:
        st.warning("Job data not loaded during session. Please go back the `Home` page")
        st.stop()  # App won't run anything after this line


def view_product_summary():
    st.header("Summary per transport area")
    st.write(
        calc_route_product_summary(
            st.session_state.data_02_intermediate["unassigned_stops"]
        )
    )


def view_all_stops():
    with st.expander("View all stops"):
        st.write(
            st.session_state.data_02_intermediate["unassigned_stops"][
                STOP_VIEW_COLUMNS
            ].rename(columns=STOP_VIEW_COLUMNS_RENAME)
        )


def view_stops_map():
    html = return_order_map_html(
        st.session_state.data_02_intermediate["unassigned_stops"]
    )
    components.html(html, height=500)
