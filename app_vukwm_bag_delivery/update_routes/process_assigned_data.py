import numpy as np
import pandas as pd
import streamlit as st

from app_vukwm_bag_delivery.view_routes.generate_route_display import (
    gen_assigned_stops_display,
)


def return_stops_display():
    unserviced_stops = st.session_state.data_07_reporting["unserviced_stops"].copy()
    unserviced_stops["route_id"] = "Unassigned"
    unserviced_stops["service_issue"] = "UNSERVICED"
    assigned_stops = st.session_state.data_07_reporting["assigned_stops"].copy()
    unassigned_stops = st.session_state.data_02_intermediate["unassigned_stops"].copy()
    assigned_stops = pd.concat([assigned_stops, unserviced_stops]).reset_index(
        drop=True
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
                "ontime": (assigned_stops["Service issues"] == "ON-TIME") & deliver,
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
                "On-time": ("ontime", "sum"),
                "Early": ("early", "sum"),
                "Late": ("late", "sum"),
            }
        )
    )
    return route_kpis


def calc_difference(kpi, kpi_prev):
    delta = kpi.fillna(0) - kpi_prev.fillna(0)
    delta = delta.reset_index()
    delta = delta.assign(
        **{
            "sort_columns": delta["Vehicle Id"]
            + np.arange(0, delta.shape[0]).astype(str),
            "Vehicle Id": "changed by",
        }
    )
    route_kpis = kpi.reset_index()
    route_kpis = route_kpis.assign(sort_columns=route_kpis["Vehicle Id"])
    route_kpis = (
        pd.concat([route_kpis, delta])
        .sort_values(["sort_columns"])
        .drop(columns=["sort_columns"])
    )
    return route_kpis


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


def initiate_data():
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
        "assigned_stops_orig": kpis.copy(),
        "kpis": kpis.copy(),
        "kpis_orig": kpis.copy(),
        "kpi_difference": kpis,
    }


def return_filtered_route_id_data(route_id="Vehicle Id"):
    if st.session_state.route_filters:
        filtered = st.session_state.data.loc[
            st.session_state.data[route_id].isin(st.session_state.route_filters)
        ]
    else:
        filtered = st.session_state.data
    return filtered