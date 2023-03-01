import logging

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

log = logging.getLogger(__name__)


def gen_time_range(min=0, max=25):
    if max > 24:
        max = 24
        add_midnight = True
    else:
        add_midnight = False
    times = []
    for i in range(min, max):
        for j in [0, 1]:
            times.append(f"{str(i).zfill(2)}:{str(30 * j).zfill(2)}:00")
    if add_midnight is True:
        times.append("23:59:59")
    return times


VEHICLE_COLUMNS_DATA_TYPE = {
    "": "bool",
    "Vehicle id": "string",
    "Type": pd.CategoricalDtype(categories=["Van", "Bicycle"], ordered=True),
    "Capacity (kg)": "int64",
    "Max stops": "int64",
    "Depot": pd.CategoricalDtype(categories=["Mandela Way", "Soho"], ordered=True),
    "Shift start time": pd.CategoricalDtype(categories=gen_time_range(), ordered=True),
    "Shift end time": pd.CategoricalDtype(categories=gen_time_range(), ordered=True),
    "Average TAT per delivery (min)": "float64",
    "Stock replenish duration (min)": "float64",
    "Dedicated transport zones": "string",
    "Cost (£) per km": "float64",
    "Cost (£) per hour": "float64",
    "lat": "float64",
    "lon": "float64",
}


def return_vehicle_grid(df):
    log.warning(
        "Using `return_vehicle_grid` is deprecated. Please use `return_vehicle_edited` instead."
    )
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(
        "multiple",
        use_checkbox=True,
        groupSelectsChildren="Group checkbox select children",
    )
    gb.configure_pagination(enabled=True)
    gb.configure_side_bar()
    gb.configure_column(
        "Depot",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": ["Soho", "Mandela Way"]},
    )
    gb.configure_column(
        "Type",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": ["Van", "Bicycle"]},
    )
    gb.configure_column("Dedicated transport zones", editable=True)
    gb.configure_column(
        "lat",
        editable=True,
    )
    gb.configure_column(
        "lon",
        editable=True,
    )
    gb.configure_column(
        "Vehicle id",
        editable=True,
    )
    gb.configure_column(
        "Capacity (kg)",
        editable=True,
    )
    gb.configure_column(
        "Max stops",
        editable=True,
    )
    gb.configure_column(
        "Cost (£) per km",
        editable=True,
    )
    gb.configure_column(
        "Cost (£) per hour",
        editable=True,
    )
    gb.configure_column(
        "Shift start time",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={
            "values": [
                "05:00:00",
                "06:00:00",
                "07:00:00",
                "08:00:00",
                "09:00:00",
                "10:00:00",
                "11:00:00",
                "12:00:00",
                "13:00:00",
                "14:00:00",
                "15:00:00",
                "16:00:00",
                "17:00:00",
                "18:00:00",
                "19:00:00",
                "20:00:00",
                "21:00:00",
                "22:00:00",
            ]
        },
    )
    gb.configure_column(
        "Shift end time",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={
            "values": [
                "05:00:00",
                "06:00:00",
                "07:00:00",
                "08:00:00",
                "09:00:00",
                "10:00:00",
                "11:00:00",
                "12:00:00",
                "13:00:00",
                "14:00:00",
                "15:00:00",
                "16:00:00",
                "17:00:00",
                "18:00:00",
                "19:00:00",
                "20:00:00",
                "21:00:00",
                "22:00:00",
            ]
        },
    )
    gb.configure_column(
        "Average TAT per delivery (min)",
        editable=True,
    )
    gb.configure_column("Stock replenish duration (min)", editable=True)

    gridOptions = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        data_return_mode="AS_INPUT",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        columns_auto_size_mode="FIT_CONTENTS",
        fit_columns_on_grid_load=False,
        theme="streamlit",  # Add theme color to the table
        enable_enterprise_modules=False,
        width="100%",
        reload_data=False,
    )
    selected = grid_response["selected_rows"]
    selected_df = pd.DataFrame(selected)
    return selected_df


def return_vehicle_edited(df: pd.DataFrame) -> pd.DataFrame:
    new_columns = [""] + df.columns.tolist()
    df = df.assign(**{"": False})[new_columns].astype(VEHICLE_COLUMNS_DATA_TYPE)
    selected_df = st.experimental_data_editor(df, num_rows="dynamic")
    selected_df = selected_df.rename(columns={"": "Selected"})
    selected_df = selected_df[selected_df["Selected"] == True].copy()
    return selected_df


def save_vehicle_selection(df: pd.DataFrame) -> None:
    if df.shape[0] > 0:
        st.session_state.data_02_intermediate["unassigned_routes"] = df.copy()
