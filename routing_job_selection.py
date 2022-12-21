import streamlit as st

import app_vukwm_bag_delivery.aggregates as aggregates


def stop_data_summary():
    stop_data = st.session_state.stop_data.copy()
    day_summary = aggregates.get_day_summary(stop_data).sort_values(
        ["Collection date"], ascending=False
    )
    st.write("Total number of stops and unassigned stops for delivery days:")
    st.dataframe(day_summary)
    if day_summary is not None:
        unique_dates = day_summary["Collection date"].unique()
        if unique_dates.shape[0] > 0:
            delivery_date = st.selectbox(
                label="Select a delivery date", options=unique_dates, index=1
            )
        else:
            delivery_date = None
        delivery_jobs = stop_data.loc[stop_data["collection_date"] == delivery_date]
        route_product_summary = aggregates.calc_product_summary(delivery_jobs)
        st.write(route_product_summary)
        st.session_state.unassigned_stops_date = delivery_jobs.copy()

    day_summary = aggregates.get_day_summary(stop_data)


def process_data_unassigned_jobs():
    stop_data = st.session_state.stop_data.copy()
    day_summary = aggregates.get_day_summary(stop_data).sort_values(
        ["Collection date"], ascending=False
    )
    st.write("Total number of tickets and unassigned tickets for delivery days:")
    st.dataframe(day_summary)
    stop_data = stop_data.loc[stop_data["Completed Date"].isna()]
    day_summary = aggregates.get_day_summary(stop_data)
    stop_data = aggregates.combine_orders(stop_data)
    st.write("Total number of unassigend deliveries (Completed Date is NULL)")
    route_product_summary = aggregates.calc_product_summary(stop_data)
    st.session_state.unassigned_stops_date = stop_data
    st.write(route_product_summary)
