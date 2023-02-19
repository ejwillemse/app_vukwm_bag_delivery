import streamlit as st

import app_vukwm_bag_delivery.models.vroom_wrappers.decode_vroom_solution as decode


def decode_solution():
    unassigned_routes = st.session_state.data_03_primary["unassigned_routes"]
    unassigned_stops = st.session_state.data_03_primary["unassigned_stops"]
    solution = st.session_state.data_06_model_output["vroom_solution"]
    st.write(solution.routes)
    matrix = st.session_state.data_04_model_input["matrix"]
    locations = st.session_state.data_03_primary["locations"]
    decoder = decode.DecodeVroomSolution(
        solution.routes,
        locations,
        unassigned_routes,
        unassigned_stops,
        matrix,
        st.secrets["osrm_port_mapping"],
    )
    assigned_stops = decoder.convert_solution()
    st.session_state.data_07_reporting = {
        "assigned_stops": assigned_stops,
        "unused_routes": decoder.unused_routes,
        "unserviced_stops": decoder.unserviced_stops,
    }
