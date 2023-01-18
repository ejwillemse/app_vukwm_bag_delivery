import logging

import numpy as np
import streamlit as st

import app_vukwm_bag_delivery.update_routes.create_routing_objects as create_routing_objects
import app_vukwm_bag_delivery.update_routes.process_assigned_data as process_assigned_data
from app_vukwm_bag_delivery.update_routes import update_routes_test_widget

ROUTE_ID = "Vehicle Id"

LAT_LON_QUERIES = [
    "lat_lon_click_query",
    "lat_lon_select_query",
    "lat_lon_hover_query",
]


def reset_state_callback():
    """Resets all filters and increments counter in Streamlit Session State"""
    st.session_state.counter += 1
    for query in LAT_LON_QUERIES:
        st.session_state[query] = set()
    st.session_state.aggrid_select = set()
    st.session_state.current_query = {}
    st.session_state.data = st.session_state.data.assign(selected=False)


def update_selected_points(new_route_id):
    """also need to update profiles..."""
    if len(st.session_state.selected_data) > 0:
        st.session_state.data.loc[
            st.session_state.data["selected"], ROUTE_ID
        ] = new_route_id
        create_routing_objects.reroute()
        st.session_state.data = None
        st.experimental_rerun()
    else:
        st.warning(f"No points were selected...")
    return


def activate_side_bar():
    routes = list(
        st.session_state.edit_routes["assigned_stops_orig"][ROUTE_ID].unique()
    )
    routes.sort()
    with st.sidebar:
        st.button(key="button0", label="CLEAR SELECTION", on_click=reset_state_callback)
        st.session_state.route_filters = st.multiselect("Show routes", routes, routes)
        st.markdown("**Update route assignments**")
        routes_select = [""] + routes
        new_route_id = st.selectbox("Change selected stops to route", routes_select)
        cap_button = st.button(
            key="button1",
            label=f"Confirm change",
        )
        if cap_button:
            update_selected_points(new_route_id)
        st.markdown("**Save/restart edits**")
        clicked3 = st.button("Save edits")
        if clicked3:
            logging.info(
                "\n\n\nlogging::::saving editor sessions-----------------------"
            )
            process_assigned_data.update_unsused_routes()
            process_assigned_data.update_unserviced_stops()
            process_assigned_data.update_assigned_stops()
            update_routes_test_widget.reset_state_callback()
            st.session_state.data = None
            st.session_state.edit_routes = None
            update_routes_test_widget.initialize_state(clear_all=True)
            st.experimental_rerun()
        clicked2 = st.button("Restart")
        if clicked2:
            logging.info(
                "\n\n\nlogging::::restarting editor sessions-----------------------"
            )
            update_routes_test_widget.reset_state_callback()
            st.session_state.data = None
            st.session_state.edit_routes = None
            update_routes_test_widget.initialize_state(clear_all=True)
            st.experimental_rerun()
