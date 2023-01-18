import numpy as np
import streamlit as st

from app_vukwm_bag_delivery.models.pipelines.summarise.sum_routes import route_summary

SUMMARY_VIEW_MAPPING = {
    "route_id": "Vehicle id",
    "vehicle_profile": "Vehicle type",
    "start_time": "Route start",
    "end_time": "Route end",
    "total_distance__meters": "Distance travelled (km)",
    "total_duration__seconds": "Duration (h)",
    "stops": "No. stops",
    "demand": "Products delivered",
    "early_stops": "No. early stop arrivals",
    "late_stops": "No. late stop arrivals",
    "waiting_duration__seconds": "Waiting time (minutes) for customers to open",
    "average_speed__kmh": "Average speed (km/h)",
}
VEHICLE_TYPE_MAPPING = {"auto": "Van", "bicycle": "Bicycle"}


def unit_conversions(assigned_stops):
    assigned_stops = assigned_stops.assign(
        vehicle_profile=assigned_stops["vehicle_profile"].replace(VEHICLE_TYPE_MAPPING),
        total_distance__meters=(assigned_stops["total_distance__meters"] / 1000)
        .round(0)
        .astype(int),
        total_duration__seconds=(
            assigned_stops["total_duration__seconds"] / 3600
        ).round(1),
        stops=assigned_stops["stops"].astype(int),
        average_speed__kmh=(assigned_stops["average_speed__kmh"]).round(1),
        demand=(assigned_stops["demand"]).astype(int),
        waiting_duration__seconds=(assigned_stops["waiting_duration__seconds"] / 60)
        .round(0)
        .astype(int),
        early_stops=assigned_stops["early_stops"].astype(int),
        late_stops=assigned_stops["late_stops"].astype(int),
    )
    return assigned_stops


def add_totals(route_sums):
    route_sums.loc["Total"] = route_sums.sum(numeric_only=True, axis=0)
    route_sums.loc["Total", "average_speed__kmh"] = np.nan
    return route_sums


def extract_high_level_summary():
    assigned_stops = st.session_state.data_07_reporting["assigned_stops"]

    route_sum = route_summary(assigned_stops)
    route_sum = add_totals(route_sum)
    route_sum = (
        unit_conversions(route_sum)
        .rename(columns=SUMMARY_VIEW_MAPPING)[SUMMARY_VIEW_MAPPING.values()]
        .fillna("")
    )

    return route_sum


def extract_unused_routes():
    unassigned_routes = st.session_state.data_02_intermediate["unassigned_routes"]
    unused_routes = st.session_state.data_07_reporting["unused_routes"]

    return unassigned_routes.loc[
        unassigned_routes["Vehicle id"].isin(unused_routes["route_id"])
    ]


def extract_unscheduled_stops():
    # TODO: make time windows persistent
    #  updated_time_windows = st.ses
    unassigned_stops_formatted = st.session_state.data_03_primary["unassigned_stops"]
    unassigned_jobs = st.session_state.data_02_intermediate["unassigned_jobs"]
    unassigned_jobs = unassigned_jobs.assign(
        **{"Site Bk": unassigned_jobs["Site Bk"].astype(str)}
    ).merge(
        unassigned_stops_formatted.assign(
            **{"Site Bk": unassigned_stops_formatted["stop_id"].astype(str)}
        )[["Site Bk", "time_window_start", "time_window_end"]].rename(
            columns={
                "time_window_start": "Time window start",
                "time_window_end": "Time window end",
            }
        ),
        how="left",
        left_on="Site Bk",
        right_on="Site Bk",
    )
    unscheduled_stops = st.session_state.data_07_reporting["unserviced_stops"]
    return unassigned_jobs.loc[
        unassigned_jobs["Site Bk"].astype(str).isin(unscheduled_stops["stop_id"].values)
    ].reset_index(drop=True)


def extract_unscheduled_route_stops():
    unassigned_stops_formatted = st.session_state.data_03_primary["unassigned_stops"]
    unassigned_jobs = st.session_state.data_02_intermediate["unassigned_jobs"]
    unassigned_jobs = unassigned_jobs.assign(
        **{"Site Bk": unassigned_jobs["Site Bk"].astype(str)}
    ).merge(
        unassigned_stops_formatted.assign(
            **{"Site Bk": unassigned_stops_formatted["stop_id"].astype(str)}
        )[["Site Bk", "time_window_start", "time_window_end"]].rename(
            columns={
                "time_window_start": "Time window start",
                "time_window_end": "Time window end",
            }
        ),
        how="left",
        left_on="Site Bk",
        right_on="Site Bk",
    )
    unscheduled_stops = st.session_state.data_07_reporting["unserviced_in_route_stops"]
    return unassigned_jobs.loc[
        unassigned_jobs["Site Bk"].astype(str).isin(unscheduled_stops["stop_id"].values)
    ].reset_index(drop=True)
