import datetime
import logging
import logging.config
import sys

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

import app_vukwm_bag_delivery.generate_routes.presenters.extract_high_level_summary as extract_high_level_summary
import app_vukwm_bag_delivery.update_routes.process_assigned_data as process_assigned_stops
import app_vukwm_bag_delivery.update_routes.update_routes_test_widget as update_routes_test_widget
import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.util_presenters.check_password import check_password
from app_vukwm_bag_delivery.view_routes.generate_route_display import (
    return_all_stops_display,
    return_assigned_stops_display,
)
from app_vukwm_bag_delivery.view_routes.generate_route_gant import return_gant
from app_vukwm_bag_delivery.view_routes.generate_route_map import return_map

# create logger


def set_page_config():
    # st.set_page_config(
    #     layout="wide",
    #     page_title="Update routes",
    #     initial_sidebar_state="expanded",
    # )
    st.title("Update routes")


if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line


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
    stop = False
    if not return_session_status.check_intermediate_unassigned_jobs_loaded():
        st.warning("Job data not loaded during session. Please go back to `Home` page")
        stop = True  # App won't run anything after this line
    if not return_session_status.check_intermediate_unassigned_fleet_loaded():
        st.warning(
            "Vehicles have not yet been configured and selected. Please go to the `Select Vehicles` page."
        )
        stop = True
    if not return_session_status.check_route_generation_completed():
        st.warning(
            "Routes have not yet been generated. Please go to the `Generate Routes` page."
        )
        stop = True  # App won't run anything after this line
    if stop:
        st.stop()


if "restarts" not in st.session_state:
    st.session_state["restarts"] = 0


if "event_clock" not in st.session_state:
    st.session_state["event_clock"] = datetime.datetime.now()


def save_session():
    st.header("Save changes")
    clicked1 = st.button("Click here to save edits")


def restart_all():
    st.header("Restart session")
    clicked2 = st.button(
        "Click here to restart editing session. ALL EDITS WILL BE LOST."
    )
    if clicked2:
        logging.info(
            "\n\n\nlogging::::restarting editor sessions-----------------------"
        )
        update_routes_test_widget.reset_state_callback()
        update_routes_test_widget.initialize_state(clear_all=True)
        st.experimental_rerun()


set_page_config()
check_previous_steps_completed()
view_instructions()
process_assigned_stops.initiate_data()

with st.expander("View route KPIs", True):
    st.dataframe(
        st.session_state.edit_routes["kpi_difference"], use_container_width=True
    )


st.session_state.edit_data = {"original_data": return_all_stops_display()}
update_routes_test_widget.main()
save_session()
restart_all()
# side_bar_status = side_bar_progress.view_sidebar()
# side_bar_progress.update_side_bar(side_bar_status)
