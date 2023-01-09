import sys

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from st_aggrid import AgGrid, GridOptionsBuilder

sys.path.insert(0, "./")

from app_vukwm_bag_delivery.presenters.select_remove_stops import (
    return_selected,
    select_remove_dataframe,
)
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
    "Transport Area",
]
STOP_VIEW_COLUMNS_RENAME = {"transport_area_number": "Transport Area"}


def set_page_config():
    st.set_page_config(
        layout="wide",
        page_title="Review Jobs Data",
        initial_sidebar_state="expanded",
    )
    st.title("Review delivery jobs")


@st.experimental_memo
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


@st.experimental_memo
def view_product_summary():
    with st.expander(" View summary per transport area"):
        st.write(
            calc_route_product_summary(
                st.session_state.data_02_intermediate["unassigned_jobs"]
            )
        )


@st.experimental_memo
def view_all_stops():
    with st.expander("View all stops"):
        st.write(
            st.session_state.data_02_intermediate["unassigned_jobs"].rename(
                columns=STOP_VIEW_COLUMNS_RENAME
            )[STOP_VIEW_COLUMNS]
        )


@st.experimental_memo
def view_stops_map():
    html = return_order_map_html(
        st.session_state.data_02_intermediate["unassigned_stops"]
    )
    components.html(html, height=500)


def confirm_removal():
    pressed = st.button("Click here to save stop EXCLUSIONS")
    if pressed:
        if "removed_unassigned_stops" in st.session_state.data_02_intermediate:
            st.session_state.data_02_intermediate[
                "user_confirmed_removed_unassigned_stops"
            ] = st.session_state.data_02_intermediate["removed_unassigned_stops"].copy()


def view_select_removal_stops() -> None:
    st.header("Select stops to be excluded from routing")
    data = st.session_state.data_02_intermediate["unassigned_jobs"]
    data = data.rename(columns=STOP_VIEW_COLUMNS_RENAME)[STOP_VIEW_COLUMNS]
    select_remove_dataframe(data)
    selected_df = return_selected()
    if selected_df.shape[0] > 0:
        st.write("Currently the following stops will be EXCLUDED for routing.")
        st.write(selected_df[STOP_VIEW_COLUMNS])
        confirm_removal()
    else:
        st.write("Currently all stops will be included for routing.")
