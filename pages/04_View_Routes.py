import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components

import app_vukwm_bag_delivery.generate_routes.presenters.extract_high_level_summary as extract_high_level_summary
import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.util_presenters.check_password import check_password
from app_vukwm_bag_delivery.view_routes.generate_route_display import (
    return_assigned_stops_display,
)
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
    st.markdown("Manual changes to the routes can be made in `Update Routes`")


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


def show_route_sum():
    st.markdown("**Route summary**: high level route KPIs")
    st.write(extract_high_level_summary.extract_high_level_summary())
    with st.expander(
        "Click here for insights into making the routes more balanced or reducing the fleet size"
    ):
        st.markdown(
            """
            If there is excess capacity in the routes, some of the routes may become unbalanced. In this case, some routes maybe very long, and others very short. This is typically the lowest overall cost solution, but can cause some operational issues.

            The following changes to can be made to ensure better balanced routes:\n
            1. **Make the shifts start later or end sooner:** go back to the `Select Vehicles` page and reduce the shift durations of the selected vehicles. This will limit the number of jobs that can be assigned to each vehicle. The jobs will then be spread over better over available vehicles.
            2. **Extend the shift and reducing the fleet:** go back to the `Select Vehicles` page and extend the shift durations of the selected vehicles. This could result in one less vehicle reqiured and a better balance amongst the other vehicles.
            3. **Manual move jobs to the underutilised vehicle:** go to the `Update Routes` page and manually move some of the jobs to underutilised vehicles. The optimal route per vehicle can still be calculated, ensuring that the routes are efficient.
            """
        )


def show_unused_vehicles():
    if return_session_status.check_unused_routes():
        st.markdown(
            "**Unused vehicles**: the following vehicles were not assigned any stops"
        )
        st.write(extract_high_level_summary.extract_unused_routes())
        with st.expander("Click here for insights into avoiding unused vehicles"):
            st.markdown(
                """
                The following changes to can be made to ensure that all selected vehicles are used:\n
                 1. **Make the shifts start later or end sooner:** go back to the `Select Vehicles` page and reduce the shift durations of the selected vehicles. This will limit the number of jobs that can be assigned to each vehicle. The jobs will then be spread over all available vehicles.
                 2. **Manual move jobs to unused vehicles:** go to the `Update Routes` page and manually move some of the jobs to unassigned vehicles. The optimal route per vehicle can still be calculated, ensuring that the routes are efficient.
                """
            )
    else:
        st.markdown("All selected vehicles are being used.")


def show_unscheduled_stops():
    if return_session_status.check_unserviced_stops():
        st.markdown(
            "**Unserviced stops**: the following stops could not be included in any routes"
        )
        with st.expander("Click here to show/hide the stops", True):
            st.write(extract_high_level_summary.extract_unscheduled_stops())
        with st.expander("Click here for insights into avoiding unserviced stops"):
            st.markdown(
                """
                Unserviced stops can be caused by a number of factors. So some experimentation may required to find the best remedy. Below are some factors and possible solutions:\n
                 1. **There are not enough resources**: go back to the `Select Vehicles` page and select more vehicles.
                 2. **There is not enough time**: go back to the `Select Vehicles` page and extend the vehicle shifts.
                 3. **There are not enough vehicles with the required skills**: this ocurs when there are too many bicycle jobs for bicycles to service. In this case, more bicycles can be added, or their shifts extended.
                 4. **There are too many jobs with narrow and overlapping time-windows**: this occurs when there are a bunch of jobs at different sites with similar narrow time-windows. In this case, either add more vehicles or adjust the time-windows of the customers.
                 5. **Time windows fall outside shift hours**: some stops have time-windows that fall outside the vehicle shifts. In this case, either adjust the shift duration or the time-windows of the customers.

                 Another option is to go to the `Update Routes` page and manually add the unscheduled stops to vehicles. The indivual routes will still be optimised, with efforts made to ensure the routes are feasible.
                """
            )
    else:
        st.markdown("All stops are scheduled for service in the routes.")


def show_route_summary():
    st.subheader("Route summary")
    show_route_sum()
    show_unused_vehicles()
    show_unscheduled_stops()


def show_detailed_stop_info():
    st.subheader("Detailed stop info")
    with st.expander("Click here for detailed stop info and sequences", True):
        st.write(return_assigned_stops_display())


def filter_routes():
    vehicles = (
        st.session_state.data_07_reporting["assigned_stops"]["route_id"]
        .sort_values()
        .unique()
    )
    selected_vehicles = st.multiselect(
        "Select vehicles to focus on",
        vehicles,
        vehicles,
        help="Filtering applies to the map, gantt chart and detailed stop view.",
    )
    if selected_vehicles:
        st.session_state.view_routes = {"filter_vehicles": selected_vehicles}


set_page_config()
side_bar_status = side_bar_progress.view_sidebar()
check_previous_steps_completed()
view_instructions()
filter_routes()
display_routes()
display_gant()
show_route_summary()
show_detailed_stop_info()
side_bar_progress.update_side_bar(side_bar_status)
