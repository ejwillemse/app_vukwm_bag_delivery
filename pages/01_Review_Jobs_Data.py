import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.review_jobs_data.presenters.edit_data import edit_data
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
from app_vukwm_bag_delivery.util_presenters.filters.filter_dataframe import (
    filter_df_widget,
)

STOP_VIEW_COLUMNS = [
    "Ticket No",
    "Customer Bk",
    "Site Bk",
    "Site Name",
    "Transport Area Code",
    "Product Name",
    "Quantity",
    "Order Weight (kg)",
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
    st.title("Review delivery jobs")


def view_instructions():
    with st.expander("Instructions"):
        st.markdown("### Using the map")
        st.markdown("Scroll in and out with a mouse wheel for zooming.")
        st.markdown(
            "Note: the map view is not saved and will reset when you leave the page."
        )
        st.video(st.secrets["videos"]["video2"])
        st.markdown("### Inspecting and updating time-windows")
        st.markdown(
            """
        Note: Filtering some tables results in records dissapearing, even when removing the filter. 
        To get all the records back, go to antoher page, and then back to the current one."""
        )
        st.video(st.secrets["videos"]["video3"])
        st.markdown("### Searching and excluding stops from routing")
        st.markdown(
            "Also shown are some special filtering and other table commande. Note that this is not available in all tables."
        )
        st.video(st.secrets["videos"]["video4"])


def check_previous_steps_completed():
    if (
        "data_02_intermediate" not in st.session_state
        or "unassigned_stops" not in st.session_state.data_02_intermediate
        or "unassigned_jobs_editable" not in st.session_state.data_02_intermediate
    ):
        st.warning("Job data not loaded during session. Please go back to `Home` page")
        st.stop()  # App won't run anything after this line


def edit_select_data():
    with st.expander("Insutrctions", expanded=True):
        st.markdown(
            """
Edit any data and click save when completed. You can also deselect rows by clicking on the checkbox.
To search for specific values, press `constrol + F` and type in the search term. On a mac, use `command + F`.
        """
        )
    edit_data()


def view_product_summary():
    st.markdown("View stop info per transport area")
    st.write(
        calc_route_product_summary(
            st.session_state.data_02_intermediate["unassigned_jobs_editable"]
        )
    )


def view_all_stops():
    with st.expander("View all stops"):
        data = filter_df_widget(
            st.session_state.data_02_intermediate["unassigned_jobs_editable"].rename(
                columns=STOP_VIEW_COLUMNS_RENAME
            )[STOP_VIEW_COLUMNS]
        )
        st.write(data)


def view_stops_map():
    html = return_order_map_html(
        st.session_state.data_02_intermediate["unassigned_jobs_editable"]
    )
    components.html(html, height=500)


def confirm_removal():
    pressed = st.button("Click here to save stop EXCLUSIONS")
    if pressed:
        if (
            "removed_unassigned_stops" in st.session_state.data_02_intermediate
            and st.session_state.data_02_intermediate["unassigned_jobs_editable"].shape[
                0
            ]
            > 0
        ):
            if (
                "user_confirmed_removed_unassigned_stops"
                not in st.session_state.data_02_intermediate
            ):
                st.session_state.data_02_intermediate[
                    "user_confirmed_removed_unassigned_stops"
                ] = pd.DataFrame()
            st.session_state.data_02_intermediate[
                "user_confirmed_removed_unassigned_stops"
            ] = (
                pd.concat(
                    [
                        st.session_state.data_02_intermediate[
                            "user_confirmed_removed_unassigned_stops"
                        ],
                        st.session_state.data_02_intermediate[
                            "removed_unassigned_stops"
                        ]
                        .rename(columns=STOP_VIEW_COLUMNS_RENAME)[STOP_VIEW_COLUMNS]
                        .copy(),
                    ]
                )
                .drop_duplicates()
                .reset_index(drop=True)
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
    data = st.session_state.data_02_intermediate["unassigned_jobs_editable"]
    n_stops_in = data.shape[0]
    data = data.rename(columns=STOP_VIEW_COLUMNS_RENAME)[STOP_VIEW_COLUMNS]
    modify = st.radio(
        "Select specific or all filtered stops for exclusion",
        ["All filtered stops", "Specificically selected stops"],
    )
    data = filter_df_widget(data, key="view_select_removal_stops")
    if modify == "All filtered stops":
        selected_df = data.copy()
        st.session_state.data_02_intermediate[
            "removed_unassigned_stops"
        ] = selected_df.copy()
    else:
        select_remove_dataframe(data)
        selected_df = return_selected()
    if selected_df.shape[0] > 0:
        st.write("Currently the following stops will be EXCLUDED for routing.")
        st.write(selected_df[STOP_VIEW_COLUMNS])
    else:
        st.write("Currently all stops will be included for routing.")
    if selected_df.shape[0] > n_stops_in * 0.5:
        st.warning(
            f"If you click on save, {int((selected_df.shape[0] / n_stops_in) * 100)} % of the stops will be removed. Please check that this is correct."
        )
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

    timelines = generate_known_unknown(unassigned_stops_tw)
    st.markdown("Sites with known open and close times")
    st.plotly_chart(
        timelines["known_open"], theme="streamlit", use_container_width=True
    )
    st.markdown("Sites with unknown open and close times")
    st.plotly_chart(
        timelines["unkown_open"], theme="streamlit", use_container_width=True
    )

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
    st.write(
        day_summary(st.session_state.data_02_intermediate["unassigned_jobs_editable"])
    )


def view_profile_type_summary():
    st.markdown("Delivery info per required delivery vehicle type")
    st.write(
        profile_type_summary(
            st.session_state.data_02_intermediate["unassigned_jobs_editable"]
        )
    )


def view_product_type_summary():
    st.markdown("Delivery info per product type")
    st.write(
        product_type_summary(
            st.session_state.data_02_intermediate["unassigned_jobs_editable"]
        )
    )


if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line

set_page_config()
side_bar_status = side_bar_progress.view_sidebar()
check_previous_steps_completed()

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "Instructions",
        "Edit and select data",
        "Delivery Summary",
        "Time windows",
    ]
)

with tab1:
    n_stops = st.session_state.data_02_intermediate["unassigned_jobs_editable"][
        "Site Bk"
    ].nunique()
    area2_stops = (
        st.session_state.data_02_intermediate["unassigned_jobs_editable"][
            "Transport Area"
        ]
        == 2
    ).sum()
    view_instructions()
    st.session_state["n_stops"] = n_stops
    st.session_state["area2_stops"] = area2_stops
    cols = st.columns(3)
    with cols[0]:
        st.metric("Total number of stops", n_stops)
    with cols[1]:
        st.metric("Stops in bicycle area (area 2)", area2_stops)
    with cols[2]:
        st.metric("Stops in other areas", n_stops - area2_stops)
    view_stops_map()

with tab2:
    st.subheader("Edit and select data")
    edit_select_data()


with tab3:
    st.subheader("Delivery summary")
    view_day_summary()
    view_profile_type_summary()
    view_product_type_summary()
    view_product_summary()
    view_all_stops()

with tab4:
    confirm_update_timewindows()

side_bar_status = side_bar_progress.update_side_bar(side_bar_status)
