import logging

import numpy as np
import pandas as pd
import streamlit as st

from app_vukwm_bag_delivery.models.pipelines.generate_solver_inputs import (
    get_osrm_tables,
)


def combine_route_stops(stops, routes):
    route_points = (
        routes.rename(columns={"route_id": "stop_id"})[
            ["stop_id", "longitude", "latitude"]
        ]
        .drop_duplicates()
        .copy()
    )
    route_points["matrix_index"] = np.arange(route_points.shape[0])
    route_points["stop_type"] = "route_depot"
    stop_points = stops[["stop_id", "longitude", "latitude"]].copy()
    stop_points["matrix_index"] = (
        np.arange(stop_points.shape[0]) + route_points.shape[0]
    )
    stop_points["stop_type"] = "stop"
    matrix_points = pd.concat([route_points, stop_points])
    return matrix_points


def extract_matrix(route_df, matrix_df):
    route_profile = route_df["profile"].unique()
    matrix = {}
    for profile in route_profile:
        logging.info(f"Generate {profile} matrix with {matrix_df.shape[0]} points")
        matrix["profile"] = get_osrm_tables.get_time_dist_matrix(
            matrix_df, st.secrets["osrm_port_mapping"][profile]
        )
    return matrix


def generate_matrix_inputs():
    stop_df = st.session_state.data_03_primary["unassigned_stops"]
    route_df = st.session_state.data_03_primary["unassigned_routes"]
    matrix_df = combine_route_stops(stop_df, route_df)
    matrix = extract_matrix(route_df, matrix_df)
    st.session_state.data_04_model_input = {"matrix_df": matrix_df, "matrix": matrix}
