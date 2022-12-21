import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

import app_vukwm_bag_delivery.hygese_solver as hygese_solver
import app_vukwm_bag_delivery.return_routes as return_routes
from app_vukwm_bag_delivery.osrm_tsp import sequence_routes


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
        .rename(columns={"Depot": "Site Name"})
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
        results = sequence_routes(
            df_routing,
            ports=st.secrets["osrm_ports"],
            route_column="Vehicle id",
        )
        # gb = GridOptionsBuilder.from_dataframe(results[0])
        # gb.configure_pagination(enabled=True)
        # gb.configure_side_bar()
        # gridOptions = gb.build()
        # AgGrid(
        #     results[0],
        #     gridOptions=gridOptions,
        #     fit_columns_on_grid_load=False,
        #     theme="streamlit",  # Add theme color to the table
        #     enable_enterprise_modules=True,
        #     height=500,
        #     width="100%",
        #     reload_data=True,
        #     allow_unsafe_jscode=True,
        # )
        return results[0]


def generate_van_routes(fleet, solver_max):
    if "remaining_jobs" in st.session_state:
        jobs = st.session_state.remaining_jobs
        fleet = fleet.loc[fleet["Type"] != "Bicycle"]
        assigned_jobs, unassigned_jobs = hygese_solver.generate_routes(
            jobs, fleet, time_limit=solver_max
        )
        # gb = GridOptionsBuilder.from_dataframe(assigned_jobs)
        # gb.configure_pagination(enabled=True)
        # gb.configure_side_bar()
        # gridOptions = gb.build()
        # AgGrid(
        #     assigned_jobs,
        #     gridOptions=gridOptions,
        #     fit_columns_on_grid_load=False,
        #     theme="streamlit",  # Add theme color to the table
        #     enable_enterprise_modules=True,
        #     height=500,
        #     width="100%",
        #     reload_data=True,
        #     allow_unsafe_jscode=True,
        # )
        return assigned_jobs


def generate_routes(fleet, delivery_jobs):
    allocate_jobs_per_type(fleet, delivery_jobs)


def start_routing():

    if "unassigned_stops_date" in st.session_state:
        delivery_jobs = st.session_state.unassigned_stops_date.copy()
    else:
        delivery_jobs = None

    if "fleet" in st.session_state:
        fleet = st.session_state.fleet.copy()
    else:
        fleet = None

    if fleet is not None and delivery_jobs is not None:
        generate_routes(fleet, delivery_jobs)
        st.subheader("Configure solver and generate routes")
        solver_max = st.slider("Maximum solver-time (seconds)", 1, 120, 5)
        if st.button("GENERATE ROUTES"):
            with st.spinner(f"Generating routes..."):
                bicycle_jobs = generate_bicycle_routes()
                van_routes = generate_van_routes(fleet, solver_max)
                routes = pd.concat([bicycle_jobs, van_routes]).reset_index(drop=True)
                st.session_state.assigned_jobs = routes.copy()
                st.write("Route generation completed.")
                routes.to_csv("data/test/route_test.csv", index=False)
                st.session_state.fleet.to_csv("data/test/fleet_test.csv", index=False)
                st.session_state.unassigned_stops_date.to_csv(
                    "data/test/unassigned_jobs.csv", index=False
                )
            with st.spinner(f"Generating route outputs..."):
                routes = return_routes.generate_route_data(
                    st.session_state.assigned_jobs,
                    st.session_state.fleet,
                    st.session_state.unassigned_stops_date,
                )
                route_maps = return_routes.return_map_html(routes)
                st.session_state.routes = routes.copy()
                st.session_state.route_maps = route_maps
                st.write("Route visualisations completed")
