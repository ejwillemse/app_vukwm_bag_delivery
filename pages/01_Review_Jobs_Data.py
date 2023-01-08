import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from st_aggrid import AgGrid, DataReturnMode, GridOptionsBuilder, GridUpdateMode

from app_vukwm_bag_delivery.aggregates import combine_orders
from app_vukwm_bag_delivery.render_order_map import return_order_map_html
from app_vukwm_bag_delivery.return_session_staus import (
    return_side_bar,
    return_side_short,
)
from check_password import check_password
from routing_job_selection import process_data_unassigned_jobs

if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line

st.title("Review delivery jobs and select delivery date")

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

if "stop_data" not in st.session_state:
    st.warning("Job data not loaded during session.")
    st.stop()  # App won't run anything after this line

process_data_unassigned_jobs()

st.header("Inspect job data")
html = return_order_map_html(st.session_state.unassigned_stops_date)
components.html(html, height=500)
st.write(st.session_state.unassigned_stops_date)

with st.expander("Filter jobs to be EXCLUDED from routing:"):
    gb = GridOptionsBuilder.from_dataframe(st.session_state.unassigned_stops_date)
    gridOptions = gb.build()
    grid_response = AgGrid(
        st.session_state.unassigned_stops_date,
        gridOptions=gridOptions,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.GRID_CHANGED,
        fit_columns_on_grid_load=False,
        theme="streamlit",  # Add theme color to the table
        enable_enterprise_modules=False,
        width="100%",
        reload_data=True,
        allow_unsafe_jscode=True,
    )
