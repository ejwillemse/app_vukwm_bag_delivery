import datetime

import numpy as np
import pandas as pd
import streamlit as st

from app_vukwm_bag_delivery.dispatch_routes.excel_download import to_excel
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
    check_new_jobs_added,
    check_route_generation_completed,
    check_route_sheets_generated,
    check_time_windows_update,
    check_unserviced_stops,
    check_unserviced_stops_in_routes,
    check_unused_routes,
)


@st.cache_data
def return_all_jobs():
    path = st.secrets["s3_input_paths"]["raw_user_input"]
    jobs_file = download_s3_file.return_available_files(
        st.secrets["bucket"],
        st.secrets["dev_s3"],
        path,
    )
    return jobs_file


def download_selected_file(selected):
    selected_name = selected[selected["Selected"] == True].iloc[0]["filename"]
    with st.spinner("Preparing file for download..."):
        raw_user_input = st.secrets["s3_input_paths"]["raw_user_input"]
        df_raw = download_s3_file.return_file(
            st.secrets["bucket"],
            st.secrets["dev_s3"],
            st.secrets["s3_input_paths"]["raw_user_input"],
            pd.read_excel,
            st.secrets["s3_input_paths"]["raw_user_input"] + selected_name,
        )
        selected_name = selected_name.replace(".xlsx", ".csv")
        df_geo = download_s3_file.return_file(
            st.secrets["bucket"],
            st.secrets["dev_s3"],
            st.secrets["s3_input_paths"]["geocoded_input"],
            pd.read_csv,
            st.secrets["s3_input_paths"]["geocoded_input"] + selected_name,
        )
        df_raw[["Site Latitude", "Site Longitude"]] = df_geo[
            ["Site Latitude", "Site Longitude"]
        ].values
        df_raw = df_raw.assign(**{"Site Address": df_geo["Site Address"].values})
        df_xlsx = to_excel(df_raw)
    st.download_button(
        label="Download job list as excel file",
        data=df_xlsx,
        file_name=selected_name.replace(".csv", ".xlsx"),
    )


def confirm_select(selected):
    if selected["Selected"].sum() == 1:
        pressed = st.button("Download selected file")
        if pressed:
            download_selected_file(selected)
    elif selected["Selected"].sum() > 1:
        st.warning("Please select only one file to download")


def load_jobs_file():
    path = st.secrets["s3_input_paths"]["raw_user_input"]
    jobs_file = return_all_jobs()
    jobs_file_display = jobs_file.assign(
        filename=jobs_file["filename"].str.replace(path, "", regex=False)
    ).sort_values(["last_modified"], ascending=False)
    jobs_file_display = jobs_file_display.assign(Selected=False)[
        ["Selected"] + jobs_file_display.columns.tolist()
    ]
    selected = st.experimental_data_editor(jobs_file_display)
    confirm_select(selected)


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


def convert_intermediate_data(excel_date_format=True):
    unassigned_jobs = raw_input_processing.process_input_data(
        st.session_state.data_01_raw["unassigned_stops"],
        st.session_state.data_01_raw["raw_input"],
        st.session_state.data_01_raw["bag_weights"],
        excel_date_format=excel_date_format,
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
    if check_new_jobs_added():
        del st.session_state["new_jobs_added"]
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


def upload_data(new_data):
    reload_data()
    st.session_state.data_01_raw["raw_input"] = new_data.copy()
    st.session_state.data_01_raw["unassigned_stops"] = new_data.copy()
    st.session_state.stop_data = new_data.copy()
    convert_intermediate_data(excel_date_format=False)
    return_time_window_info()


def reload_data():
    clear_processed_data()
    reload_intermediate_data()
    return_time_window_info()


def format_add_hoc_data(data, old_data):
    if data["Ticket No"].duplicated().any():
        st.warning(
            "`Ticket No` contains duplicates, please correct, and re-upload the jobs file."
        )
        st.stop()
    if data["Ticket No"].isin(old_data["Ticket No"]).any():
        st.warning(
            "`Ticket No` already exists, please correct, and re-upload the jobs file."
        )
        st.stop()
    date = datetime.datetime.now().strftime("%Y-%m-%d") + " 00:00:00"
    data = data.assign(
        **{
            "Site Bk": [f"ADD HOC {x}" for x in range(len(data))],
            "Customer Bk": "N/A",
            "Created Date": date,
            "Required Date": date,
            "on hold": np.nan,
            "Schedule ID": np.nan,
            "Scheduled Date": np.nan,
            "Completed Date": np.nan,
            "Registration No": np.nan,
        }
    )
    return data


def add_address(data):
    data = data.assign(
        **{
            "Site Address": data["Site Address1"].fillna("")
            + " "
            + data["Site Address2"].fillna("")
            + " "
            + data["Site Address3"].fillna("")
            + " "
            + data["Site Address4"].fillna("")
            + " "
            + data["Site Address5"].fillna("")
            + " "
            + data["Site Post Town"].fillna("")
            + ", "
            + data["Site Post Code"].fillna(""),
        }
    )
    data = data.assign(**{"Site Address": data["Site Address"].str.upper()})
    return data


def add_input_data(new_data):
    old_data = st.session_state.data_01_raw["raw_input"]
    unassigned_stops = st.session_state.data_01_raw["unassigned_stops"]
    old_data = unassigned_stops[old_data.columns].copy()
    new_data = format_add_hoc_data(new_data, old_data)
    new_data = pd.concat([new_data, old_data]).reset_index(drop=True)[old_data.columns]
    new_data = add_address(new_data)
    reload_data()
    st.session_state.data_01_raw["raw_input"] = new_data.copy()
    st.session_state.data_01_raw["unassigned_stops"] = new_data.copy()
    st.session_state.stop_data = new_data.copy()
    convert_intermediate_data(excel_date_format=False)
    return_time_window_info()
