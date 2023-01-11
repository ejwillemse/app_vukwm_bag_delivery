import pickle

import streamlit as st

import app_vukwm_bag_delivery.models.vroom_wrappers.decode_vroom_solution as decode


def decode_soltuion():
    unassigned_routes = st.session_state.data_03_primary["unassigned_routes"]
    unassigned_stops = st.session_state.data_03_primary["unassigned_stops"]
    solution = st.session_state.data_06_model_output["vroom_solution"]
    matrix = st.session_state.data_04_model_input["matrix"]
    locations = st.session_state.data_03_primary["locations"]
    unassigned_stops.to_csv(
        "data/local_test/03_Generate_Routes/unassigned_stops.csv", index=False
    )
    unassigned_routes.to_csv(
        "data/local_test/03_Generate_Routes/unassigned_routes.csv", index=False
    )
    locations.to_csv("data/local_test/03_Generate_Routes/locations.csv", index=False)
    solution.routes.to_csv(
        "data/local_test/03_Generate_Routes/vroom_routes.csv", index=False
    )

    with open("data/local_test/03_Generate_Routes/matrix.pickle", "bw") as f:
        pickle.dump(matrix, f)
    # decoder = decode.DecodeVroomSolution(
    #     unassigned_routes, unassigned_stops, solution, matrix, locations
    # )
    # decoder.extract_unassigned()
    # decoder.complete_route_df()
    # decoder.extract_unused_routes()
    # decoder.get_geo_info(st.secrets["osrm_port_mapping"])
    # decoder.add_travel_leg()
    # return decoder
    return None
