import logging

import pandas as pd

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
import streamlit as st

import app_vukwm_bag_delivery.home.presenters.load_input_data as load_input_data
import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.util_presenters.check_password import check_password
from app_vukwm_bag_delivery.util_views.return_session_status import return_full_status

# force restart


def set_page_config():
    st.set_page_config(
        layout="wide",
        page_title="VUKMWM Bag Delivery",
        initial_sidebar_state="expanded",
    )

    st.title("Bag delivery routing")


def view_instructions():
    with st.expander("Instructions"):
        st.markdown(
            """
        ## Welcome to the bag delivery routing app

        These info-boxes are contained in each page of the app and shows you how to use the app. Each info-box contained help for the specific page.
        
        ### Basic navigation

        On the left of the screen is a side-bar. The top of the side-bar can be used to navigate through different pages on the app. There are seven pages in total. Just click on the down-arrow in the side-bar to view all the pages.
        The bottom of the side-bar contains the status of the current session. There are certain steps that have to be completed to generate and dispatch routes. The status of the steps are shown on the left.

        If you are using the app from a small screen, the side-bar will autohide and appear, so you may have to click on it to make it show.

        On the top-right of the app is a settings options. A useful feature is `Record a screencast`. If you notice a bug, feel free to take and send us a screen-recording.
        
        ### Using the app

        A more detailed status break-down is shown on this screen.
        The status will also show warnings.

        There are four required and four optional steps that have to be completed to generate and dispatch routes:

        * **Step 1 Loading data (required):** The latest undelivered orders are automatically loaded when logging into the application. The status of all steps, including the data loading can be viewed from this page, i.e. the `Home page`.
        * **Step 2 Review Jobs Data (optional):** From this page you review the jobs data, as well s deselect jobs that should not be routed. This page also allows you to view and change the time-windows of customers.
        * **Step 3 Select Vehicles (required):** Select the vehicles that are available for routing. You can also edit key values for each vehcile, such as the shift start-times.
        * **Step 4 Generate Routes (required):** Generate routes and view their high-level KPIs. The page will also show you issues with the routing, such as unused vehicles, or jobs that could not be allocated to routes.
        * **Step 5 View Routes (optional):** View the routes in more detail as well as their KPIs.
        * **Step 6 Update Routes (optional):** Manually edit routes by reassigning jobs between vehicles. The impact of the edits on KPIs are immediately calculated.
        * **Step 7 Dispatch Routes (required):** Dispatch the routes to drivers. Currently the routes can be downloaded directly, or pushed to google-sheets in the form of properly formally route-sheets. The route-sheets can be printed and given to the drivers.

        ### Recommendations

        A few recommendations to get the most out of the app:

        * All information will be lost if the app is closed or refreshed. The ability to save the session is currently in development.
        * If you notice any strange behaviour, please take a screen-recording and share it with us. You can also try the following:
           * Go to another page, and then back to the page where you noticed this issue. This will cause the specific page to reload.
           * Refresh the app, but note that this will cause all steps and edits to be lost.
        * The `Update Routes` feature is still highly experimental and best done via a computer with a large screen.

        ### Known issues

        The following are know issues:

        1. Filtering some tables results in records dissapearing, even when removing the filter. 
           * Workaround: to get all the records back, go to antoher page, and then back to the current one.
        2. The Update Routes page refreshes all the time.
           * Workaround: unfortunately, only patience. This is an experimental feature, hence why this happens.
        3. The map in Update Routes page jumps around when panning and zooming.
           * Workaround: unfortunately, only patience. This is an experimental feature, hence why this happens. It does go back to actual viewpoint afte it jumps.

        ### Video walkthroug

        The following video shows a quick walk-through of the basic app usage:
        """
        )
        st.video(st.secrets["videos"]["video1"])
        st.markdown(
            """
        ### Contact info

        This app was developed by Waste Labs. Get in touch with us at <https://wastelabs.co/>"""
        )


def load_existing_input_data(df_upload):
    with st.spinner("Initiating session and processing existing data..."):
        load_input_data.upload_data(df_upload)


set_page_config()

if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line

side_bar_status = side_bar_progress.view_sidebar()
view_instructions()

if not return_session_status.check_raw_jobs_loaded():
    with st.spinner("Initiating session and processing uploaded data..."):
        load_input_data.load_data()

tabs = st.tabs(["View session status", "Upload jobs data", "Download jobs data"])

with tabs[0]:
    st.markdown(return_full_status())
    side_bar_progress.update_side_bar(side_bar_status)

with tabs[1]:
    st.markdown(
        "Upload a jobs data file. Note that there are strict formatting requirements. We recommend download an existing file and inspecting it."
    )
    df = st.file_uploader("Upload jobs data file")
    if df is not None:
        df_upload = pd.read_excel(df)
        pressed = st.button("Process file for routing")
        if pressed:
            load_existing_input_data(df_upload)
        with st.expander("View uploaded data"):
            st.write(df_upload)


with tabs[2]:
    st.markdown("Download the current or previous jobs data file.")
    load_input_data.load_jobs_file()
