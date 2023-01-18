import datetime
import logging

import pandas as pd
import streamlit as st
from vroom.input import input

import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
from app_vukwm_bag_delivery.models.vroom_wrappers import (
    decode_vroom_solution,
    generate_vroom_object,
)
from app_vukwm_bag_delivery.view_routes.generate_route_display import (
    gen_assigned_stops_display,
)


def generate_vroom_input(unassigned_routes, unassigned_stops):
    problem_instance = input.Input()
    matrix = st.session_state.data_04_model_input["matrix"]
    problem_instance = generate_vroom_object.add_matrix_profiles(
        problem_instance,
        matrix,
    )

    problem_instance = generate_vroom_object.add_vehicles(
        problem_instance, unassigned_routes
    )

    problem_instance = generate_vroom_object.add_stops(
        problem_instance, unassigned_stops
    )

    return problem_instance


def drop_deliveries(df):
    return df.loc[df["Activity type"] == "DELIVERY"]


def stop_assignment_id(df):
    return df.assign(assignmnet_id=df["Vehicle Id"] + "__" + df["Site Bk"].fillna(""))


def route_changed_flag(df_new, df_orign):
    lost_ids = ~df_orign["assignmnet_id"].isin(df_new["assignmnet_id"])
    new_ids = ~df_new["assignmnet_id"].isin(df_orign["assignmnet_id"])
    st.write(df_orign.loc[lost_ids])
    st.write(df_new.loc[new_ids])
    vehicle_updates = set(
        list(df_orign.loc[lost_ids]["Vehicle Id"].unique())
        + list(df_new.loc[new_ids]["Vehicle Id"].unique())
    )
    return list(vehicle_updates)


def filter_stop_info(route_id):
    unassigned_routes = st.session_state.data_03_primary["unassigned_routes"]
    unassigned_stops = st.session_state.data_03_primary["unassigned_stops"]
    unassigned_routes = unassigned_routes.loc[unassigned_routes["route_id"] == route_id]
    stops = st.session_state.data
    stops = stops.loc[stops["Vehicle Id"] == route_id]
    unassigned_stops = unassigned_stops.loc[
        unassigned_stops["stop_id"]
        .astype(str)
        .isin(stops["Site Bk"].astype(str).values)
    ]
    return unassigned_routes, unassigned_stops


def decode_solution(unassigned_routes, unassigned_stops, solution):
    matrix = st.session_state.data_04_model_input["matrix"]
    locations = st.session_state.data_03_primary["locations"]
    decoder = decode_vroom_solution.DecodeVroomSolution(
        solution.routes,
        locations,
        unassigned_routes,
        unassigned_stops,
        matrix,
        st.secrets["osrm_port_mapping"],
    )
    assigned_stops = decoder.speed_convert_solution()
    return (assigned_stops, decoder.unserviced_stops)


def return_stops_display(assigned_stops, unserviced_stops, route_info):
    if unserviced_stops.shape[0] > 0:
        unserviced_stops["route_id"] = route_info.iloc[0]["route_id"]
        unserviced_stops["vehicle_profile"] = route_info.iloc[0]["profile"]
        unserviced_stops["service_issue"] = "UNSERVICED"
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


def find_changed_routes():
    current_assignment = drop_deliveries(st.session_state.data)
    previous_assignment = drop_deliveries(
        st.session_state.edit_routes["previous_assigned"]
    )

    previous_assignment = stop_assignment_id(previous_assignment)
    current_assignment = stop_assignment_id(current_assignment)
    vehicle_updates = route_changed_flag(previous_assignment, current_assignment)
    return vehicle_updates


def generate_new_routes(vehicle_updates):
    new_assigned_stops = []
    if vehicle_updates:
        for vehicle_id in vehicle_updates:
            route_info, stop_info = filter_stop_info(vehicle_id)
            if stop_info.shape[0] > 0:
                problem_instance = generate_vroom_input(route_info, stop_info)
                with st.spinner("Solving"):
                    solution = problem_instance.solve(exploration_level=5, nb_threads=4)
                (assigned_stops, unserviced_stops) = decode_solution(
                    route_info, stop_info, solution
                )
                assigned_stops = return_stops_display(
                    assigned_stops, unserviced_stops, route_info
                )
                new_assigned_stops.append(assigned_stops)
        new_assigned_stops = pd.concat(new_assigned_stops)
        return new_assigned_stops


def reroute():
    vehicle_updates = find_changed_routes()
    new_routes = generate_new_routes(vehicle_updates)
