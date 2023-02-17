import datetime

import plotly.express as px
import streamlit as st

COLOR_SEQUENCE = [
    "#12939A",
    "#DDB27C",
    "#88572C",
    "#FF991F",
    "#F15C17",
    "#223F9A",
    "#DA70BF",
    "#125C77",
    "#4DC19C",
    "#776E57",
    "#17B8BE",
    "#F6D18A",
    "#B7885E",
    "#FFCB99",
    "#F89570",
    "#829AE3",
    "#E79FD5",
    "#1E96BE",
    "#89DAC1",
    "#B3AD9E",
]

MAPPING = {
    "route_id": "Vehicle Id",
    "vehicle_profile": "Vehicle profile",
    "stop_id": "Site Bk",
    "stop_sequence": "Stop sequence",
    "job_sequence": "Job sequence",
    "arrival_time": "Arrival time",
    "service_start_time": "Service start time",
    "departure_time": "Departure time",
    "waiting_duration__seconds": "Waiting time (minutes)",
    "travel_duration_to_stop__seconds": "Travel duration to stop (minutes)",
    "travel_distance_to_stop__meters": "Travel distance to stops (km)",
    "travel_speed__kmh": "Travel speed (km/h)",
    "service_duration__seconds": "Service duration (minutes)",
    "activity_type": "Activity type",
    "skills": "Skills",
    "latitude": "latitude",
    "longitude": "longitude",
    "travel_path_to_stop": "travel_path_to_stop",
    "road_snap_longitude": "road_longitude",
    "road_snap_latitude": "road_latitude",
    "time_window_start": "Time window start",
    "time_window_end": "Time window end",
    "service_issue": "Service issues",
}
VEHICLE_TYPE_MAPPING = {"auto": "Van", "bicycle": "Bicycle"}


def display_format(unassigned_stops):
    unassigned_stops = unassigned_stops[
        [
            "Customer Bk",
            "Site Bk",
            "Site Name",
            "Transport Area Code",
            "Product description",
            "Site Address",
            "Ticket No",
        ]
    ].copy()
    unassigned_stops["Product description"] = unassigned_stops[
        "Product description"
    ].str.replace("\n", "; ")
    unassigned_stops["Site Bk"] = unassigned_stops["Site Bk"].astype(str)
    return unassigned_stops


def unit_conversions(assigned_stops):
    assigned_stops = assigned_stops.assign(
        vehicle_profile=assigned_stops["vehicle_profile"].replace(VEHICLE_TYPE_MAPPING),
        waiting_duration__seconds=(
            assigned_stops["waiting_duration__seconds"] / 60
        )  # to minutes
        .round(0)
        .astype(int),
        travel_distance_to_stop__meters=(
            assigned_stops["travel_distance_to_stop__meters"] / 1000
        ).round(2),
        travel_duration_to_stop__seconds=(
            assigned_stops["travel_duration_to_stop__seconds"] / 60
        )  # to minutes
        .round(0)
        .astype(int),
        service_duration__seconds=(
            assigned_stops["service_duration__seconds"] / 60
        )  # to minutes
        .round(0)
        .astype(int),
        travel_speed__kmh=(assigned_stops["travel_speed__kmh"]).round(1),
    )
    return assigned_stops


def return_assigned_stops_display(assigned_stops, unassigned_stops):
    assigned_stops_display = unit_conversions(assigned_stops)
    assigned_stops_display = assigned_stops_display.rename(columns=MAPPING)[
        MAPPING.values()
    ]
    unassigned_stops_display = display_format(unassigned_stops)
    assigned_stops_display = assigned_stops_display.merge(
        unassigned_stops_display, left_on="Site Bk", right_on="Site Bk", how="left"
    ).fillna(" ")
    return assigned_stops_display


def generate_timeline(df, detailed):
    hovertemplate1 = (
        "<b>Stop no.: %{customdata[0]}</b><br>"
        + "Site: %{customdata[1]}</b><br>"
        + "Site Bk: %{customdata[2]}<br>"
        + "Address: %{customdata[3]}<br>"
        + "Delivery products: %{customdata[4]}<br>"
        + "Arrival time: %{customdata[5]}<br>"
    )

    custom_data = [
        "Stop sequence",
        "Site Name",
        "Site Bk",
        "Site Address",
        "Product description",
        "Arrival time",
    ]

    assigned_stops_route_paths_plot = df.copy()

    if detailed:
        label = (
            +assigned_stops_route_paths_plot["Stop sequence"].astype(str)
            + "<br>"
            + assigned_stops_route_paths_plot["Site Name"]
        )
    else:
        label = assigned_stops_route_paths_plot["Stop sequence"]
    assigned_stops_route_paths_plot = assigned_stops_route_paths_plot.assign(
        label=label
    )

    assigned_stops_route_paths_plot["Arrival time"] = (
        datetime.datetime.now().strftime("%Y-%m-%d")
        + " "
        + assigned_stops_route_paths_plot["Arrival time"]
    )
    assigned_stops_route_paths_plot["Departure time"] = (
        datetime.datetime.now().strftime("%Y-%m-%d")
        + " "
        + assigned_stops_route_paths_plot["Departure time"]
    )
    fig = px.timeline(
        assigned_stops_route_paths_plot,
        x_start="Arrival time",
        x_end="Departure time",
        y="Vehicle Id",
        color="Vehicle Id",
        color_discrete_sequence=COLOR_SEQUENCE,
        text="label",
        custom_data=custom_data,
    )
    _ = fig.update_traces(hovertemplate=hovertemplate1)
    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list(
                    [
                        dict(
                            count=15, label="15min", step="minute", stepmode="backward"
                        ),
                        dict(
                            count=30, label="30min", step="minute", stepmode="backward"
                        ),
                        dict(count=1, label="1h", step="hour", stepmode="backward"),
                        dict(count=3, label="3h", step="hour", stepmode="backward"),
                        dict(count=6, label="6h", step="hour", stepmode="backward"),
                        dict(step="all"),
                    ]
                ),
                font=dict(color="black"),
            ),
            rangeslider=dict(visible=True),
            type="date",
        )
    )
    fig.update_xaxes(tickformat="%H:%M")
    return fig


def return_gant(detailed=False):
    assigned_stops = st.session_state.data_07_reporting["assigned_stops"].copy()
    unassigned_stops = st.session_state.data_02_intermediate["unassigned_stops"].copy()
    if (
        "view_routes" in st.session_state
        and "filter_vehicles" in st.session_state.view_routes
    ):
        filter_routes = st.session_state.view_routes["filter_vehicles"]
        if filter_routes:
            assigned_stops = assigned_stops.loc[
                assigned_stops["route_id"].isin(filter_routes)
            ]
    assigned_stops = return_assigned_stops_display(assigned_stops, unassigned_stops)
    return generate_timeline(assigned_stops, detailed)
