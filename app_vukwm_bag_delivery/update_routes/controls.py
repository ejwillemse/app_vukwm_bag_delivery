import streamlit as st

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
    if len(st.session_state.selected_data) > 0:
        st.session_state.data.loc[
            st.session_state.data["selected"], ROUTE_ID
        ] = new_route_id
        st.experimental_rerun()
    else:
        st.warning(f"No points were selected...")


def activate_side_bar():
    routes = list(
        st.session_state.edit_routes["assigned_stops_orig"][ROUTE_ID].unique()
    )
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
