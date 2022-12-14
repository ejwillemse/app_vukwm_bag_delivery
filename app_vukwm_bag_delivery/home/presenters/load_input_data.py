import streamlit as st

from app_vukwm_bag_delivery.models.pipelines.process_input_data import (
    download_s3_file,
    raw_input_processing,
)


def load_raw_data():
    (excel_data, geo_data, _) = download_s3_file.return_routing_files(
        st.secrets["bucket"],
        st.secrets["dev_s3"],
        st.secrets["s3_input_paths"]["raw_user_input"],
        st.secrets["s3_input_paths"]["geocoded_input"],
        st.secrets["s3_input_paths"]["unassigned_stops_input"],
    )
    st.session_state.data_01_raw = {
        "raw_input": excel_data,
        "unassigned_stops": geo_data,
    }
    st.session_state.stop_data = geo_data.copy()


def convert_intermediate_data():
    unassigned_jobs = raw_input_processing.process_input_data(
        st.session_state.data_01_raw["unassigned_stops"]
    )
    unassigned_stops = raw_input_processing.combine_orders(unassigned_jobs)
    st.session_state.data_02_intermediate = {
        "unassigned_jobs": unassigned_jobs,
        "unassigned_stops": unassigned_stops,
    }


def load_data():
    load_raw_data()
    convert_intermediate_data()
