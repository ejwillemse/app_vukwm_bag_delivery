import streamlit as st

from app_vukwm_bag_delivery.util_views.return_session_status import return_short_status


def view_sidebar():
    st.sidebar.header("Session status")
    status_text = st.sidebar.empty()
    status_text.markdown(return_short_status())
    return status_text


def update_side_bar(status_text):
    status_text.markdown(return_short_status())

