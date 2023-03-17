import logging

import pandas as pd
import streamlit as st

from app_vukwm_bag_delivery.home.presenters.load_input_data import reload_data

log = logging.getLogger(__name__)

STOP_COLUMN_TYPES = {
    "Selected": "bool",
    "Ticket No": "string",
    "Customer Bk": "string",
    "Site Bk": "string",
    "Site Name": "string",
    "Transport Area Code": "string",
    "Product Name": object,
    "Quantity": "int64",
    "Order Weight (kg)": "float64",
    "Created Date": "string",
    "Required Date": "string",
    "Notes": "string",
    "on hold": "string",
    "Schedule ID": "string",
    "Scheduled Date": "string",
    "Completed Date": "string",
    "Registration No": "string",
    "Site Address1": "string",
    "Site Address2": "string",
    "Site Address3": "string",
    "Site Address4": "string",
    "Site Address5": "string",
    "Site Post Town": "string",
    "Site Post Code": "string",
    "Site Latitude": "float64",
    "Site Longitude": "float64",
    "Site Address": "string",
    "Transport Area": "int64",
    "skills": "string",
    # "Service duration (seconds)": "float64",
    # "Time window start": "category",
    # "Time window end": "category",
    "Product Alias": "string",
    "Batches per box": "int64",
    "Weight per batch (kg)": "int64",
    "Weight per box (kg)": "int64",
    "completed": "bool",
    # "stop_id": "category",
    # "activity_type": "category",
    "weight_merge_key": "string",
    # "demand": "float64",
}
STOP_VIEW_COLUMNS_RENAME = {"transport_area_number": "Transport Area"}
STOP_VIEW_COLUMNS_REVERSE_NAME = {}

VEHICLE_COLUMNS_DATA_TYPE = {
    "": "bool",
    "Vehicle id": "string",
    "Type": pd.CategoricalDtype(categories=["Van", "Bicycle"], ordered=True),
    "Capacity (kg)": "int64",
    "Max stops": "int64",
    "Depot": pd.CategoricalDtype(categories=["Mandela Way", "Soho"], ordered=True),
    "Average TAT per delivery (min)": "float64",
    "Stock replenish duration (min)": "float64",
    "Dedicated transport zones": "string",
    "Cost (£) per km": "float64",
    "Cost (£) per hour": "float64",
    "lat": "float64",
    "lon": "float64",
}


def edit_data():
    data = st.session_state.data_02_intermediate["unassigned_jobs_editable"]
    data = data.astype(STOP_COLUMN_TYPES)
    edited_data = st.experimental_data_editor(
        data[STOP_COLUMN_TYPES.keys()][data.columns]
    )
    unknown_locations = edited_data.loc[
        edited_data["Site Latitude"].isna() | edited_data["Site Latitude"] == 0
    ]

    if unknown_locations.shape[0] > 0:
        st.warning(
            "The following locations are not recognised. Please manually update their latitude and longitude values."
        )
        st.write(unknown_locations)

    save_reload = st.button("Save edits and selections")
    st.warning(
        "All data edits, as well as generated and edited routes will be lost. This includes time-window edits."
    )
    exluded_jobs = edited_data.loc[~edited_data["Selected"]]
    if save_reload is True:
        st.session_state.data_02_intermediate[
            "unassigned_jobs_editable"
        ] = edited_data.copy()
        st.session_state.data_02_intermediate[
            "user_confirmed_removed_unassigned_stops"
        ] = exluded_jobs.copy()
        st.session_state.data_02_intermediate[
            "removed_unassigned_stops"
        ] = exluded_jobs.copy()
        reload_data()
        # st.experimental_rerun()

    if exluded_jobs.shape[0] > 0:
        st.markdown(
            "The following jobs have been deselected and will not be included in the routing."
        )
        st.write(exluded_jobs)
