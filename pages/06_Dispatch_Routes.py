import datetime
import time

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
    st.title("Dispatch and download routes")


if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line


def view_instructions():
    with st.expander("Instructions"):
        st.markdown(
            "### Final inspection and exporting the routes to excel and as printable route-sheets"
        )
        st.markdown(
            "Values in tables can be directly copied and pasted in excel for offline analysis."
        )
        st.video(st.secrets["videos"]["video11"])


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
        "Click here to view the required product inventory per vehicle", True
    ):
        st.write(
            st.session_state.data_07_reporting["assigned_jobs_download_product_totals"]
        )


def show_assigned_routes():
    st.markdown("Final job assignment:", True)
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
    with st.expander("Click here to create printable route sheets", True):
        st.markdown(
            "Click on the button below to generate a printable route sheets. A google-sheet link will be created. From there, the route sheets can be further edited and printed. Each tab in the sheet contains the route plan for each vehicle."
        )
        gen_sheet = st.button(
            "Create printable sheets",
            help="A google-sheet link will be created and printed on screen. From there, the route sheets can be further edited and printed.",
        )
        if gen_sheet:
            with st.spinner("Creating route-sheet values"):
                generate_sheet_cells()
            with st.spinner("Saving routes to google-sheets"):
                write_google_sheet()
        if return_session_status.check_route_sheets_generated():
            latest = st.session_state.data_07_reporting["route_sheet_urls"][-1]
            all = st.session_state.data_07_reporting["route_sheet_urls"]
            mardown_list = "\n".join([f"* [{x[0]}]({x[1]})" for x in all])
            st.markdown(
                "The latest generated route sheet can be viewed, edited and printed from the link below:"
            )
            st.markdown(f"* [{latest[0]}]({latest[1]})")
            st.markdown("")
            st.markdown("Links to route sheets from the current session:")
            st.markdown(mardown_list)
            st.markdown("")
        st.markdown(
            "All previously generated route sheet can be viewed [here](https://drive.google.com/drive/folders/1dJqOU6zc_sZYyh5MUfJhEvMuXZ221wLS)."
        )


def confirm_dispatch():
    st.write(
        "Enter `Dispatch routes` below and press enter to confirm that the routes should be dispatched."
    )
    input = st.text_input("")
    if input == "Dispatch routes":
        st.success("Dispatch complete")
        st.session_state["mobile_app_dispatch"] = True


def dispatch_routes():
    st.subheader("Dispatch routes to driver's mobile devices")
    if "jobs_dispatched" in st.session_state:
        st.success(
            "Routes have been dispatched to the drivers' mobile devices. This can only be performed once. Reload the app to make this action available again."
        )
        return None
    st.warning(
        "This step cannot be undone. Please ensure that all data is correct and that the final routes available under `View Routes` are the final ones to be dispatched."
    )
    dispatch_df = download_results()
    st.write(
        "Enter `Dispatch routes` below and press enter to confirm that the routes should be dispatched."
    )
    input = st.text_input("")
    if input == "Dispatch routes":
        pressed = st.button(
            "Are you sure you want to dispatch the routes?",
            help="Dispatch routes to driver's mobile devices",
        )
        if pressed:
            st.success(
                "Rouets have been dispatched. Actually, if you can kill the app within 3 seconds it won't be dispatched, so last chance..."
            )
            st.balloons()
            time.sleep(3)
            st.session_state["jobs_dispatched"] = True
            st.experimental_rerun()


set_page_config()
side_bar_status = side_bar_progress.view_sidebar()
check_previous_steps_completed()
view_instructions()
create_formatted_assigned_jobs()
get_route_totals()

tabs = st.tabs(
    [
        "Summary",
        "Print route sheets",
        "Dispatch to driver app",
        "Download dispatch sheet",
    ]
)

with tabs[0]:
    st.subheader("Dispatch summary")
    show_assigned_inventory()
    show_assigned_routes()
# download()
with tabs[1]:
    create_route_sheet()
with tabs[2]:
    dispatch_routes()
with tabs[3]:
    download()
side_bar_progress.update_side_bar(side_bar_status)
