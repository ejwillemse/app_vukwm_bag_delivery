import streamlit as st

from app_vukwm_bag_delivery.models.pipelines.summarise.sum_routes import route_summary


def extract_high_level_summary():
    assigned_stops = st.session_state.data_07_reporting["assigned_stops"]
    route_sum = route_summary(assigned_stops)
    return route_sum


def extract_unused_routes():
    unused_routes = st.session_state.data_07_reporting["unused_routes"]


def extract_unscheduled_stops():
    unscheduled_stops = st.session_state.data_07_reporting["unscheduled_stops"]
