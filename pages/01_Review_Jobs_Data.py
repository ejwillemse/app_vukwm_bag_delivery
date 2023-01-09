import streamlit as st
from st_aggrid import AgGrid, DataReturnMode, GridOptionsBuilder, GridUpdateMode

import app_vukwm_bag_delivery.views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.aggregates import combine_orders
from app_vukwm_bag_delivery.presenters.check_password import check_password
from app_vukwm_bag_delivery.views.page_view_01_Review_Jobs_Data import (  # check_previous_steps_completed,
    check_previous_steps_completed,
    set_page_config,
    view_all_stops,
    view_instructions,
    view_product_summary,
    view_stops_map,
)
from app_vukwm_bag_delivery.views.render_unassigned_stops_map import (
    return_order_map_html,
)
from routing_job_selection import process_data_unassigned_jobs

if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line

set_page_config()

side_bar_status = side_bar_progress.view_sidebar()
view_instructions()
check_previous_steps_completed()
view_product_summary()
view_all_stops()
view_stops_map()

# process_data_unassigned_jobs()

# st.header("Inspect job data")

# st.write(st.session_state["data_02_intermediate"]["unassigned_stops"])


# st.write(st.session_state.unassigned_stops_date)

# with st.expander("Filter jobs to be EXCLUDED from routing:"):
#     gb = GridOptionsBuilder.from_dataframe(st.session_state.unassigned_stops_date)
#     gridOptions = gb.build()
#     grid_response = AgGrid(
#         st.session_state.unassigned_stops_date,
#         gridOptions=gridOptions,
#         data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
#         update_mode=GridUpdateMode.GRID_CHANGED,
#         fit_columns_on_grid_load=False,
#         theme="streamlit",  # Add theme color to the table
#         enable_enterprise_modules=False,
#         width="100%",
#         reload_data=True,
#         allow_unsafe_jscode=True,
#     )
