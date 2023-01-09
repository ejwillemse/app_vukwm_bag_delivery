import streamlit as st


def check_intermediate_unassigned_jobs_loaded():
    return (
        "data_02_intermediate" in st.session_state
        and "unassigned_stops" in st.session_state.data_02_intermediate
        and "unassigned_jobs" in st.session_state.data_02_intermediate
    )


def check_jobs_excluded_from_route():
    return (
        "data_02_intermediate" in st.session_state
        and "user_confirmed_removed_unassigned_stops"
        in st.session_state.data_02_intermediate
        and st.session_state.data_02_intermediate[
            "user_confirmed_removed_unassigned_stops"
        ].shape[0]
        > 0
    )


def check_intermediate_unassigned_fleet_loaded():
    return (
        "data_02_intermediate" in st.session_state
        and "unassigned_routes" in st.session_state.data_02_intermediate
        and st.session_state.data_02_intermediate["unassigned_routes"].shape[0]
    )


def return_full_status():
    if check_intermediate_unassigned_jobs_loaded():
        data_loaded_tickbox = " :white_check_mark: Job data have been imported and can be inspected in the `Review Jobs Data` page.\n"
    else:
        data_loaded_tickbox = " :red_circle: Job data has not yet been imported.\n"

    if check_jobs_excluded_from_route():
        data_excluded_tickbox = " :large_orange_diamond: Jobs have been manually excluded from delivery via the `Review Jobs Data` page.\n"
    else:
        data_excluded_tickbox = ""

    if check_intermediate_unassigned_fleet_loaded():
        fleet_loaded_tickbox = (
            " :white_check_mark: Vehicles have been selected for routing.\n"
        )
    else:
        fleet_loaded_tickbox = " :red_circle: Vehicles still have to be selected for routing. Please go to the `Select Vehicles` page.\n"

    if "assigned_jobs" in st.session_state:
        routes_generated_tickbox = " :white_check_mark: Routes have been generated for the vehicles and can be inspected in the `View Routes` page and modified in the `Update Routes` page.\n"
    else:
        routes_generated_tickbox = " :red_circle: Routes still have to be generated for the vehicles. Please go to `Generate Routes` page.\n"

    if "jobs_dispatched" in st.session_state:
        routes_dispatched_tickbox = (
            " :white_check_mark: Routes have been dispatched to the drivers.\n"
        )
    else:
        routes_dispatched_tickbox = " :red_circle: Routes still have to be dispatched to the drivers. Please go to the `Dispatch Routes` page.\n"
    mark_down = f"""
Status of session steps:\n 
{data_loaded_tickbox}
{data_excluded_tickbox}
{fleet_loaded_tickbox}
{routes_generated_tickbox}
{routes_dispatched_tickbox}
"""
    return mark_down


def return_short_status():

    if check_intermediate_unassigned_jobs_loaded():
        data_loaded_tickbox = " :white_check_mark: Job data imported\n"
    else:
        data_loaded_tickbox = " :red_circle: Job data imported\n"

    if check_jobs_excluded_from_route():
        data_excluded_tickbox = " :large_orange_diamond: Jobs manually excluded\n"
    else:
        data_excluded_tickbox = ""

    if check_intermediate_unassigned_fleet_loaded():
        fleet_loaded_tickbox = " :white_check_mark: Vehicles selected\n"
    else:
        fleet_loaded_tickbox = " :red_circle: Vehicles selected\n"

    if "assigned_jobs" in st.session_state:
        routes_generated_tickbox = " :white_check_mark: Routes generated\n"
    else:
        routes_generated_tickbox = " :red_circle: Routes generated\n"

    if "jobs_dispatched" in st.session_state:
        routes_dispatched_tickbox = " :white_check_mark: Routes dispatched\n"
    else:
        routes_dispatched_tickbox = " :red_circle: Routes dispatched\n"
    mark_down = f"""
{data_loaded_tickbox}
{data_excluded_tickbox}
{fleet_loaded_tickbox}
{routes_generated_tickbox}
{routes_dispatched_tickbox}
"""
    return mark_down
