import streamlit as st
from vroom.input import input

import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
from app_vukwm_bag_delivery.models.vroom_wrappers import generate_vroom_object


def generate_vroom_input():
    problem_instance = input.Input()
    matrix = st.session_state.data_04_model_input["matrix"]
    unassigned_routes = st.session_state.data_03_primary["unassigned_routes"]
    unassigned_stops = st.session_state.data_03_primary["unassigned_stops"]

    problem_instance = generate_vroom_object.add_matrix_profiles(
        problem_instance,
        matrix,
    )

    problem_instance = generate_vroom_object.add_vehicles(
        problem_instance, unassigned_routes
    )

    problem_instance = generate_vroom_object.add_stops(
        problem_instance, unassigned_stops, unassigned_routes
    )
    st.session_state.data_04_model_input["vroom_input"] = problem_instance
