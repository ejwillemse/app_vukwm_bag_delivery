import streamlit as st


def return_full_status():
    if "stop_data" in st.session_state:
        data_loaded_tickbox = " :white_check_mark: Job data have been imported and can be inspected in the `Review Jobs Data` page.\n"
    else:
        data_loaded_tickbox = " :red_circle: Job data has not yet been imported.\n"

    if "fleet" in st.session_state:
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
{fleet_loaded_tickbox}
{routes_generated_tickbox}
{routes_dispatched_tickbox}
"""
    return mark_down


def return_short_status():
    if "stop_data" in st.session_state:
        data_loaded_tickbox = " :white_check_mark: Job data imported\n"
    else:
        data_loaded_tickbox = " :red_circle: Job data imported\n"

    if "fleet" in st.session_state:
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
{fleet_loaded_tickbox}
{routes_generated_tickbox}
{routes_dispatched_tickbox}
"""
    return mark_down
