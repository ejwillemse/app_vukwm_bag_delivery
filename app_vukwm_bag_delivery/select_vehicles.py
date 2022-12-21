import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder


def return_vehicle_default():
    vehicle_ids = ["W01", "W02", "W03", "W04", "W05", "W06"]
    vehicle_type = ["Van", "Van", "Van", "Bicycle", "Van", "Van"]
    depot = [
        "Mandela Way",
        "Mandela Way",
        "Mandela Way",
        "Soho",
        "Mandela Way",
        "Mandela Way",
    ]
    lon = [-0.07962670, -0.07962670, -0.07962670, -0.13748230, -0.07962670, -0.07962670]
    lat = [51.49175400, 51.49175400, 51.49175400, 51.51358620, 51.49175400, 51.49175400]
    capacity = [500, 500, 500, 25, 500, 500]
    dedicated_transport_zones = [None, None, None, 2, None, None]
    cost_per_km = [1, 1, 1, 0.5, 1, 1]
    cost_per_h = [10, 10, 10, 10, 10, 10]
    shift_start_time = ["09:00"] * 6
    ave_duration = [5] * 6

    vehicle_df = pd.DataFrame(
        {
            "Vehicle id": vehicle_ids,
            "Type": vehicle_type,
            "Capacity (#boxes)": capacity,
            "Depot": depot,
            "Shift start time": shift_start_time,
            "Average TAT per delivery (min)": ave_duration,
            "Dedicated transport zones": dedicated_transport_zones,
            "Cost (£) per km": cost_per_km,
            "Cost (£) per hour": cost_per_h,
            "lat": lat,
            "lon": lon,
        }
    )
    return vehicle_df


def return_vehicle_grid(data):
    gb = GridOptionsBuilder.from_dataframe(data)
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
                "07:00",
                "08:00",
                "09:00",
                "10:00",
                "11:00",
                "12:00",
                "13:00",
                "14:00",
                "15:00",
                "16:00",
                "17:00",
                "18:00",
            ]
        },
    )
    gb.configure_column(
        "Average TAT per delivery (minutes)",
        editable=True,
    )

    gridOptions = gb.build()

    MAX_HEIGHT = 800
    ROW_HEIGHT = 40

    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode="AS_INPUT",
        update_mode="MANUAL",
        fit_columns_on_grid_load=False,
        theme="streamlit",  # Add theme color to the table
        enable_enterprise_modules=False,
        height=min(len(data) * ROW_HEIGHT, MAX_HEIGHT),
        width="100%",
        reload_data=True,
        editable=True,
        allow_unsafe_jscode=True,
    )
    return grid_response


def select_vehicles():
    st.write("The following vehicles are available for routing:")
    vehicle_df = return_vehicle_default()
    data = vehicle_df
    grid_response = return_vehicle_grid(data)
    data = grid_response["data"]
    selected = grid_response["selected_rows"]
    select_vehicles = pd.DataFrame(
        selected
    )  # Pass the selected rows to a new dataframe df

    if select_vehicles.shape[0] > 0:
        select_vehicles = select_vehicles.drop(columns=["_selectedRowNodeInfo"])
        st.session_state.fleet = select_vehicles.copy()

    if "fleet" in st.session_state:
        st.write(
            "The following vehicles were selected for routing during this session:"
        )
        st.write(st.session_state.fleet)


if __name__ == "__main__":
    print(return_vehicle_default().columns)
