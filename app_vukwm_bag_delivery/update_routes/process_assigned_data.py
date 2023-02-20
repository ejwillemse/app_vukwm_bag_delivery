import numpy as np
import pandas as pd
import streamlit as st

import app_vukwm_bag_delivery.models.vroom_wrappers.decode_vroom_solution as decode
from app_vukwm_bag_delivery.view_routes.generate_route_display import (
    gen_assigned_stops_display,
)


def add_empty_routes(assigned_stops, add_unassigned_route=True):
    """Empty routes are added to the stop objects (maybe this should be the default?)"""
    all_routes = st.session_state.data_02_intermediate["unassigned_routes"]
    unused_routes = all_routes.loc[
        ~all_routes["Vehicle id"].isin(assigned_stops["Vehicle Id"])
    ][["Vehicle id"]].rename(columns={"Vehicle id": "Vehicle Id"})
    if (
        add_unassigned_route is True
        and (assigned_stops["Vehicle Id"] != "Unassigned").all() == True
    ):
        unassigned = pd.DataFrame([{"Vehicle Id": "Unassigned"}])
        unused_routes = pd.concat([unused_routes, unassigned])
    assigned_stops = (
        pd.concat([assigned_stops, unused_routes])
        .reset_index(drop=True)
        .sort_values(["Vehicle Id", "Stop sequence", "Site Name"])
    )
    return assigned_stops


def return_stops_display():
    unserviced_stops = st.session_state.data_07_reporting["unserviced_stops"].copy()
    if st.session_state.data_07_reporting["unserviced_stops"].shape[0] == 0:
        unserviced_stops = pd.DataFrame(
            [{"route_id": "Unassigned", "service_issue": "UNSERVICED"}]
        )
    unserviced_stops["route_id"] = "Unassigned"
    unserviced_stops["service_issue"] = "UNSERVICED"
    assigned_stops = st.session_state.data_07_reporting["assigned_stops"].copy()
    unassigned_stops = st.session_state.data_02_intermediate["unassigned_stops"].copy()
    assigned_stops = (
        pd.concat([assigned_stops, unserviced_stops])
        .sort_values(["route_id"])
        .reset_index(drop=True)
    )
    assigned_stops = gen_assigned_stops_display(
        assigned_stops, unassigned_stops, fillna=False
    )
    return assigned_stops


def update_stops_display(assigned_stops, unserviced_stops):
    unassigned_stops = st.session_state.data_02_intermediate["unassigned_stops"].copy()
    assigned_stops = pd.concat([assigned_stops, unserviced_stops]).reset_index(
        drop=True
    )
    assigned_stops = gen_assigned_stops_display(
        assigned_stops, unassigned_stops, fillna=False
    )
    return assigned_stops


def gen_kpis(assigned_stops):
    deliver = assigned_stops["Activity type"] == "DELIVERY"
    route_kpis = (
        assigned_stops.assign(
            **{
                "Duration (h)": assigned_stops["Travel duration to stop (minutes)"] / 60
                + assigned_stops["Service duration (minutes)"] / 60
                + assigned_stops["Waiting time (minutes)"] / 60,
                "deliver": deliver,
                # "ontime": (assigned_stops["Service issues"] == "ON-TIME") & deliver,
                "early": (assigned_stops["Service issues"] == "EARLY") & deliver,
                "late": (assigned_stops["Service issues"] == "LATE") & deliver,
                "UNSERVICED": (assigned_stops["Service issues"] == "UNSERVICED")
                & deliver,
            }
        )
        .groupby(["Vehicle Id"])
        .agg(
            **{
                "Duration (h)": ("Duration (h)", "sum"),
                "Distance (km)": ("Travel distance to stops (km)", "sum"),
                "Stops": ("deliver", "sum"),
                "Unserviced": ("UNSERVICED", "sum"),
                # "On-time": ("ontime", "sum"),
                "Early": ("early", "sum"),
                "Late": ("late", "sum"),
            }
        )
    )
    route_kpis.loc["Total"] = route_kpis.sum()
    route_kpis[["Distance (km)", "Stops", "Unserviced", "Early", "Late"]] = route_kpis[
        ["Distance (km)", "Stops", "Unserviced", "Early", "Late"]
    ].astype(int)
    return route_kpis


def calc_difference(kpi, kpi_prev):
    delta = kpi.fillna(0) - kpi_prev.fillna(0)
    # delta = delta.reset_index()
    # delta = delta.assign(
    #     **{
    #         "sort_columns": delta["Vehicle Id"]
    #         + np.arange(0, delta.shape[0]).astype(str),
    #         "Vehicle Id": "changed by",
    #     }
    # )
    # route_kpis = kpi.reset_index()
    # route_kpis = route_kpis.assign(sort_columns=route_kpis["Vehicle Id"])
    # route_kpis = (
    #     pd.concat([route_kpis, delta])
    #     .sort_values(["sort_columns"])
    #     .drop(columns=["sort_columns"])
    # )
    return delta


def calc_kpi_difference():
    return calc_difference(
        st.session_state.edit_routes["kpis"], st.session_state.edit_routes["kpis_orig"]
    )


def update_assigned_stop(assigned_stops):
    st.session_state.edit_routes["assigned_stops"] = assigned_stops
    st.session_state.edit_routes["kpis"] = gen_kpis(assigned_stops)
    st.session_state.edit_routes["kpi_difference"] = calc_kpi_difference()


def store_new_assigned_stops(assigned_stops, unserviced_stops):
    assigned_stops = update_stops_display(assigned_stops, unserviced_stops)
    update_assigned_stop(store_new_assigned_stops)


def clear_route_edit_data():
    st.session_state.edit_routes = {}


def initiate_data():
    if "edit_routes" not in st.session_state or not st.session_state.edit_routes:
        unassigned_routes = st.session_state.data_03_primary["unassigned_routes"]
        unused_routes = unassigned_routes.loc[
            ~unassigned_routes["route_id"].isin(
                st.session_state.data_07_reporting["assigned_stops"]["route_id"]
            )
        ][["route_id", "profile"]]
        # unused_routes = st.session_state.data_07_reporting["unused_routes"][
        #     ["route_id", "profile"]
        # ]
        unused_routes = unused_routes.rename(
            columns={"route_id": "Vehicle Id", "profile": "Vehicle profile"}
        )
        unused_routes = unused_routes.assign(
            **{
                "Vehicle profile": unused_routes["Vehicle profile"].replace(
                    {"auto": "Van", "bicycle": "Bicycle"}
                )
            }
        )
        assigned_stops = return_stops_display()
        assigned_stops = pd.concat([assigned_stops, unused_routes])
        kpis = gen_kpis(assigned_stops)
        st.session_state.edit_routes = {
            "assigned_stops": assigned_stops.copy(),
            "assigned_stops_orig": assigned_stops.copy(),
            "kpis": kpis.copy(),
            "kpis_orig": kpis.copy(),
            "previous_assigned": assigned_stops.copy(),
        }
        st.session_state.edit_routes["kpi_difference"] = calc_kpi_difference()


def return_filtered_route_id_data(route_id="Vehicle Id"):
    if st.session_state.route_filters:
        filtered = st.session_state.data.loc[
            st.session_state.data[route_id].isin(st.session_state.route_filters)
        ]
    else:
        filtered = st.session_state.data
    return filtered


def update_unsused_routes():
    stops = st.session_state.edit_routes["assigned_stops"]
    empty_routes = stops.loc[stops["Site Bk"].isna()]["Vehicle Id"]
    unassigned_routes = st.session_state.data_03_primary["unassigned_routes"]
    empty_routes = unassigned_routes.loc[
        unassigned_routes["route_id"].isin(empty_routes.values)
    ]
    st.session_state.data_07_reporting["unused_routes"] = empty_routes.copy()


def update_unserviced_stops():
    location = st.session_state.data_03_primary["locations"]
    stops = st.session_state.edit_routes["assigned_stops"]
    stops_unserviced = stops.loc[stops["Vehicle Id"] == "Unassigned"]
    stops_unserviced = location.loc[
        location["stop_id"].isin(stops_unserviced["Site Bk"].values)
    ]
    st.session_state.data_07_reporting["unserviced_stops"] = stops_unserviced.copy()


def update_assigned_stops():
    stops = st.session_state.edit_routes["assigned_stops"]
    unassigned_routes = st.session_state.data_03_primary["unassigned_routes"]
    unassigned_stops = st.session_state.data_03_primary["unassigned_stops"]
    matrix = st.session_state.data_04_model_input["matrix"]
    locations = st.session_state.data_03_primary["locations"]

    solution = stops  # .loc[stops["Service issues"] != "UNSERVICED"]
    solution = (
        solution.merge(
            unassigned_routes[["route_id", "route_index", "profile"]],
            how="left",
            left_on="Vehicle Id",
            right_on="route_id",
        )
        .merge(
            locations[["stop_id", "location_index"]],
            left_on="Site Bk",
            right_on="stop_id",
        )
        .sort_values(["Vehicle Id", "Stop sequence"])
    )
    time_start = pd.to_datetime(solution["Arrival time"])
    solution = solution.assign(
        **{
            "arrival_time__seconds": (
                (time_start - time_start.dt.normalize()) / pd.Timedelta("1 second")
            ),
            "service_duration__seconds": solution["Service duration (minutes)"] * 60,
            "waiting_duration__seconds": solution["Waiting time (minutes)"] * 60,
        }
    ).rename(
        columns={
            "Service issues": "service_issue",
            "Activity type": "activity_type",
            "profile": "vehicle_profile",
            "stop_id": "stop_id",
        }
    )[
        [
            "route_id",
            "route_index",
            "activity_type",
            "location_index",
            "arrival_time__seconds",
            "service_duration__seconds",
            "waiting_duration__seconds",
            "service_issue",
            "vehicle_profile",
            "stop_id",
        ]
    ]
    solution = solution.dropna(subset=["route_id"])
    route_unassigned = (
        solution.loc[
            (solution["route_id"] != "Unassigned")
            & (solution["service_issue"] == "UNSERVICED")
        ][["route_id", "service_issue", "vehicle_profile", "stop_id"]]
        .merge(locations)
        .drop(columns=["location_index"])
    )
    solution = (
        solution.loc[solution["service_issue"] != "UNSERVICED"]
        .drop(columns=["route_id", "service_issue", "stop_id"])
        .reset_index(drop=True)
    )
    decoder = decode.DecodeVroomSolution(
        solution,
        locations,
        unassigned_routes,
        unassigned_stops,
        matrix,
        st.secrets["osrm_port_mapping"],
    )

    assigned_stops = decoder.extend_solution()
    assigned_stops = (
        pd.concat([assigned_stops, route_unassigned])
        .sort_values(["route_id", "stop_sequence"])
        .reset_index(drop=True)
    )
    assigned_stops = assigned_stops.assign(
        arrival_time=assigned_stops["arrival_time"].fillna(method="ffill"),
        service_start_time=assigned_stops["service_start_time"].fillna(method="ffill"),
        departure_time=assigned_stops["departure_time"].fillna(method="ffill"),
        waiting_duration__seconds=assigned_stops["waiting_duration__seconds"].fillna(0),
        travel_duration_to_stop__seconds=assigned_stops[
            "travel_duration_to_stop__seconds"
        ].fillna(0),
        travel_distance_to_stop__meters=assigned_stops[
            "travel_distance_to_stop__meters"
        ].fillna(0),
    )
    assigned_stops = add_sequences(assigned_stops)
    st.session_state.data_07_reporting["assigned_stops"] = assigned_stops.copy()
    st.session_state.data_07_reporting[
        "unserviced_in_route_stops"
    ] = assigned_stops.loc[
        (assigned_stops["route_id"] != "Unassigned")
        & (assigned_stops["service_issue"] == "UNSERVICED")
    ]


def add_sequences(assigned_stops: pd.DataFrame, job_activities=None) -> pd.DataFrame:
    """Add stop and job only visit sequences"""

    def cal_route_sequences(df):
        return df.groupby(["route_id"]).cumcount()

    if job_activities is None:
        job_activities = ["JOB"]

    assigned_stops = assigned_stops.assign(
        stop_sequence=cal_route_sequences(assigned_stops)
    )
    job_stops = assigned_stops.loc[
        assigned_stops["location_type"].isin(job_activities)
    ].copy()
    job_stops = job_stops.assign(job_sequence=cal_route_sequences(job_stops))
    assigned_stops = assigned_stops.drop(columns=["job_sequence"]).merge(
        job_stops[["route_id", "stop_sequence", "job_sequence"]], how="left"
    )
    return assigned_stops
