import streamlit as st
import app_vukwm_bag_delivery.aggregates as aggregates


def stop_data_summary():
    if "stop_data" in st.session_state:
        st.subheader("Select routing date")
        with st.expander("Instructions"):
            st.markdown(
                """
            Step 1: Upload a bag-delivery excel file.\n
            Step 2: The application will then geocode missing latitude and longitude coordinates using google-maps and show the results.\n
            Step 3: Choose a delivery day to generate routes for, taking into acount that stops already have to be assigned to vehicles.\n
            Step 4: Select one or more vehicles to generate routes for. We recommend choosing all assigned vehicles.\n
            Step 5: Click on the generate route button, and job sequences for each vehicle will be generated.\n
            Step 6: Download the results as an Excel file.
            """
            )
        stop_data = st.session_state.stop_data.copy()
        stop_data = aggregates.date_to_string(stop_data)
        stop_data = aggregates.get_area_num(stop_data)
        day_summary = aggregates.get_day_summary(stop_data)
        st.write("Total number of stops and unassigned stops for delivery days:")
        st.dataframe(day_summary)

        if day_summary is not None:
            unique_dates = day_summary["Collection date"].unique()
            if unique_dates.shape[0] > 0:
                delivery_date = st.selectbox(
                    "Select a delivery date",
                    unique_dates,
                )
            else:
                delivery_date = None
            delivery_jobs = stop_data.loc[stop_data["collection_date"] == delivery_date]
            route_product_summary = aggregates.calc_product_summary(delivery_jobs)
            st.write(route_product_summary)
            st.session_state.delivery_jobs = delivery_jobs.copy()
