"""
Example taken from https://github.com/reyemb/streamlit-plotly-mapbox-events and updated with example from https://plotly.com/python/scattermapbox/ and https://github.com/andfanilo/social-media-tutorials/blob/master/20220914-crossfiltering/streamlit_app.py.

Allows for table and map select, route based filtering, and changing as single category value.

Run it via the below from the main project:

```
streamlit run examples/plotly_mapbox_aggrid_multi_select_change_update.py
```

This is a comprehensive and last update. See issue [16](https://github.com/WasteLabs/streamlit_bi_comms_plotly_map_component/issues/16) for more details.
"""

import logging

import numpy as np
import pandas as pd
import streamlit as st

from app_vukwm_bag_delivery.update_routes.controls import activate_side_bar
from app_vukwm_bag_delivery.update_routes.interactive_map import render_plotly_map_ui
from app_vukwm_bag_delivery.update_routes.select_dataframe import selection_dataframe

PLOTLY_HEIGHT = 500
LAT_COL = "latitude"
LON_COL = "longitude"
ROUTE_ID = "Vehicle Id"
LAT_LON_ID = "_lon-lat__id"
LAT_LON_QUERIES = [
    "lat_lon_click_query",
    "lat_lon_select_query",
    "lat_lon_hover_query",
]
LAT_LON_QUERIES_ACTIVE = {
    "lat_lon_click_query": False,
    "lat_lon_select_query": True,
    "lat_lon_hover_query": False,
}

MAP_ZOOM = 11


def create_lat_lon_id(data):
    return data.assign(
        **{
            LAT_LON_ID: lambda data: data[LON_COL].astype(str)
            + "-"
            + data[LAT_COL].astype(str)
        },
        index=np.arange(0, data.shape[0]),
        selected=False,
    )


@st.experimental_singleton
def load_transform_data():
    """Load data and do some basic transformation. The `st.experimental_singleton`
    decorator prevents the data from being continously reloaded.
    """
    logging.info("logging::::data being loaded with chaching")
    data = st.session_state.edit_routes["assigned_stops"]
    data = create_lat_lon_id(data)
    st.session_state.data = data.copy()
    logging.info("logging::::data being loaded with chaching completed")
    return data


def load_transform_data_full():
    """Load data and do some basic transformation. The `st.experimental_singleton`
    decorator prevents the data from being continously reloaded.
    """
    logging.info("logging::::data being loaded without chaching")
    data = st.session_state.edit_routes["assigned_stops"]
    data = create_lat_lon_id(data)
    st.session_state.data = data.copy()
    logging.info("logging::::data being loaded without chaching completed")
    return data


def initialize_state(clear_all=False):
    """Initializes all filters, data and counter in Streamlit Session State."""
    logging.info(f"logging::::initialize_state with `clear_all = {clear_all}`")
    for query in LAT_LON_QUERIES:
        if query not in st.session_state or clear_all:
            st.session_state[query] = set()

    if "map_move_query" not in st.session_state or clear_all:
        st.session_state.map_move_query = set()

    if "map_layout" not in st.session_state or clear_all:
        st.session_state.map_layout = {}

    if "counter" not in st.session_state:
        st.session_state.counter = 0

    if "aggrid_select" not in st.session_state or clear_all:
        st.session_state.aggrid_select = set()

    if "data" not in st.session_state or clear_all:
        st.session_state.data = None

    if "selected_data" not in st.session_state or clear_all:
        st.session_state.selected_data = []

    if "current_query" not in st.session_state or clear_all:
        st.session_state.current_query = {}

    # if "aggrid_select" not in st.session_state or clear_all:
    #     st.session_state.current_query = {}

    if "route_filters" not in st.session_state or clear_all:
        st.session_state.route_filters = []


def reset_state_callback():
    """Resets all filters and increments counter in Streamlit Session State"""
    st.session_state.counter += 1
    for query in LAT_LON_QUERIES:
        st.session_state[query] = set()
    st.session_state.aggrid_select = set()
    st.session_state.current_query = {}
    st.session_state.data = st.session_state.data.assign(selected=False)


def query_data_map() -> pd.DataFrame:
    """Apply filters in Streamlit Session State to filter the input DataFrame"""
    logging.info(f"logging::::query map data")
    selected_ids = set()
    query_update = False
    for query in LAT_LON_QUERIES:
        if st.session_state[query]:
            logging.info(f"logging::::query update values found in {query}")
            selected_ids.update(st.session_state[query])
            query_update = True

    if query_update:
        logging.info(f"logging::::update selected values found map query to True")
        st.session_state.data.loc[
            st.session_state.data[LAT_LON_ID].isin(selected_ids),
            "selected",
        ] = True

    if st.session_state["aggrid_select"]:
        logging.info(f"logging::::query update values found in aggrid_select")
        logging.info(
            f"logging::::update selected values found in aggrid_select to True"
        )
        selected_index = st.session_state["aggrid_select"]
        st.session_state.data.loc[
            st.session_state.data["index"].isin(selected_index),
            "selected",
        ] = True
    st.session_state.selected_data = st.session_state.data.loc[
        st.session_state.data["selected"]
    ].copy()


def update_state():
    """Stores input dict of filters into Streamlit Session State.

    If one of the input filters is different from previous value in Session State,
    rerun Streamlit to activate the filtering and plot updating with the new info in State.
    """
    logging.info("logging::::checking for status updates")
    rerun = False
    for (
        query
    ) in LAT_LON_QUERIES:  # these should be ignore under special reset conditions
        if st.session_state.current_query[query] - st.session_state[query]:
            st.session_state[query] = st.session_state.current_query[query]
            logging.info(f"logging::::status updated found in {query}")
            rerun = True

    if (
        st.session_state.current_query["map_move_query"]
        - st.session_state["map_move_query"]
    ):
        st.session_state["map_move_query"] = st.session_state.current_query[
            "map_move_query"
        ]
        logging.info(f"logging::::status updated found in map_move_query")
        rerun = True

    if (
        st.session_state.current_query["aggrid_select"]
        - st.session_state["aggrid_select"]
    ):
        st.session_state["aggrid_select"] = st.session_state.current_query[
            "aggrid_select"
        ]
        logging.info(f"logging::::status updated found in aggrid select")
        rerun = True

    if rerun:
        logging.info(f"logging::::rerunning app")
        st.experimental_rerun()
    else:
        logging.info(f"logging::::no query updates found, not rerunning")


def return_selection_summary():
    df = st.session_state.selected_data
    df_sum = (
        df.sort_values([ROUTE_ID, "Transport Area Code"])
        .assign(**{"Transport Area Code": df["Transport Area Code"]})
        .groupby([ROUTE_ID])
        .agg(
            **{
                "#Stops": (ROUTE_ID, "count"),
                "Skills": ("Skills", "unique"),
                "Transport areas": ("Transport Area Code", "unique"),
                "Travel distance (km)": ("Travel distance to stops (km)", "sum"),
                "Travel time (min)": ("Travel duration to stop (minutes)", "sum"),
                "Service time (min)": ("Service duration (minutes)", "sum"),
            },
        )
        .reset_index()
    )
    df_sum = df_sum.assign(
        **{
            "Skills": df_sum["Skills"].apply(
                lambda x: [y for y in x if y is not pd.np.nan]
            ),
            "Transport areas": df_sum["Transport areas"].apply(
                lambda x: [y for y in x if y is not pd.np.nan]
            ),
        }
    )
    if df_sum.shape[0] > 0:
        total_row = (
            df_sum.assign(temp_id=1)
            .groupby("temp_id")
            .agg(
                **{
                    ROUTE_ID: (ROUTE_ID, "count"),
                    "#Stops": ("#Stops", "sum"),
                    "Travel distance (km)": ("Travel distance (km)", "sum"),
                    "Travel time (min)": ("Travel time (min)", "sum"),
                    "Service time (min)": ("Service time (min)", "sum"),
                }
            )
        )
        total_row["Vehicle Id"] = ["Total"]
        df_sum = pd.concat([df_sum, total_row])
    return df_sum


def main():
    if "data" not in st.session_state:
        logging.info(
            "logging::::session data not yet loaded, initialising state and load data"
        )
        initialize_state()
        load_transform_data_full()
    elif st.session_state.data is None:
        load_transform_data_full()
    else:
        load_transform_data()
    activate_side_bar()
    side_by_side = st.checkbox(
        "Side-by-side layout",
        help="Deselect to change the orientation to a top-bottom layout",
        value=False,
    )
    if not side_by_side:
        query_data_map()
        render_plotly_map_ui()
        selection_dataframe()
        st.write("Selection summary:")
        summary = return_selection_summary().T
        summary.columns = summary.iloc[0].values
        summary = summary.iloc[1:]
        st.dataframe(summary, use_container_width=True)

        st.write("Selected stops:")
        st.write(st.session_state.selected_data)
        update_state()
    else:
        c1, c2 = st.columns(2)
        query_data_map()

        with c1:
            render_plotly_map_ui()
            st.write("Selection summary:")
            summary = return_selection_summary().T
            summary.columns = summary.iloc[0].values
            summary = summary.iloc[1:]
            st.dataframe(summary, use_container_width=True)
        with c2:
            selection_dataframe()
            st.write("Selected stops:")
            st.write(st.session_state.selected_data)
    update_state()
