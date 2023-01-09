import streamlit as st

from app_vukwm_bag_delivery.generate_routes import start_routing
from util_views.return_session_status import (
    return_side_bar,
    return_side_short,
)
from presenters.utils.check_password import check_password

st.set_page_config(
    layout="wide",
    page_title="Welcome",
    initial_sidebar_state="expanded",
)


if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line

st.title("Generate routes")

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

stop = False
if "fleet" not in st.session_state:
    st.warning(
        "Vehicles have not yet been configured and selected. Please go to the 'Select vehicles' page."
    )
    stop = True


if "unassigned_stops_date" not in st.session_state:
    st.warning(
        "Delivery jobs have not yet been uploaded. Please go to the 'Review Jobs Data' page."
    )

if stop is True:
    st.stop()

st.write("Routes will be generated for the following vehicles:")
st.write(st.session_state.fleet)

start_routing()

status_text.markdown(return_side_short())
