import pandas as pd
import streamlit as st

import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.select_vehicles.presenters.select_vehicles import (
    return_vehicle_grid,
    save_vehicle_selection,
)
from app_vukwm_bag_delivery.select_vehicles.views import get_defaults
from app_vukwm_bag_delivery.util_presenters.check_password import check_password

VEHICLE_VIEW_COLUMNS = [
    "Vehicle id",
    "Type",
    "Capacity (#boxes)",
    "Depot",
    "Shift start time",
    "Shift end time",
    "Average TAT per delivery (min)",
    "Dedicated transport zones",
    "Cost (£) per km",
    "Cost (£) per hour",
    "lat",
    "lon",
]


def set_page_config():
    st.set_page_config(
        layout="wide",
        page_title="Select and edit vehicles",
        initial_sidebar_state="expanded",
    )
    st.title("Select and edit vehicles")


if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line


def check_previous_steps_completed():
    if (
        "data_02_intermediate" not in st.session_state
        or "unassigned_stops" not in st.session_state.data_02_intermediate
        or "unassigned_jobs" not in st.session_state.data_02_intermediate
    ):
        st.warning("Job data not loaded during session. Please go back to `Home` page")
        st.stop()  # App won't run anything after this line


def view_instructions():
    with st.expander("Instructions"):
        st.markdown("### Selecting and editing vehicles")
        st.markdown(
            """
        Multiple transport zones can be assigned to a vehicle by entering the area numbers, seperated with a commma. 
        Areas not specified in the in the dedicated tranpsort zones can be allocated to any vehicle. 
        By default W04 is the bicycle and is assigned to zone 2. This can be manually changed.
        """
        )
        st.video(st.secrets["videos"]["video5"])


def clear_selection_removal():
    pressed = st.button("Click here to clear selection")
    if pressed:
        st.session_state.data_02_intermediate["unassigned_routes"] = pd.DataFrame()
        st.experimental_rerun()


def view_pre_selected_routes() -> None:
    if (
        "unassigned_routes" in st.session_state.data_02_intermediate
        and st.session_state.data_02_intermediate["unassigned_routes"].shape[0] > 0
    ):
        st.subheader("Vehicles currently selected for routing")
        st.write(
            st.session_state.data_02_intermediate["unassigned_routes"][
                VEHICLE_VIEW_COLUMNS
            ]
        )
        clear_selection_removal()


def confirm_selection(selected_df):
    pressed = st.button("Click here to save vehicle selection")
    if pressed:
        save_vehicle_selection(selected_df)


def select_vehicles():
    st.write(
        "The following vehicles are available for routing. Select the ones to be used:"
    )
    vehicle_df = get_defaults.return_vehicle_default()
    selected_df = return_vehicle_grid(vehicle_df)

    if selected_df.shape[0] > 0:
        st.write(
            f"The following {selected_df.shape[0]} vehicles will be used for deliveries:"
        )
        st.write(selected_df[VEHICLE_VIEW_COLUMNS])
        confirm_selection(selected_df[VEHICLE_VIEW_COLUMNS])


set_page_config()
st.sidebar.header("Session status")
side_bar_status = side_bar_progress.view_sidebar()
check_previous_steps_completed()
view_instructions()
select_vehicles()
view_pre_selected_routes()
side_bar_progress.update_side_bar(side_bar_status)
