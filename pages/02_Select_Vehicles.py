import streamlit as st

from app_vukwm_bag_delivery.select_vehicles import select_vehicles
from check_password import check_password

st.set_page_config(
    layout="wide",
    page_title="Welcome",
    initial_sidebar_state="expanded",
)


if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line


st.title("Select and edit vehicles")

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
select_vehicles()
