import logging

import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

from app_vukwm_bag_delivery.update_routes.process_assigned_data import (
    return_filtered_route_id_data,
)

ROUTE_ID = "Vehicle Id"
TABLE_HEIGHT = 500


def selection_dataframe() -> None:
    logging.info(f"logging::::selecting dataframe")
    data = return_filtered_route_id_data(ROUTE_ID).copy()
    data = data.loc[data["Activity type"] != "DEPOT_START_END"].copy()
    data = data.sort_values([ROUTE_ID, "Stop sequence"])
    data = data.assign(temp_index=np.arange(data.shape[0]))

    pre_selected_rows = data.loc[data["selected"]]["temp_index"].tolist()

    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_pagination(
        paginationAutoPageSize=False, paginationPageSize=data.shape[0]
    )  # Add pagination
    gb.configure_column("index", headerCheckboxSelection=True)
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_selection(
        "multiple",
        use_checkbox=True,
        groupSelectsChildren="Group checkbox select children",
        pre_selected_rows=pre_selected_rows,
    )  # Enable multi-row selection
    gridOptions = gb.build()

    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode="AS_INPUT",
        update_mode="MANUAL",
        columns_auto_size_mode="FIT_CONTENTS",
        fit_columns_on_grid_load=False,
        theme="streamlit",  # Add theme color to the table
        enable_enterprise_modules=True,
        height=TABLE_HEIGHT,
        width="100%",
        reload_data=False,
    )
    selected = grid_response["selected_rows"]
    selected_df = pd.DataFrame(selected)
    if selected_df.shape[0] > 0:
        logging.info(f"logging::::data selected for update")
        selected_index = set(selected_df["index"].tolist())
    else:
        logging.info(f"logging::::no data selected for update")
        selected_index = set()
    st.session_state.current_query["aggrid_select"] = selected_index
