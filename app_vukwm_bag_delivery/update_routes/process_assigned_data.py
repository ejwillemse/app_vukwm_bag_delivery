import numpy as np
import pandas as pd
import streamlit as st

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
        unused_routes = st.session_state.data_07_reporting["unused_routes"][
            ["route_id", "profile"]
        ]
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
