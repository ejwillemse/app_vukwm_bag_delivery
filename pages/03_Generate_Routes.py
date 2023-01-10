import streamlit as st

import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.generate_routes.presenters.decode_solution import (
    decode_soltuion,
)
from app_vukwm_bag_delivery.generate_routes.presenters.generate_matrix import (
    generate_matrix_inputs,
)
from app_vukwm_bag_delivery.generate_routes.presenters.generate_route_objects import (
    generate_vroom_input,
)
from app_vukwm_bag_delivery.generate_routes.presenters.process_input_data import (
    process_input_data,
)
from app_vukwm_bag_delivery.generate_routes.presenters.solve_vroom_instace import solve
from app_vukwm_bag_delivery.util_presenters.check_password import check_password


def set_page_config():
    st.set_page_config(
        layout="wide",
        page_title="Generate routes",
        initial_sidebar_state="expanded",
    )
    st.title("Generate routes")


if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line


def view_instructions():
    with st.expander("Instructions"):
        st.markdown(
            """
        Perform the following steps to edit vehicle information and select the vehicles to be routed. If no vehicles are selected, it is assumed that the entire fleet is available for routing.

        * Step 1: Inspect the vehicle information in the table.
        * Step 2: Edit the vehicle informaiton where required.
        * Step 3: Select active vehicles by clicking on the boxes next to the vehicle ID.
        * Step 4: Click on "Update" to load the vehicles.
        """
        )


def check_previous_steps_completed():
    stop = False
    if not return_session_status.check_intermediate_unassigned_jobs_loaded():
        st.warning("Job data not loaded during session. Please go back to `Home` page")
        stop = True  # App won't run anything after this line
    if not return_session_status.check_intermediate_unassigned_fleet_loaded():
        st.warning(
            "Vehicles have not yet been configured and selected. Please go to the 'Select Vehicles' page."
        )
        stop = True
    if stop:
        st.stop()


def display_routes():
    st.write("Routes will be generated for the following vehicles:")
    st.write(st.session_state.data_02_intermediate["unassigned_routes"])


def display_excluded_stops():
    if return_session_status.check_jobs_excluded_from_route():
        st.write("The following stops will be EXCLUDED from routing:")
        st.write(
            st.session_state.data_02_intermediate[
                "user_confirmed_removed_unassigned_stops"
            ]
        )


def start_routing():
    start = st.button("Generate routes")
    if start:
        with st.spinner("Peperating fleet and stop data..."):
            process_input_data()
            st.markdown(":white_check_mark: Fleet and stop data prepared")
        with st.spinner("Generating map data..."):
            generate_matrix_inputs()
            st.markdown(":white_check_mark: Map data loaded")
        with st.spinner("Seting up route engine..."):
            generate_vroom_input()
            st.markdown(":white_check_mark: Routing engine setup completed")
        with st.spinner("Generating routes..."):
            solve()
            st.markdown(":white_check_mark: Routes generated")
        with st.spinner("Completing route analysis..."):
            decoder = decode_soltuion()
            st.markdown(":white_check_mark: Analyses completed")
            st.session_state.decoder = decoder
            st.markdown("Routes can be viewed in `View Routes` page")
    if "decoder" in st.session_state:
        st.write(st.session_state.decoder.solution.routes)
        st.write(st.session_state.decoder.route_summary)
        st.write(st.session_state.decoder.routes_extended_df)
        st.session_state.decoder.solution.routes.to_csv(
            "data/test/temp_vroom_solution.csv", index=False
        )
        st.session_state.decoder.unassigned_route_df.to_csv(
            "data/test/unassigned_route_df.csv", index=False
        )
        st.session_state.decoder.stop_df.to_csv("data/test/stop_df.csv", index=False)
        st.session_state.decoder.matrix_df.to_csv(
            "data/test/matrix_df.csv", index=False
        )
        st.session_state.decoder.stop_sequence_info.to_csv(
            "data/test/stop_sequence_info.csv", index=False
        )
        st.session_state.decoder.travel_leg_info.to_file(
            "data/test/travel_leg_info.geojson", driver="GeoJSON"
        )
        import pickle

        with open("data/test/matrix.pickle", "bw") as f:
            pickle.dump(st.session_state.decoder.matrix, f)

        # st.write(st.session_state.decoder.travel_leg_info)


set_page_config()
st.sidebar.header("Session status")
side_bar_status = side_bar_progress.view_sidebar()
check_previous_steps_completed()
view_instructions()
display_routes()
display_excluded_stops()
start_routing()
side_bar_progress.update_side_bar(side_bar_status)
