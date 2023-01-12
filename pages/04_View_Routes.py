import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.util_presenters.check_password import check_password
from app_vukwm_bag_delivery.view_routes.generate_route_gant import return_gant
from app_vukwm_bag_delivery.view_routes.generate_route_map import return_map


def set_page_config():
    st.set_page_config(
        layout="wide",
        page_title="View routes",
        initial_sidebar_state="expanded",
    )
    st.title("View routes")


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
            "Vehicles have not yet been configured and selected. Please go to the `Select Vehicles` page."
        )
        stop = True
    if not return_session_status.check_route_generation_completed():
        st.warning(
            "Routes have not yet been generated. Please go to the `Generate Routes` page."
        )
        stop = True  # App won't run anything after this line
    if stop:
        st.stop()


def display_routes():
    html = return_map()
    components.html(html, height=750)


def display_gant():
    detail = st.radio(
        "Label detail",
        options=["Simple", "Detailed"],
        help="`Detailed` works best if the resolution is at 15min.",
    )
    detail_flag = {"Simple": False, "Detailed": True}[detail]
    gant = return_gant(detail_flag)
    st.plotly_chart(gant, theme="streamlit", use_container_width=True)


set_page_config()
side_bar_status = side_bar_progress.view_sidebar()
check_previous_steps_completed()
view_instructions()
display_routes()
display_gant()
# display_excluded_stops()
# routing()
# show_route_summary()
side_bar_progress.update_side_bar(side_bar_status)

# st.sidebar.header("Session status")
# status_text = st.sidebar.empty()
# status_text.markdown(return_side_short())

# with st.expander("Instructions"):
#     st.markdown(
#         """
#     Perform the following steps to edit vehicle information and select the vehicles to be routed. If no vehicles are selected, it is assumed that the entire fleet is available for routing.

#     * Step 1: Inspect the vehicle information in the table.
#     * Step 2: Edit the vehicle informaiton where required.
#     * Step 3: Select active vehicles by clicking on the boxes next to the vehicle ID.
#     * Step 4: Click on "Update" to load the vehicles.
#     """
#     )


# if "routes" not in st.session_state:
#     st.warning(
#         "Routes have not yet been generated. Please go to the 'Generate Routes' page."
#     )
#     st.stop()

# routes = st.session_state.routes.copy()
# route_maps = st.session_state.route_maps
# route_sum = summarise_route(routes)
# st.write("Route summary")
# st.write(route_sum)

# components.html(route_maps, height=750)

# st.write("Route timeline")
# st.plotly_chart(generate_timeline(routes), theme="streamlit", use_container_width=True)
