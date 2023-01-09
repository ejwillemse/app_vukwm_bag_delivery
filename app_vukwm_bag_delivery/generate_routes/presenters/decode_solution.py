import streamlit as st

import app_vukwm_bag_delivery.models.routing_engine.decode_vroom_solution as decode


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
    st.write(decoder.get_route_kpis())
    st.write("Stops that cannot be completed:")
    st.write(decoder.stops_unassigned_df)
    st.write("Unused vehicles:")
    st.write(decoder.routes_unused_df)
