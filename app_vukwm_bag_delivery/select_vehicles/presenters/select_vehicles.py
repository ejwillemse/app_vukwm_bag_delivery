import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


def return_vehicle_grid(df):
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
        "Capacity (#boxes)",
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


def save_vehicle_selection(df):
    if df.shape[0] > 0:
        st.session_state.data_02_intermediate["unassigned_routes"] = df.copy()
