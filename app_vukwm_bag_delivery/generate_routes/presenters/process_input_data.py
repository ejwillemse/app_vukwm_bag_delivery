import streamlit as st

import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
from app_vukwm_bag_delivery.models.pipelines.convert_input_data import (
    convert_fleet,
    convert_jobs,
)


def process_input_data():
    fleet_df = convert_fleet.convert_fleet(
        st.session_state.data_02_intermediate["unassigned_routes"]
    )
    st.session_state.data_03_primary = {"unassigned_routes": fleet_df}

    if return_session_status.check_jobs_excluded_from_route():
        remove_stops = st.session_state.data_02_intermediate[
            "user_confirmed_removed_unassigned_stops"
        ]
    else:
        remove_stops = None

    stop_df = convert_jobs.unassigned_stops_convert(
        st.session_state.data_02_intermediate["unassigned_jobs"], remove_stops
    )

    stop_df = convert_jobs.add_skills(stop_df, fleet_df)
    st.session_state.data_03_primary["unassigned_stops"] = stop_df
