import pandas as pd
import streamlit as st

import app_vukwm_bag_delivery.presenters.load_input_data as load_input_data
import app_vukwm_bag_delivery.views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.presenters.check_password import check_password
from app_vukwm_bag_delivery.views.Home_view import set_page_config, view_instructions
from app_vukwm_bag_delivery.views.return_session_status import return_full_status

set_page_config()

if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line

side_bar_status = side_bar_progress.view_sidebar()
view_instructions()

if "stop_data" not in st.session_state:
    with st.spinner(f"Initiating session and loading data..."):
        load_input_data.load_data()

st.markdown(return_full_status())
side_bar_progress.update_side_bar(side_bar_status)
