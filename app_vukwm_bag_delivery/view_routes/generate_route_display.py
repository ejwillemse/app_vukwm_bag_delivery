import numpy as np
import pandas as pd
import streamlit as st

MAPPING = {
    "route_id": "Vehicle Id",
    "trip_id": "Trip Id",
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
    unassigned_stops[["Site Bk", "Customer Bk"]] = unassigned_stops[
        ["Site Bk", "Customer Bk"]
    ].astype(str)
    return unassigned_stops


def unit_conversions(assigned_stops):
    assigned_stops = assigned_stops.assign(
        vehicle_profile=assigned_stops["vehicle_profile"].replace(VEHICLE_TYPE_MAPPING),
        waiting_duration__seconds=(
            assigned_stops["waiting_duration__seconds"].fillna(0) / 60
        )  # to minutes
        .round(0)
        .astype(int),
        travel_distance_to_stop__meters=(
            assigned_stops["travel_distance_to_stop__meters"] / 1000
        ).round(2),
        travel_duration_to_stop__seconds=(
            assigned_stops["travel_duration_to_stop__seconds"].fillna(0) / 60
        )  # to minutes
        .round(0)
        .astype(int),
        service_duration__seconds=(
            assigned_stops["service_duration__seconds"].fillna(0) / 60
        )  # to minutes
        .round(0)
        .astype(int),
        travel_speed__kmh=(assigned_stops["travel_speed__kmh"]).round(1),
        trip_id=assigned_stops["trip_id"].fillna(1).astype(int),
    )
    return assigned_stops


def gen_assigned_stops_display(assigned_stops, unassigned_stops, fillna=True):
    assigned_stops_display = unit_conversions(assigned_stops)
    assigned_stops_display = assigned_stops_display.rename(columns=MAPPING)[
        MAPPING.values()
    ]
    unassigned_stops_display = display_format(unassigned_stops)
    assigned_stops_display = (
        assigned_stops_display.merge(
            unassigned_stops_display, left_on="Site Bk", right_on="Site Bk", how="left"
        )
        .sort_values(["Vehicle Id", "Stop sequence", "Site Name"])
        .reset_index(drop=True)
    )
    if fillna:
        assigned_stops_display = assigned_stops_display.fillna(" ")
    return assigned_stops_display


def return_assigned_stops_display():
    assigned_stops = st.session_state.data_07_reporting["assigned_stops"].copy()
    unassigned_stops = st.session_state.data_02_intermediate["unassigned_stops"].copy()
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
    assigned_stops = gen_assigned_stops_display(assigned_stops, unassigned_stops)
    return assigned_stops


def return_all_stops_display():
    unserviced_stops = st.session_state.data_07_reporting["unserviced_stops"].copy()
    unserviced_stops["route_id"] = "Unassigned"
    unserviced_stops["service_issue"] = "UNSERVICED"
    assigned_stops = st.session_state.data_07_reporting["assigned_stops"].copy()
    unassigned_stops = st.session_state.data_02_intermediate["unassigned_stops"].copy()
    unassigned_stops = st.session_state.data_02_intermediate["unassigned_stops"].copy()
    assigned_stops = pd.concat([assigned_stops, unserviced_stops]).reset_index(
        drop=True
    )
    assigned_stops = gen_assigned_stops_display(
        assigned_stops, unassigned_stops, fillna=False
    )
    return assigned_stops
