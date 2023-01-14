import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def return_selected():
    if "removed_unassigned_stops" not in st.session_state.data_02_intermediate:
        selected = pd.DataFrame()
        st.session_state.data_02_intermediate["removed_unassigned_stops"] = selected
    else:
        selected = st.session_state.data_02_intermediate["removed_unassigned_stops"]
    return selected


def return_selected_stops_ids():
    if "removed_unassigned_stops" not in st.session_state.data_02_intermediate:
        pre_selected = []
    elif (
        st.session_state.data_02_intermediate["removed_unassigned_stops"].shape[0] == 0
    ):
        pre_selected = []
    else:
        pre_selected = st.session_state.data_02_intermediate[
            "removed_unassigned_stops"
        ]["Ticket No"].values
    return pre_selected


def update_select_remove_dataframe(selected_df) -> None:
    if "removed_unassigned_stops" not in st.session_state.data_02_intermediate:
        st.session_state.data_02_intermediate[
            "removed_unassigned_stops"
        ] = pd.DataFrame()
    else:
        st.session_state.data_02_intermediate["removed_unassigned_stops"] = selected_df


def select_remove_dataframe(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(
        enabled=True, paginationAutoPageSize=False, paginationPageSize=15
    )  # Add pagination
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_selection(
        "multiple",
        use_checkbox=True,
        groupSelectsChildren="Group checkbox select children",
        # pre_selected_rows=pre_selected_rows, # this causes double selection issues...
    )  # Enable multi-row selection
    gridOptions = gb.build()

    # the page is restarted each time AgGrid gets a response, hence causing the issues
    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        data_return_mode="AS_INPUT",
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        columns_auto_size_mode="FIT_CONTENTS",
        fit_columns_on_grid_load=False,
        theme="streamlit",  # Add theme color to the table
        enable_enterprise_modules=False,
        width="100%",
        reload_data=False,
    )
    selected = grid_response["selected_rows"]
    selected_df = pd.DataFrame(selected)
    update_select_remove_dataframe(selected_df)
