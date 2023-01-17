import numpy as np
import pandas as pd
import streamlit as st

from app_vukwm_bag_delivery.view_routes.generate_route_display import (
    return_all_stops_display,
    return_assigned_stops_display,
)


def process_assigned_stops():
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
    assigned_stops = return_all_stops_display()
    assigned_stops = pd.concat([assigned_stops, unused_routes])
    kpis = gen_kpis(assigned_stops)
    st.session_state.edit_routes = {
        "assigned_stops": assigned_stops.copy(),
        "assigned_stops_orig": kpis.copy(),
        "kpis": kpis.copy(),
        "kpis_orig": kpis.copy(),
    }
    st.write(kpis)


def update_kpis():
    assigned_stops = st.session_state.edit_routes["assigned_stops"]
    st.session_state.edit_routes = {
        "assigned_stops": assigned_stops.copy(),
        "kpis": gen_kpis(assigned_stops),
    }


def update_assigned_stop():
    assigned_stops = st.session_state.edit_routes["assigned_stops"]
    st.session_state.edit_routes = {
        "assigned_stops": assigned_stops.copy(),
        "kpis": gen_kpis(assigned_stops),
    }


def gen_kpis(assigned_stops):
    route_kpis = (
        assigned_stops.assign(
            **{
                "Duration (h)": assigned_stops["Travel duration to stop (minutes)"] / 60
                + assigned_stops["Service duration (minutes)"] / 60
                + assigned_stops["Waiting time (minutes)"] / 60,
                "ontime": assigned_stops["Service issues"] == "ON-TIME",
                "early": assigned_stops["Service issues"] == "EARLY",
                "late": assigned_stops["Service issues"] == "LATE",
                "UNSERVICED": assigned_stops["Service issues"] == "UNSERVICED",
            }
        )
        .groupby(["Vehicle Id"])
        .agg(
            **{
                "Duration (h)": ("Duration (h)", "sum"),
                "Distance (km)": ("Travel distance to stops (km)", "sum"),
                "Stops": ("Job sequence", "max"),
                "Unserviced": ("UNSERVICED", "sum"),
                "On-time": ("ontime", "sum"),
                "Early": ("early", "sum"),
                "Late": ("late", "sum"),
            }
        )
    )
    return route_kpis


# def get_kpi_difference():
#     st.session_state["kpis"] =

#         "assigned_stops": assigned_stops.copy(),
#         "assigned_stops_orig": kpis.copy(),
#         "kpis": kpis.copy(),
#         "kpis_orig": kpis.copy(),
#     }


def add_difference(kpi, kpi_prev):
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
