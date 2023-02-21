import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, ColumnsAutoSizeMode, GridOptionsBuilder, GridUpdateMode

from app_vukwm_bag_delivery.util_presenters.filters.filter_dataframe import (
    filter_df_widget,
)

INSPECT_ORDER = [
    "Site Bk",
    "Site Name",
    "Delivery open time",
    "Delivery close time",
    "Typical open time",
    "Typical close time",
    "Notes",
    "Transport Area Code",
    "Unknown open times",
    "Site Address",
    "Original delivery open time",
    "Original delivery close time",
]


def gen_time_range():
    times = []
    for i in range(6, 20):
        for j in [0, 1]:
            times.append(f"{str(i).zfill(2)}:{str(30 * j).zfill(2)}:00")
    return times


def return_timewindow_grid(df):
    gb = GridOptionsBuilder.from_dataframe(df[INSPECT_ORDER])
    gb.configure_pagination(
        enabled=True, paginationAutoPageSize=False, paginationPageSize=15
    )  # Add pagination
    gb.configure_side_bar()
    gb.configure_column(
        "Delivery open time",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": gen_time_range()},
    )
    gb.configure_column(
        "Delivery close time",
        editable=True,
        cellEditor="agSelectCellEditor",
        cellEditorParams={"values": gen_time_range()},
    )
    gridOptions = gb.build()
    grid_response = AgGrid(
        df[INSPECT_ORDER],
        gridOptions=gridOptions,
        data_return_mode="AS_INPUT",
        update_mode=GridUpdateMode.VALUE_CHANGED,
        columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
        fit_columns_on_grid_load=False,
        theme="streamlit",  # Add theme color to the table
        enable_enterprise_modules=True,
        width="100%",
        reload_data=False,
    )
    selected = grid_response["data"]
    selected_df = pd.DataFrame(selected)
    return selected_df


def create_update_key(df):
    df = df.assign(
        update_key=df["Site Bk"].astype(str)
        + "__"
        + df["Delivery open time"]
        + "__"
        + df["Delivery close time"]
    )
    return df


def update_timewindows_selection():
    orig_df = st.session_state.data_02_intermediate["unassigned_stops_tw"]
    orig_df = orig_df.assign(
        **{
            "Original delivery open time": orig_df["Delivery open time"],
            "Original delivery close time": orig_df["Delivery close time"],
        }
    )
    orig_df = create_update_key(orig_df)
    if (
        "updated_time_windows" not in st.session_state.data_02_intermediate
        or st.session_state.data_02_intermediate["updated_time_windows"].shape[0] == 0
    ):
        st.session_state.data_02_intermediate["updated_time_windows"] = orig_df
    updated_df = st.session_state.data_02_intermediate["updated_time_windows"]

    updated_df = filter_df_widget(updated_df, key="update_timewindows_selection")
    modify = st.radio(
        "Select specific or all filtered stops for exclusion",
        ["View time-windows", "Update time-windows"],
    )
    if modify == "Update time-windows":
        updated_df = return_timewindow_grid(updated_df)
        updated_df = create_update_key(updated_df)
        show_updated_time_windows = updated_df.loc[
            ~updated_df["update_key"].isin(orig_df["update_key"])
        ].drop(columns=["update_key"])
    else:
        st.write(updated_df)
        show_updated_time_windows = pd.DataFrame()
    return show_updated_time_windows
