import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

import app_vukwm_bag_delivery.generate_routes.presenters.extract_high_level_summary as extract_high_level_summary
import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.util_presenters.check_password import check_password
from app_vukwm_bag_delivery.view_routes.generate_route_display import (
    return_assigned_stops_display,
)
from app_vukwm_bag_delivery.view_routes.generate_route_gant import return_gant
from app_vukwm_bag_delivery.view_routes.generate_route_map import return_map


def set_page_config():
    st.set_page_config(
        layout="wide",
        page_title="Dispatch routes",
        initial_sidebar_state="expanded",
    )
    st.title("Dispatch and download routes")


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


set_page_config()
side_bar_status = side_bar_progress.view_sidebar()
check_previous_steps_completed()
view_instructions()
side_bar_progress.update_side_bar(side_bar_status)

original_jobs = st.session_state.data_01_raw["raw_input"]
st.write("raw_inputs")
st.write(original_jobs)

unassigned_jobs = st.session_state.data_02_intermediate["unassigned_jobs"]
st.write("unassigned_jobs")
st.write(unassigned_jobs)

if (
    "user_confirmed_removed_unassigned_stops" in st.session_state.data_02_intermediate
    and st.session_state.data_02_intermediate[
        "user_confirmed_removed_unassigned_stops"
    ].shape[0]
    > 0
):
    deselected_jobs = st.session_state.data_02_intermediate[
        "user_confirmed_removed_unassigned_stops"
    ]
else:
    deselected_jobs = pd.DataFrame(columns=unassigned_jobs.columns)
st.write("deselected_jobs")
st.write(deselected_jobs)

assigned_stops = st.session_state.data_07_reporting["assigned_stops"]
st.write("assigned_stops")
st.write(assigned_stops)

unserviced_stops = st.session_state.data_07_reporting["unserviced_stops"]
st.write("unserviced_stops")
st.write(unserviced_stops)


to_scheduled_jobs = (
    original_jobs.loc[
        original_jobs["Ticket No"].isin(unassigned_jobs["Ticket No"])
        & (~original_jobs["Ticket No"].isin(deselected_jobs["Ticket No"]))
    ]
    .drop(columns=["Site Latitude", "Site Longitude"])
    .merge(unassigned_jobs[["Ticket No", "Site Latitude", "Site Longitude"]])
)

st.write("to_scheduled_jobs")
st.write(to_scheduled_jobs)

assigned_jobs = (
    to_scheduled_jobs.assign(**{"Site Bk": to_scheduled_jobs["Site Bk"].astype(str)})
    .merge(
        assigned_stops[["route_id", "vehicle_profile", "arrival_time", "job_sequence"]]
        .rename(
            columns={
                "stop_id": "Site Bk",
                "route_id": "Vehicle Id",
                "vehicle_profile": "Vehicle type",
                "job_sequence": "Visit sequence",
                "arrival_time": "Arrival time",
            }
        )
        .assign(
            **{
                "Site Bk": assigned_stops["stop_id"].astype(str),
                "Vehicle type": assigned_stops["vehicle_profile"].replace(
                    {"auto": "Van", "bicycle": "Bicycle"}
                ),
            }
        ),
        how="left",
    )
    .sort_values(["Vehicle Id", "Visit sequence"])
)
assigned_jobs = assigned_jobs.assign(
    **{"Visit sequence": (assigned_jobs["Visit sequence"] + 1).fillna(0).astype(int)}
)

st.write("assigned_jobs")
st.write(assigned_jobs)
