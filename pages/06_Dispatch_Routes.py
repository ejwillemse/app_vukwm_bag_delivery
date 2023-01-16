import datetime

import streamlit as st

import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.dispatch_routes.excel_download import download_results
from app_vukwm_bag_delivery.dispatch_routes.format_assigned_jobs import (
    create_formatted_assigned_jobs,
    get_route_totals,
)
from app_vukwm_bag_delivery.dispatch_routes.route_sheet_cell_gen import (
    generate_sheet_cells,
)
from app_vukwm_bag_delivery.dispatch_routes.route_sheet_gsheet_generation import (
    write_google_sheet,
)
from app_vukwm_bag_delivery.util_presenters.check_password import check_password


def set_page_config():
    st.set_page_config(
        layout="wide",
        page_title="Dispatch routes",
        initial_sidebar_state="expanded",
    )
    st.title("Dispatch and download routes")


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


def show_assigned_inventory():
    st.markdown("Vehicle product inventory:")
    with st.expander(
        "Click here to view the required product inventory per vehicle", False
    ):
        st.write(
            st.session_state.data_07_reporting["assigned_jobs_download_product_totals"]
        )


def show_assigned_routes():
    st.markdown("Final job assignment:")
    with st.expander(
        "Click here to view job lists with vehicle and sequence assignments"
    ):
        st.write(st.session_state.data_07_reporting["assigned_jobs_download"])


def download():
    st.subheader("Download results")
    xl_download = download_results()
    st.download_button(
        label="Download job list as excel file",
        data=xl_download,
        file_name=f"vukwm_bag_delivery_job_list_{datetime.datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss')}.xlsx",
    )


def create_route_sheet():
    st.subheader("Create printable route sheets")
    st.markdown(
        "Click on the button below to generate a printable route sheet. A google-sheet link will be created. From there, the route sheets can be further edited and printed "
    )
    gen_sheet = st.button(
        "Create printable sheets",
        help="A google-sheet link will be created and printed on screen. From there, the route sheets can be further edited and printed.",
    )
    if gen_sheet:
        with st.spinner("Creating route-sheet values"):
            generate_sheet_cells()
        with st.spinner("Saving results to google-sheets"):
            write_google_sheet()
    if return_session_status.check_route_sheets_generated():
        st.markdown(
            "The route sheet can be viewed, edited and printed at the link below:"
        )
        st.write(st.session_state.data_07_reporting["route_sheet_urls"][-1][1])
        with st.expander(
            "Click here to view links to previously generated route sheets"
        ):
            st.write(st.session_state.data_07_reporting["route_sheet_urls"])


set_page_config()
side_bar_status = side_bar_progress.view_sidebar()
check_previous_steps_completed()
view_instructions()
create_formatted_assigned_jobs()
get_route_totals()
show_assigned_inventory()
show_assigned_routes()
download()
create_route_sheet()
side_bar_progress.update_side_bar(side_bar_status)
