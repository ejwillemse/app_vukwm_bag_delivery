import numpy as np
import streamlit as st

import app_vukwm_bag_delivery.update_routes.create_routing_objects as create_routing_objects

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
    # profiles = st.session_state.data_02_intermediate["unassigned_routes"]
    # st.write(profiles)
    # st.write(ROUTE_ID)
    # profiles = profiles.loc[profiles["Vehicle id"] == ROUTE_ID]
    # st.write(profiles)
    # if profiles.shape[0] > 0:
    #     st.write(profiles)
    #     new_profile = profiles.iloc[0]["Type"]
    # else:
    #     new_profile = np.nan
    if len(st.session_state.selected_data) > 0:
        st.session_state.data.loc[
            st.session_state.data["selected"], ROUTE_ID
        ] = new_route_id
        # st.session_state.data.loc[
        #     st.session_state.data["selected"], "Vehicle profile"
        # ] = new_profile
        st.experimental_rerun()
    else:
        st.warning(f"No points were selected...")


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
        if new_route_id != "":
            cap_button = st.button(
                key="button1",
                label=f"Confirm change",
            )
            if cap_button:
                update_selected_points(new_route_id)


def reroute():
    create_routing_objects.reroute()
