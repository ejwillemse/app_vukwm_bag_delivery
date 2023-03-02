import streamlit as st

from app_vukwm_bag_delivery.models.pipelines.process_input_data import (
    download_s3_file,
    raw_input_processing,
)
from app_vukwm_bag_delivery.models.pipelines.process_input_data.raw_input_processing import (
    assign_bicycle_skills,
    extract_transport_number,
)
from app_vukwm_bag_delivery.review_jobs_data.presenters.inspect_timewindows import (
    return_time_window_info,
)
from app_vukwm_bag_delivery.util_views.return_session_status import (
    check_intermediate_unassigned_fleet_loaded,
    check_manual_edits,
    check_route_generation_completed,
    check_route_sheets_generated,
    check_time_windows_update,
    check_unserviced_stops,
    check_unserviced_stops_in_routes,
    check_unused_routes,
)


def load_raw_data():
    (
        excel_data,
        geo_data,
        _,
        open_time_data,
        bag_weights,
    ) = download_s3_file.return_routing_files(
        st.secrets["bucket"],
        st.secrets["dev_s3"],
        st.secrets["s3_input_paths"]["raw_user_input"],
        st.secrets["s3_input_paths"]["geocoded_input"],
        st.secrets["s3_input_paths"]["unassigned_stops_input"],
        st.secrets["s3_input_paths"]["opening_time_input"],
        st.secrets["s3_input_paths"]["bag_weights"],
    )
    st.session_state.data_01_raw = {
        "raw_input": excel_data,
        "unassigned_stops": geo_data,
        "open_time": open_time_data,
        "bag_weights": bag_weights,
    }
    st.session_state.stop_data = geo_data.copy()


def convert_intermediate_data():
    unassigned_jobs = raw_input_processing.process_input_data(
        st.session_state.data_01_raw["unassigned_stops"],
        st.session_state.data_01_raw["raw_input"],
        st.session_state.data_01_raw["bag_weights"],
    )
    unassigned_stops = raw_input_processing.combine_orders(unassigned_jobs)
    columns = ["Selected"] + unassigned_jobs.columns.tolist()
    unassigned_jobs = unassigned_jobs.assign(**{"Selected": True})[columns]
    st.session_state.data_02_intermediate = {
        "unassigned_jobs": unassigned_jobs.copy(),
        "unassigned_jobs_editable": unassigned_jobs.copy(),
        "unassigned_stops": unassigned_stops.copy(),
    }


def reload_intermediate_data():
    unassigned_jobs = st.session_state.data_02_intermediate[
        "unassigned_jobs_editable"
    ].copy()
    unassigned_jobs = extract_transport_number(unassigned_jobs)
    unassigned_jobs = assign_bicycle_skills(unassigned_jobs)
    unassigned_stops = raw_input_processing.combine_orders(unassigned_jobs)
    st.session_state.data_02_intermediate["unassigned_jobs"] = unassigned_jobs.copy()
    st.session_state.data_02_intermediate[
        "unassigned_jobs_editable"
    ] = unassigned_jobs.copy()
    st.session_state.data_02_intermediate["unassigned_stops"] = unassigned_stops.copy()


def clear_processed_data():
    if check_intermediate_unassigned_fleet_loaded():
        del st.session_state.data_02_intermediate["unassigned_routes"]
    if check_time_windows_update():
        del st.session_state.data_02_intermediate["time_windows_update"]
    if check_route_generation_completed():
        del st.session_state.data_07_reporting["assigned_stops"]
    if check_unused_routes():
        del st.session_state.data_07_reporting["unused_routes"]
    if check_unserviced_stops():
        del st.session_state.data_07_reporting["unserviced_stops"]
    if check_unserviced_stops_in_routes():
        del st.session_state.data_07_reporting["unserviced_stops_in_routes"]
    if check_manual_edits():
        del st.session_state["routes_manually_edits"]
    if check_route_sheets_generated():
        del st.session_state.data_07_reporting["route_sheet_urls"]


def load_data():
    load_raw_data()
    convert_intermediate_data()
    return_time_window_info()


def reload_data():
    clear_processed_data()
    reload_intermediate_data()
    return_time_window_info()
