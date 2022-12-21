import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components


def generate_timeline(df):
    assigned_stops_route_paths_plot = df.copy()
    assigned_stops_route_paths_plot = assigned_stops_route_paths_plot.rename(
        columns={
            "arrival_time": "Arrival time",
            "depart_time": "Depart time",
            "route_id": "Route ID",
            "vehicle_type": "Vehicle type",
            "route_sequence": "Route sequence",
        }
    )
    fig = px.timeline(
        assigned_stops_route_paths_plot,
        x_start="Arrival time",
        x_end="Depart time",
        y="Route ID",
        color="Vehicle type",
        text="Route sequence",
    )
    return fig


def summarise_route(assigned_stops_route_paths):

    route_sum = assigned_stops_route_paths.groupby(
        [
            "Vehicle id",
            "Type",
            "Capacity (#boxes)",
            "Cost (£) per km",
            "Cost (£) per hour",
        ]
    ).agg(
        n_stops=("route_sequence", "max"),
        n_boxes=("Total boxes", "sum"),
        route_start=("arrival_time", "min"),
        route_end=("depart_time", "max"),
        duration=("depart_stop_seconds", "max"),
        total_distance=("distance_km", "sum"),
    )
    route_sum = route_sum.assign(
        duration=(route_sum["duration"] / 3600).round(2),
        route_start=route_sum["route_start"].dt.strftime("%H:%M:%S"),
        route_end=route_sum["route_end"].dt.strftime("%H:%M:%S"),
        n_boxes=route_sum["n_boxes"].astype(int),
        total_distance=route_sum["total_distance"].round(0).astype(int),
    ).reset_index()
    route_sum["Route cost (£)"] = (
        route_sum["duration"] * route_sum["Cost (£) per hour"]
        + route_sum["total_distance"] * route_sum["Cost (£) per km"]
    )
    column_names = {
        "n_stops": "Number of stops",
        "n_boxes": "Number of boxes",
        "route_start": "Route start time",
        "route_end": "Route end time",
        "duration": "Route duration (h)",
        "total_distance": "Route distance (km)",
    }

    route_sum = route_sum.rename(columns=column_names)
    return route_sum


from app_vukwm_bag_delivery.return_session_staus import (
    return_side_bar,
    return_side_short,
)
from check_password import check_password

if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line

st.title("View routes")

st.sidebar.header("Session status")
status_text = st.sidebar.empty()
status_text.markdown(return_side_short())

with st.expander("Instructions"):
    st.markdown(
        """
    Perform the following steps to edit vehicle information and select the vehicles to be routed. If no vehicles are selected, it is assumed that the entire fleet is available for routing.

    * Step 1: Inspect the vehicle information in the table.
    * Step 2: Edit the vehicle informaiton where required.
    * Step 3: Select active vehicles by clicking on the boxes next to the vehicle ID.
    * Step 4: Click on "Update" to load the vehicles.
    """
    )


if "routes" not in st.session_state:
    st.warning(
        "Routes have not yet been generated. Please go to the 'Generate Routes' page."
    )
    st.stop()

routes = st.session_state.routes.copy()
route_maps = st.session_state.route_maps
components.html(route_maps, height=750)
route_sum = summarise_route(routes)
st.write("Route summary")
st.write(route_sum)
st.write("Route timeline")
st.plotly_chart(generate_timeline(routes), theme="streamlit", use_container_width=True)
