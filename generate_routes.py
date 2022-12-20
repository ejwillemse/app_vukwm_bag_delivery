import streamlit as st
import pandas as pd
from app_vukwm_bag_delivery.osrm_tsp import sequence_routes
import app_vukwm_bag_delivery.hygese_solver as hygese_solver
from st_aggrid import GridOptionsBuilder, AgGrid


def allocate_jobs_per_type(fleet_df, jobs):
    zone_assignment = fleet_df.dropna(subset=["Dedicated transport zones"]).drop(
        columns=["lat", "lon"]
    )
    zone_assignment["Dedicated transport zones"] = zone_assignment[
        "Dedicated transport zones"
    ].astype(int)
    dedicated_jobs = jobs.merge(
        zone_assignment,
        left_on="tansport_area_num",
        right_on="Dedicated transport zones",
    )
    if dedicated_jobs.shape[0] > 0:
        st.markdown(
            f"**Bicycle allocation:** {dedicated_jobs.shape[0]} jobs ({int(dedicated_jobs.shape[0] / jobs.shape[0] * 100)}% of all jobs) will be allocated to the bicycle."
        )
        st.session_state.bicycle_jobs = dedicated_jobs.copy()
        with st.expander("Click here for more info on the bicycle allocation"):
            st.write(dedicated_jobs)
            st.map(dedicated_jobs)
    else:
        st.markdown(
            f"**Bicycle allocation:** {dedicated_jobs.shape[0]} jobs ({int(dedicated_jobs.shape[0] / jobs.shape[0] * 100)}% of all jobs) will be allocated to the bicycle."
        )
        if zone_assignment.shape[0] == 0:
            st.markdown(f"WARNING: the bicycle was not selected for routing.")
        if dedicated_jobs.shape[0] == 0:
            st.markdown(
                f"WARNING: no jobs will be allocated to the bicycle for routing. Jobs within the bicycle zone will be allocated to other vehicles."
            )
    remaining_jobs = jobs.loc[~jobs["Ticket No"].isin(dedicated_jobs["Ticket No"])]
    st.markdown(
        f"**Van allocation:** {remaining_jobs.shape[0]} jobs ({int(remaining_jobs.shape[0] / jobs.shape[0] * 100)}% of all jobs) will be allocated to the vans."
    )
    st.session_state.remaining_jobs = remaining_jobs.copy()
    with st.expander("Click here for more info on the van allocations"):
        st.write(remaining_jobs)
        st.map(remaining_jobs)


def add_depot(df, fleet, vehicle_id):
    depot_stop = (
        fleet.loc[fleet["Vehicle id"] == vehicle_id]
        .iloc[:1][["Depot", "lat", "lon", "Vehicle id"]]
        .rename(columns={"Depot": "Site Name", "lon": "longitude", "lat": "latitude"})
    )
    df_routing = pd.concat([depot_stop, df, depot_stop]).reset_index(drop=True)
    return df_routing


def generate_bicycle_routes():
    if "bicycle_jobs" in st.session_state:
        route_stops = st.session_state.bicycle_jobs.copy().assign(
            vehicle_type="Bicycle"
        )
        fleet = st.session_state.fleet
        vehicle_id = route_stops["Vehicle id"].unique()[0]
        df_routing = add_depot(route_stops, fleet, vehicle_id=vehicle_id)
        with st.spinner(f"Generating delivery sequences for the bicycle..."):
            results = sequence_routes(
                df_routing,
                ports=st.secrets["osrm_ports"][0],
                route_column="Vehicle id",
            )
            gb = GridOptionsBuilder.from_dataframe(results[0])
            gb.configure_pagination(enabled=True)
            gb.configure_side_bar()
            gridOptions = gb.build()
            AgGrid(
                results[0],
                gridOptions=gridOptions,
                fit_columns_on_grid_load=False,
                theme="streamlit",  # Add theme color to the table
                enable_enterprise_modules=True,
                height=500,
                width="100%",
                reload_data=True,
                allow_unsafe_jscode=True,
            )


def generate_van_routes(fleet):
    if "remaining_jobs" in st.session_state:
        jobs = st.session_state.remaining_jobs
        fleet = fleet.loc[fleet["Type"] != "Bicycle"]
        with st.spinner(f"Generating routes for the vans..."):
            assigned_jobs, unassigned_jobs = hygese_solver.generate_routes(jobs, fleet)
            gb = GridOptionsBuilder.from_dataframe(assigned_jobs)
            gb.configure_pagination(enabled=True)
            gb.configure_side_bar()
            gridOptions = gb.build()
            AgGrid(
                assigned_jobs,
                gridOptions=gridOptions,
                fit_columns_on_grid_load=False,
                theme="streamlit",  # Add theme color to the table
                enable_enterprise_modules=True,
                height=500,
                width="100%",
                reload_data=True,
                allow_unsafe_jscode=True,
            )


def generate_routes(fleet, delivery_jobs):
    st.subheader("Generate routes")
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
    allocate_jobs_per_type(fleet, delivery_jobs)


def start_routing():

    if "delivery_jobs" in st.session_state:
        delivery_jobs = st.session_state.delivery_jobs.copy()
    else:
        delivery_jobs = None

    if "fleet" in st.session_state:
        fleet = st.session_state.fleet.copy()
    else:
        fleet = None

    if fleet is not None and delivery_jobs is not None:
        generate_routes(fleet, delivery_jobs)
        if st.button("Generate route sequences"):
            generate_bicycle_routes()
            generate_van_routes(fleet)
