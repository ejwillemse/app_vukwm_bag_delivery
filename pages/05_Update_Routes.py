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
from app_vukwm_bag_delivery.util_presenters import \
    save_session as save_global_session
from app_vukwm_bag_delivery.util_presenters.check_password import \
    check_password
from app_vukwm_bag_delivery.view_routes.generate_route_display import (
    return_all_stops_display, return_assigned_stops_display)

# create logger


def set_page_config():
    st.title("Update routes")


if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()


def view_instructions():
    with st.expander("Instructions"):
        st.markdown("### Basic orientation")
        st.video(st.secrets["videos"]["video8"])
        st.markdown("### Different ways to select stops")
        st.markdown(
            "When selecting stops from the table, after selecting the stops by checking their boxes, click on `Update` right above the table to activate the selection."
        )
        st.video(st.secrets["videos"]["video9"])
        st.markdown("### Selecting stops and changing them to a different route")
        st.markdown(
            "Each time a selection is confirmed, the optimal individual sequence for the affected routes are re-calculated."
        )
        st.video(st.secrets["videos"]["video10"])
        st.markdown("### Saving updates")
        st.markdown(
            "Click on `Save edits` to make the changes permenant. Note that the edits will be lost when the routes are generated from `Generate Routes`. Click on `Restart` to undo all the edits made since the last save."
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
    if clicked1:
        process_assigned_stops.update_unsused_routes()
        process_assigned_stops.update_unserviced_stops()
        process_assigned_stops.update_assigned_stops()


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
        st.session_state.data = None
        st.session_state.edit_routes = None
        update_routes_test_widget.initialize_state(clear_all=True)
        st.experimental_rerun()


set_page_config()
save_global_session.save_session()
check_previous_steps_completed()
view_instructions()
process_assigned_stops.initiate_data()

with st.expander("View route KPIs and changes from manual updates", True):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("Fleet KPIs")
        st.dataframe(st.session_state.edit_routes["kpis"], use_container_width=True)
    with c2:
        st.markdown("KPI changes from manual updates")
        st.dataframe(
            st.session_state.edit_routes["kpi_difference"], use_container_width=True
        )


st.session_state.edit_data = {"original_data": return_all_stops_display()}
update_routes_test_widget.main()
