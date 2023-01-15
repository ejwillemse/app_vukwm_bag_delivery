import streamlit as st

import app_vukwm_bag_delivery.home.presenters.load_input_data as load_input_data
import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.util_presenters.check_password import check_password
from app_vukwm_bag_delivery.util_views.return_session_status import return_full_status


def set_page_config():
    st.set_page_config(
        layout="wide",
        page_title="Home",
        initial_sidebar_state="expanded",
    )

    st.title("Bag delivery routing")


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


set_page_config()

if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line

side_bar_status = side_bar_progress.view_sidebar()
view_instructions()

if not return_session_status.check_raw_jobs_loaded():
    with st.spinner("Initiating session and loading data..."):
        load_input_data.load_data()


st.markdown(return_full_status())
side_bar_progress.update_side_bar(side_bar_status)
