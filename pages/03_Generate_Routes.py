import pandas as pd
import streamlit as st

import app_vukwm_bag_delivery.generate_routes.presenters.extract_high_level_summary as extract_high_level_summary
import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.generate_routes.presenters.decode_solution import (
    decode_solution,
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
from app_vukwm_bag_delivery.update_routes import update_routes_test_widget
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
        st.markdown("### Generating routes")
        st.markdown(
            """
        The shift start and end times can be edited by clicking on the cell values in the table.
        Some basic hints are given as to avoid unsused routes, or when jobs cannot be assigned to any routes. These involve going back and editing the vehicles, or manually adjusting the routes.
        """
        )
        st.video(st.secrets["videos"]["video6"])


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


def routing_steps():
    st.write("Routing steps status")
    step_place_holder1 = st.empty()
    step_place_holder1.write(":white_circle: Fleet and stop data prepared")
    step_place_holder2 = st.empty()
    step_place_holder2.write(":white_circle: Map data loaded")
    step_place_holder3 = st.empty()
    step_place_holder3.write(":white_circle: Routing engine setup completed")
    step_place_holder4 = st.empty()
    step_place_holder4.write(":white_circle: Routes generated")
    step_place_holder5 = st.empty()
    step_place_holder5.write(":white_circle: Analyses completed")
    process_input_data()
    step_place_holder1.markdown(":white_check_mark: Fleet and stop data prepared")
    generate_matrix_inputs()
    step_place_holder2.markdown(":white_check_mark: Map data loaded")
    generate_vroom_input()
    step_place_holder3.markdown(":white_check_mark: Routing engine setup completed")
    solve()
    step_place_holder4.markdown(":white_check_mark: Routes generated")
    decode_solution()
    step_place_holder5.markdown(":white_check_mark: Analyses completed")


def show_route_sum():
    st.markdown("**Route summary**: high level route KPIs")
    st.write(extract_high_level_summary.extract_high_level_summary())
    with st.expander(
        "Click here for insights into making the routes more balanced, reducing the fleet size and why the vehicles may start their shift late"
    ):
        st.markdown(
            """
            If there is excess capacity in the routes, some of the routes may become unbalanced. In this case, some routes maybe very long, and others very short. This is typically the lowest overall cost solution, but can cause some operational issues.

            The following changes to can be made to ensure better balanced routes:\n
            1. **Make the shifts start later or end sooner:** go back to the `Select Vehicles` page and reduce the shift durations of the selected vehicles. This will limit the number of jobs that can be assigned to each vehicle. The jobs will then be spread over better over available vehicles.
            2. **Extend the shift and reducing the fleet:** go back to the `Select Vehicles` page and extend the shift durations of the selected vehicles. This could result in one less vehicle reqiured and a better balance amongst the other vehicles.
            3. **Manual move jobs to the underutilised vehicle:** go to the `Update Routes` page and manually move some of the jobs to underutilised vehicles. The optimal route per vehicle can still be calculated, ensuring that the routes are efficient.

            If there are some routes that have very jobs, it may be possible to increase the shift duration of the other routes to get rid of the short route all together.

            If the vehicles are not fully utilised, it is sometimes better to start the routes later than prescriped. This is due to some sites opening up later in the day. Allowing the vehicles to start later means they avoid having to circle back to sites when they are opened, or waiting at sites to open.
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
    if return_session_status.check_route_generation_completed():
        st.subheader("Route summary")
        st.markdown(
            "Below is a high level summary of the routes. Full route info can be viewed in the `View Routes` page. Manual changes to the routes can be made in `Update Routes`"
        )
        show_route_sum()
        show_unused_vehicles()
        show_unscheduled_stops()


def routing():
    start = st.button("Generate routes")
    if start:
        routing_steps()
        st.session_state.data = None
        st.session_state.edit_routes = None
        update_routes_test_widget.initialize_state(clear_all=True)
        st.session_state.routes_manually_edits = False
        st.session_state.data_07_reporting["unserviced_in_route_stops"] = pd.DataFrame()


set_page_config()
side_bar_status = side_bar_progress.view_sidebar()
check_previous_steps_completed()
view_instructions()
display_routes()
display_excluded_stops()
routing()
show_route_summary()
side_bar_progress.update_side_bar(side_bar_status)
