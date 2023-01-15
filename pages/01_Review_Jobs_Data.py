import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.review_jobs_data.presenters.inspect_timewindows import (
    generate_known_unknown,
)
from app_vukwm_bag_delivery.review_jobs_data.presenters.select_remove_stops import (
    return_selected,
    select_remove_dataframe,
)
from app_vukwm_bag_delivery.review_jobs_data.presenters.update_time_windows import (
    update_timewindows_selection,
)
from app_vukwm_bag_delivery.review_jobs_data.views.render_unassigned_stops_map import (
    return_order_map_html,
)
from app_vukwm_bag_delivery.review_jobs_data.views.summarise_inputs import (
    calc_route_product_summary,
    day_summary,
    product_type_summary,
    profile_type_summary,
)
from app_vukwm_bag_delivery.util_presenters.check_password import check_password

STOP_VIEW_COLUMNS = [
    "Ticket No",
    "Customer Bk",
    "Site Bk",
    "Site Name",
    "Transport Area Code",
    "Product Name",
    "Quantity",
    "Created Date",
    "Required Date",
    "Notes",
    "on hold",
    "Schedule ID",
    "Scheduled Date",
    "Completed Date",
    "Registration No",
    "Site Address1",
    "Site Address2",
    "Site Address3",
    "Site Address4",
    "Site Address5",
    "Site Post Town",
    "Site Post Code",
    "Site Latitude",
    "Site Longitude",
    "Site Address",
    "Transport Area",
]
STOP_VIEW_COLUMNS_RENAME = {"transport_area_number": "Transport Area"}


def set_page_config():
    st.set_page_config(
        layout="wide",
        page_title="Review Jobs Data",
        initial_sidebar_state="expanded",
    )
    st.title("Review delivery jobs")


@st.experimental_memo
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
    if (
        "data_02_intermediate" not in st.session_state
        or "unassigned_stops" not in st.session_state.data_02_intermediate
        or "unassigned_jobs" not in st.session_state.data_02_intermediate
    ):
        st.warning("Job data not loaded during session. Please go back to `Home` page")
        st.stop()  # App won't run anything after this line


def view_product_summary():
    st.markdown("View stop info per transport area")
    st.write(
        calc_route_product_summary(
            st.session_state.data_02_intermediate["unassigned_jobs"]
        )
    )


def view_all_stops():
    with st.expander("View all stops"):
        st.write(
            st.session_state.data_02_intermediate["unassigned_jobs"].rename(
                columns=STOP_VIEW_COLUMNS_RENAME
            )[STOP_VIEW_COLUMNS]
        )


def view_stops_map():
    html = return_order_map_html(
        st.session_state.data_02_intermediate["unassigned_stops"]
    )
    components.html(html, height=500)


def confirm_removal():
    pressed = st.button("Click here to save stop EXCLUSIONS")
    if pressed:
        if "removed_unassigned_stops" in st.session_state.data_02_intermediate:
            st.session_state.data_02_intermediate[
                "user_confirmed_removed_unassigned_stops"
            ] = (
                st.session_state.data_02_intermediate["removed_unassigned_stops"]
                .rename(columns=STOP_VIEW_COLUMNS_RENAME)[STOP_VIEW_COLUMNS]
                .copy()
            )


def clear_selection_removal():
    pressed = st.button("Click here to clear selection")
    if pressed:
        st.session_state.data_02_intermediate[
            "removed_unassigned_stops"
        ] = pd.DataFrame()
        st.session_state.data_02_intermediate[
            "user_confirmed_removed_unassigned_stops"
        ] = pd.DataFrame()
        st.experimental_rerun()


def view_select_removal_stops() -> None:
    st.subheader("Exclude jobs from delivery")
    with st.expander("Select stops to be excluded from routing"):
        data = st.session_state.data_02_intermediate["unassigned_jobs"]
        data = data.rename(columns=STOP_VIEW_COLUMNS_RENAME)[STOP_VIEW_COLUMNS]
        select_remove_dataframe(data)
        selected_df = return_selected()
        if selected_df.shape[0] > 0:
            st.write("Currently the following stops will be EXCLUDED for routing.")
            st.write(selected_df[STOP_VIEW_COLUMNS])
        else:
            st.write("Currently all stops will be included for routing.")
        confirm_removal()


def view_pre_edited_timewindows() -> None:
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
    pressed = st.button("Click here to save time window updates")
    if pressed:
        st.session_state.data_02_intermediate["save_updated_time_windows"] = selected_df


def clear_selection():
    pressed = st.button("Click here to clear time window updates")
    if pressed:
        st.session_state.data_02_intermediate[
            "save_updated_time_windows"
        ] = pd.DataFrame()
        st.session_state.data_02_intermediate["updated_time_windows"] = pd.DataFrame()
        st.write(st.session_state.data_02_intermediate["updated_time_windows"].shape[0])


def confirm_update_timewindows() -> None:
    st.subheader("Confirm delivery time windows")
    unassigned_stops_tw = st.session_state.data_02_intermediate["unassigned_stops_tw"]
    with st.expander("View time window gantt chart"):
        timelines = generate_known_unknown(unassigned_stops_tw)
        st.markdown("Sites with known open and close times")
        st.plotly_chart(
            timelines["known_open"], theme="streamlit", use_container_width=True
        )
        st.markdown("Sites with unknown open and close times")
        st.plotly_chart(
            timelines["unkown_open"], theme="streamlit", use_container_width=True
        )
    with st.expander("Inspect and update time windows"):
        updated_time_windows = update_timewindows_selection()
        if updated_time_windows.shape[0] > 0:
            st.write(
                f"The following {updated_time_windows.shape[0]} site's delivery time windows have been edited:"
            )
            st.write(updated_time_windows)
            confirm_selection(updated_time_windows)
            # clear_selection()


def view_pre_selected_stops() -> None:
    if (
        "user_confirmed_removed_unassigned_stops"
        in st.session_state.data_02_intermediate
        and st.session_state.data_02_intermediate[
            "user_confirmed_removed_unassigned_stops"
        ].shape[0]
        > 0
    ):
        st.subheader("Jobs manually selected and will be EXCLUDED from delivery")
        st.write(
            st.session_state.data_02_intermediate[
                "user_confirmed_removed_unassigned_stops"
            ].rename(columns=STOP_VIEW_COLUMNS_RENAME)[STOP_VIEW_COLUMNS]
        )
        clear_selection_removal()


def view_day_summary():
    st.markdown("Delivery info per day")
    st.write(day_summary(st.session_state.data_02_intermediate["unassigned_jobs"]))


def view_profile_type_summary():
    st.markdown("Delivery info per required delivery vehicle type")
    st.write(
        profile_type_summary(st.session_state.data_02_intermediate["unassigned_jobs"])
    )


def view_product_type_summary():
    st.markdown("Delivery info per product type")
    st.write(
        product_type_summary(st.session_state.data_02_intermediate["unassigned_jobs"])
    )


if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line

set_page_config()
side_bar_status = side_bar_progress.view_sidebar()
check_previous_steps_completed()
view_instructions()
view_stops_map()
st.subheader("Delivery summary")
with st.expander("Show/hide summaries", False):
    view_day_summary()
    view_profile_type_summary()
    view_product_type_summary()
    view_product_summary()

view_all_stops()
confirm_update_timewindows()
view_select_removal_stops()
view_pre_selected_stops()
side_bar_status = side_bar_progress.update_side_bar(side_bar_status)
