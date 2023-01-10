import streamlit as st

import app_vukwm_bag_delivery.models.vroom_wrappers.decode_vroom_solution as decode


def decode_soltuion():
    matrix_df = st.session_state.data_04_model_input["matrix_df"]
    route_df = st.session_state.data_03_primary["unassigned_routes"]
    stop_df = st.session_state.data_03_primary["unassigned_stops"]
    solution = st.session_state.data_06_model_output["vroom_solution"]
    matrix = st.session_state.data_04_model_input["matrix"]
    decoder = decode.DecodeVroomSolution(matrix_df, route_df, stop_df, solution, matrix)
    decoder.extract_unassigned()
    decoder.complete_route_df()
    decoder.extract_unused_routes()
    decoder.get_geo_info(st.secrets["osrm_port_mapping"])
    decoder.add_travel_leg()
    return decoder
