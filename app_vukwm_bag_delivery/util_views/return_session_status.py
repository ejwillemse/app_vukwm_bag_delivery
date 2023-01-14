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


def check_route_generation_completed():
    return (
        "data_07_reporting" in st.session_state
        and "assigned_stops" in st.session_state.data_07_reporting
    )


def check_unused_routes():
    return (
        "data_07_reporting" in st.session_state
        and "unused_routes" in st.session_state.data_07_reporting
        and st.session_state.data_07_reporting["unused_routes"].shape[0] > 0
    )


def check_unserviced_stops():
    return (
        "data_07_reporting" in st.session_state
        and "unserviced_stops" in st.session_state.data_07_reporting
        and st.session_state.data_07_reporting["unserviced_stops"].shape[0] > 0
    )


def check_time_windows_update():
    return (
        "data_02_intermediate" in st.session_state
        and "save_updated_time_windows" in st.session_state.data_02_intermediate
        and st.session_state.data_02_intermediate["save_updated_time_windows"].shape[0]
        > 0
    )


def return_full_status():
    warnings = False
    if check_intermediate_unassigned_jobs_loaded():
        data_loaded_tickbox = " :white_check_mark: Job data have been imported and can be inspected in the `Review Jobs Data` page.\n"
    else:
        data_loaded_tickbox = " :red_circle: Job data has not yet been imported.\n"

    if check_time_windows_update():
        warnings = True
        data_time_windows_tickbox = " :large_orange_diamond: Delivery time windows of jobs have been manually updated via the `Review Jobs Data` page.\n"
    else:
        data_time_windows_tickbox = ""

    if check_jobs_excluded_from_route():
        warnings = True
        data_excluded_tickbox = " :large_orange_diamond: Jobs have been manually excluded from delivery via the `Review Jobs Data` page.\n"
    else:
        data_excluded_tickbox = ""

    if check_intermediate_unassigned_fleet_loaded():
        fleet_loaded_tickbox = (
            " :white_check_mark: Vehicles have been selected for routing.\n"
        )
    else:
        fleet_loaded_tickbox = " :red_circle: Vehicles still have to be selected for routing. Please go to the `Select Vehicles` page.\n"

    if check_route_generation_completed():
        routes_generated_tickbox = " :white_check_mark: Routes have been generated for the vehicles and can be inspected in the `View Routes` page and modified in the `Update Routes` page.\n"
    else:
        routes_generated_tickbox = " :red_circle: Routes still have to be generated for the vehicles. Please go to `Generate Routes` page.\n"

    if check_unused_routes():
        warnings = True
        unused_routes_tickbox = " :large_orange_diamond: Some of the vehicles are not being used. Go to `View Routes` for more details.\n"
    else:
        unused_routes_tickbox = ""

    if check_unserviced_stops():
        warnings = True
        check_unserviced_stops_tickbox = " :large_orange_diamond: Some of the jobs could not be allocated to vehicles. Go to `View Routes` for more details.\n"
    else:
        check_unserviced_stops_tickbox = ""

    if "jobs_dispatched" in st.session_state:
        routes_dispatched_tickbox = (
            " :white_check_mark: Routes have been dispatched to the drivers.\n"
        )
    else:
        routes_dispatched_tickbox = " :red_circle: Routes still have to be dispatched to the drivers. Please go to the `Dispatch Routes` page.\n"
    if warnings:
        warning_heading = "## Warnings"
    else:
        warning_heading = ""
    mark_down = f"""
Status of session steps:\n 
{data_loaded_tickbox}
{fleet_loaded_tickbox}
{routes_generated_tickbox}
{routes_dispatched_tickbox}
{warning_heading}
{data_time_windows_tickbox}
{data_excluded_tickbox}
{check_unserviced_stops_tickbox}
{unused_routes_tickbox}
"""
    return mark_down


def return_short_status():
    warnings = False
    if check_intermediate_unassigned_jobs_loaded():
        data_loaded_tickbox = " :white_check_mark: Job data imported\n"
    else:
        data_loaded_tickbox = " :red_circle: Job data imported\n"

    if check_time_windows_update():
        warnings = True
        data_time_windows_tickbox = " :large_orange_diamond: Time windows updated\n"
    else:
        data_time_windows_tickbox = ""

    if check_jobs_excluded_from_route():
        data_excluded_tickbox = " :large_orange_diamond: Jobs manually excluded\n"
        warnings = True
    else:
        data_excluded_tickbox = ""

    if check_intermediate_unassigned_fleet_loaded():
        fleet_loaded_tickbox = " :white_check_mark: Vehicles selected\n"
    else:
        fleet_loaded_tickbox = " :red_circle: Vehicles selected\n"

    if check_route_generation_completed():
        routes_generated_tickbox = " :white_check_mark: Routes generated\n"
    else:
        routes_generated_tickbox = " :red_circle: Routes generated\n"

    if check_unused_routes():
        warnings = True
        unused_routes_tickbox = " :large_orange_diamond: Unused vehicles\n"
    else:
        unused_routes_tickbox = ""

    if check_unserviced_stops():
        warnings = True
        check_unserviced_stops_tickbox = " :large_orange_diamond: Unallocated jobs\n"
    else:
        check_unserviced_stops_tickbox = ""

    if "jobs_dispatched" in st.session_state:
        routes_dispatched_tickbox = " :white_check_mark: Routes dispatched\n"
    else:
        routes_dispatched_tickbox = " :red_circle: Routes dispatched\n"

    if warnings:
        warning_heading = "## Warnings"
    else:
        warning_heading = ""

    mark_down = f"""
{data_loaded_tickbox}
{fleet_loaded_tickbox}
{routes_generated_tickbox}
{routes_dispatched_tickbox}
{warning_heading}
{data_time_windows_tickbox}
{data_excluded_tickbox}
{check_unserviced_stops_tickbox}
{unused_routes_tickbox}
"""
    return mark_down
