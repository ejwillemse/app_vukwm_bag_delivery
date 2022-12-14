import leafmap.foliumap as leafmap
import streamlit as st

from util_views.return_session_status import (
    return_side_bar,
    return_side_short,
)
from presenters.utils.check_password import check_password

if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line

st.title("Edit routes routes")

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
st.write("To be released soon...")

# if "routes" not in st.session_state:
#     st.warning(
#         "Routes have not yet been generated. Please go to the 'Generate Routes' page."
#     )
#     st.stop()


st.title("Home")

st.markdown(
    """
A [streamlit](https://streamlit.io) app template for geospatial applications based on [streamlit-option-menu](https://github.com/victoryhb/streamlit-option-menu). 
To create a direct link to a pre-selected menu, add `?page=<app name>` to the URL, e.g., `?page=upload`.
https://share.streamlit.io/giswqs/streamlit-template?page=upload
"""
)

m = leafmap.Map(locate_control=True)
m.add_basemap("ROADMAP")
m.to_streamlit(height=700)

