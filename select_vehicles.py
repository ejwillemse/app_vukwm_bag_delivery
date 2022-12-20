import streamlit as st
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid


def select_vehicles():
    st.subheader("Select vehicles")
    with st.expander("Instructions"):
        st.markdown(
            """
        Step 1: Upload a bag-delivery excel file.\n
        Step 2: The application will then geocode missing latitude and longitude coordinates using google-maps and show the results.\n
        Step 3: Choose a delivery day to generate routes for, taking into acount that stops already have to be assigned to vehicles.\n
        Step 4: Select one or more vehicles to generate routes for. We recommend choosing all assigned vehicles.\n
        Step 5: Click on the generate route button, and job sequences for each vehicle will be generated.\n
        Step 6: Download the results as an Excel file.
        """
        )
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

    vehicle_df = pd.DataFrame(
        {
            "Vehicle id": vehicle_ids,
            "Type": vehicle_type,
            "Capacity (#boxes)": capacity,
            "Depot": depot,
            "Dedicated transport zones": dedicated_transport_zones,
            "lat": lat,
            "lon": lon,
        }
    )
    data = vehicle_df.copy()

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

    data = grid_response["data"]
    selected = grid_response["selected_rows"]
    select_vehicles = pd.DataFrame(
        selected
    )  # Pass the selected rows to a new dataframe df

    if select_vehicles.shape[0] == 0:
        st.write(
            "No vehicles were selected so it's assumed that all are available for routing"
        )
        select_vehicles = vehicle_df
    else:
        st.write("The following vehicles were selected for routing:")
        select_vehicles = select_vehicles.drop(columns=["_selectedRowNodeInfo"])
        st.write(select_vehicles)
    st.session_state.fleet = select_vehicles.copy()
