import streamlit as st

import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
from app_vukwm_bag_delivery.models.pipelines.convert_input_data import (
    convert_fleet,
    convert_jobs,
)


def add_time_windows(df):
    time_windows = st.session_state.data_02_intermediate["unassigned_stops_tw"].copy()
    if return_session_status.check_time_windows_update():
        updated_time_windows = st.session_state.data_02_intermediate[
            "save_updated_time_windows"
        ]
        updated = time_windows["Site Bk"].isin(updated_time_windows["Site Bk"])
        time_windows.loc[
            updated, ["Delivery open time", "Delivery close time"]
        ] = updated_time_windows[updated]
    time_windows = time_windows.assign(
        stop_id=time_windows["Site Bk"].astype(str),
        time_window_start=time_windows["Delivery open time"],
        time_window_end=time_windows["Delivery close time"],
    )[["stop_id", "time_window_start", "time_window_end"]]
    df = df.drop(columns=["time_window_start", "time_window_end"]).merge(
        time_windows, left_on="stop_id", right_on="stop_id", validate="1:1"
    )
    return df


def process_input_data():
    unassigned_routes = convert_fleet.convert_fleet(
        st.session_state.data_02_intermediate["unassigned_routes"]
    )

    if return_session_status.check_jobs_excluded_from_route():
        remove_stops = st.session_state.data_02_intermediate[
            "user_confirmed_removed_unassigned_stops"
        ]
    else:
        remove_stops = None

    unassigned_stops = convert_jobs.unassigned_stops_convert(
        st.session_state.data_02_intermediate["unassigned_jobs"], remove_stops
    )
    unassigned_stops = add_time_windows(unassigned_stops)
    unassigned_stops = convert_jobs.add_skills(unassigned_stops, unassigned_routes)

    locations, unassigned_stops, unassigned_routes = convert_jobs.create_locations(
        unassigned_stops, unassigned_routes
    )
    st.session_state.data_03_primary = {"locations": locations}
    st.session_state.data_03_primary["unassigned_stops"] = unassigned_stops
    st.session_state.data_03_primary["unassigned_routes"] = unassigned_routes
