import streamlit as st
import streamlit.components.v1 as components

from app_vukwm_bag_delivery.return_session_staus import (
    return_side_bar,
    return_side_short,
)
from check_password import check_password

if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line

st.title("View routes")

st.sidebar.header("Session status")
status_text = st.sidebar.empty()
status_text.markdown(return_side_short())

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


if "routes" not in st.session_state:
    st.warning(
        "Routes have not yet been generated. Please go to the 'Generate Routes' page."
    )
    st.stop()

routes = st.session_state.routes.copy()
route_maps = st.session_state.route_maps
components.html(route_maps, height=750)
