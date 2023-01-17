"""
Example taken from https://github.com/reyemb/streamlit-plotly-mapbox-events and updated with example from https://plotly.com/python/scattermapbox/ and https://github.com/andfanilo/social-media-tutorials/blob/master/20220914-crossfiltering/streamlit_app.py.

Allows for table and map select, route based filtering, and changing as single category value.

Run it via the below from the main project:

```
streamlit run examples/plotly_mapbox_aggrid_multi_select_change_update.py
```

This is a comprehensive and last update. See issue [16](https://github.com/WasteLabs/streamlit_bi_comms_plotly_map_component/issues/16) for more details.
"""

import datetime
import logging
from typing import Dict, Set, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
from st_aggrid import AgGrid, DataReturnMode, GridOptionsBuilder, GridUpdateMode
from streamlit_plotly_mapbox_events import plotly_mapbox_events

PLOTLY_HEIGHT = 500
LAT_COL = "latitude"
LON_COL = "longitude"

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

COLUMN_ORDER = [
    "index",
    "route_id",
    "peak_hour",
    "car_hours",
    "latitude",
    "longitude",
    "selected",
    "lon-lat__id",
]

COLUMN_ORDER2 = [
    "index",
    "route_id",
    "stop_id",
    "vehicle_profile",
    "arrival_time",
    "departure_time",
    "latitude",
    "longitude",
    "selected",
    "stop_sequence",
    "lon-lat__id",
]


@st.experimental_singleton
def load_transform_data():
    """Load data and do some basic transformation. The `st.experimental_singleton`
    decorator prevents the data from being continously reloaded.
    """
    data = px.data.carshare()
    data = data.rename(
        columns={"centroid_lat": "latitude", "centroid_lon": "longitude"}
    )
    data = data.assign(
        **{
            "lon-lat__id": lambda data: data[LON_COL].astype(str)
            + "-"
            + data[LAT_COL].astype(str)
        },
        route_id="R" + data["peak_hour"].astype(str).str.zfill(2),
        index=data.index,
        selected=False,
    ).sort_values(["route_id"])[COLUMN_ORDER]
    st.session_state.data = data.copy()


@st.experimental_singleton
def load_transform_data2():
    """Load data and do some basic transformation. The `st.experimental_singleton`
    decorator prevents the data from being continously reloaded.
    """
    logging.info("logging::::data being loaded with chaching")
    data = st.session_state.data_07_reporting["assigned_stops"]
    data = data.assign(
        **{
            "lon-lat__id": lambda data: data["longitude"].astype(str)
            + "-"
            + data["latitude"].astype(str)
        },
        route=data["route_id"],
        index=np.arange(0, data.shape[0]),
        selected=False,
    ).sort_values(["route_id", "stop_sequence"])[COLUMN_ORDER2]
    st.session_state.data = data.copy()
    logging.info("logging::::data being loaded with chaching completed")
    return data


def load_transform_data_full2():
    """Load data and do some basic transformation. The `st.experimental_singleton`
    decorator prevents the data from being continously reloaded.
    """
    logging.info("logging::::data being loaded without chaching")
    data = st.session_state.data_07_reporting["assigned_stops"]
    data = data.assign(
        **{
            "lon-lat__id": lambda data: data["longitude"].astype(str)
            + "-"
            + data["latitude"].astype(str)
        },
        route=data["route_id"],
        index=np.arange(0, data.shape[0]),
        selected=False,
    ).sort_values(["route_id", "stop_sequence"])[COLUMN_ORDER2]
    st.session_state.data = data.copy()
    logging.info("logging::::data being loaded without chaching completed")
    return data


def load_transform_data_full():
    """Load data and do some basic transformation. The `st.experimental_singleton`
    decorator prevents the data from being continously reloaded.
    """
    data = px.data.carshare()
    data = data.assign(
        **{
            "lon-lat__id": lambda data: data[LON_COL].astype(str)
            + "-"
            + data[LAT_COL].astype(str)
        },
        route="R" + data["peak_hour"].astype(str).str.zfill(2),
        index=data.index,
        selected=False,
    ).sort_values(["route"])[COLUMN_ORDER]
    st.session_state.data = data.copy()


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


def return_filtered_route_id_data():
    if st.session_state.route_filters:
        filtered = st.session_state.data.loc[
            st.session_state.data["route_id"].isin(st.session_state.route_filters)
        ]
    else:
        filtered = st.session_state.data
    return filtered


def reset_state_callback():
    """Resets all filters and increments counter in Streamlit Session State"""
    st.session_state.counter += 1
    for query in LAT_LON_QUERIES:
        st.session_state[query] = set()
    # st.session_state.map_move_query = set()
    # st.session_state.map_layout = {}
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
            st.session_state.data["lon-lat__id"].isin(selected_ids),
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


def build_map() -> go.Figure:
    """Build a scatter plot on map of selected and normal elements."""

    def return_map_layout_params(df: pd.DataFrame) -> tuple[dict, int]:
        """check if the map layout has been changed, and adjust accordingly"""
        if st.session_state.map_layout:
            logging.info("logging::::zoom level already present")
            center = st.session_state.map_layout["center"]
            zoom = st.session_state.map_layout["zoom"]
        else:
            logging.info("logging::::zoom not present")
            center = {"lat": df[LAT_COL].median(), "lon": df[LON_COL].median()}
            zoom = MAP_ZOOM
        return center, zoom

    def generate_main_scatter_plot(
        df: pd.DataFrame, center: dict, zoom: int
    ) -> go.Figure:
        """Generate main scatter plot"""
        logging.info("logging::::generating scatter plot")
        fig = px.scatter_mapbox(
            df.assign(stop_sequence_txt=df["stop_sequence"].astype(str)),
            lat=LAT_COL,
            lon=LON_COL,
            color="route_id",
            color_discrete_sequence=px.colors.qualitative.Plotly,
            hover_name="index",
            hover_data={
                "route_id": True,
                "stop_id": True,
                "stop_sequence_txt": False,
                "stop_sequence": True,
                "selected": False,
                "latitude": False,
                "longitude": False,
                "lon-lat__id": False,
            },
            # size=17,  # "car_hours",
            text="stop_sequence_txt",
            size_max=20,
            zoom=zoom,
            center=center,
        )
        fig.update_traces(marker={"size": 20})
        return fig

    def add_selected_data_trace(df: pd.DataFrame, fig: go.Figure) -> None:
        """Adds selected data as red dots on top of existing figure"""
        logging.info("logging::::adding selection traces")
        selected_data = df.loc[df["selected"]]
        fig.add_trace(
            go.Scattermapbox(
                lat=selected_data[LAT_COL],
                lon=selected_data[LON_COL],
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=10, color="rgb(242, 0, 0)", opacity=1
                ),
                hoverinfo="none",
                name="Selected",
            )
        )

    def update_layout(fig: go.Figure) -> None:
        """Some basic layout updates."""
        logging.info("logging::::updating map config")
        fig.update_layout(
            mapbox=dict(
                accesstoken=st.secrets["map_box_access_token"],
                style="dark",
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=PLOTLY_HEIGHT,
        )

    logging.info("logging::::generating map layout")
    center, zoom = return_map_layout_params(return_filtered_route_id_data())
    fig = generate_main_scatter_plot(return_filtered_route_id_data(), center, zoom)
    add_selected_data_trace(return_filtered_route_id_data(), fig)
    # add_text(return_filtered_route_id_data(), fig)
    update_layout(fig)
    logging.info("logging::::map layout completed")
    return fig


def render_plotly_map_ui() -> None:
    """Renders all Plotly figures.

    Returns a Dict of filter to set of row identifiers to keep, built from the
    click/select events from Plotly figures.

    The return will be then stored into Streamlit Session State next.
    """

    def return_query_selections(map_selected: tuple) -> None:
        """Unpack events from plotly mapbox events"""
        logging.info("logging::::unpack map query events")
        i = 0
        for query in LAT_LON_QUERIES:  # search for point selections on map
            if LAT_LON_QUERIES_ACTIVE[query] is True:
                st.session_state.current_query[query] = {
                    f"{x['lon']}-{x['lat']}" for x in map_selected[i]
                }
                i += 1
            else:
                st.session_state.current_query[query] = set()

        if map_selected[-1]:  # there was a layout update
            logging.info("logging::::unpack map layout change query")
            st.session_state.map_layout["center"] = map_selected[-1]["raw"][
                "mapbox.center"
            ]
            st.session_state.map_layout["zoom"] = map_selected[-1]["zoom"]
            st.session_state.current_query["map_move_query"] = {
                map_selected[-1]["raw"]["mapbox.center"]["lat"],
                map_selected[-1]["raw"]["mapbox.center"]["lon"],
                map_selected[-1]["zoom"],
            }
        else:
            st.session_state.current_query["map_move_query"] = set()
        logging.info("logging::::unpack map query events completed")

    logging.info("logging::::start plotly map render")
    fig = build_map()
    # map_selected event is not being run, guess because there hasn't been a change on the physical map...
    logging.info("logging::::monitor mapbox events")
    map_selected = plotly_mapbox_events(
        fig,
        click_event=LAT_LON_QUERIES_ACTIVE["lat_lon_click_query"],
        select_event=LAT_LON_QUERIES_ACTIVE["lat_lon_select_query"],
        hover_event=LAT_LON_QUERIES_ACTIVE["lat_lon_hover_query"],
        relayout_event=True,
        key=f"lat_lon_query{st.session_state.counter}",
        override_height=PLOTLY_HEIGHT + st.session_state.counter,
        override_width="%100",
    )
    logging.info("logging::::map monitoring complete")
    return_query_selections(map_selected)


def selection_dataframe() -> None:
    logging.info(f"logging::::selecting dataframe")
    data = return_filtered_route_id_data().copy()
    data = data.assign(temp_index=np.arange(data.shape[0]))

    pre_selected_rows = data.loc[data["selected"]]["temp_index"].tolist()

    gb = GridOptionsBuilder.from_dataframe(data)
    gb.configure_pagination(
        paginationAutoPageSize=False, paginationPageSize=data.shape[0]
    )  # Add pagination
    gb.configure_column("index", headerCheckboxSelection=True)
    gb.configure_side_bar()  # Add a sidebar
    gb.configure_selection(
        "multiple",
        use_checkbox=True,
        groupSelectsChildren="Group checkbox select children",
        pre_selected_rows=pre_selected_rows,
    )  # Enable multi-row selection
    gridOptions = gb.build()

    grid_response = AgGrid(
        data,
        gridOptions=gridOptions,
        data_return_mode="AS_INPUT",
        update_mode="MANUAL",
        columns_auto_size_mode="FIT_CONTENTS",
        fit_columns_on_grid_load=False,
        theme="streamlit",  # Add theme color to the table
        enable_enterprise_modules=False,
        height=PLOTLY_HEIGHT,
        width="100%",
        reload_data=False,
    )
    selected = grid_response["selected_rows"]
    selected_df = pd.DataFrame(selected)
    if selected_df.shape[0] > 0:
        logging.info(f"logging::::data selected for update")
        selected_index = set(selected_df["index"].tolist())
    else:
        logging.info(f"logging::::no data selected for update")
        selected_index = set()
    st.session_state.current_query["aggrid_select"] = selected_index


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


def activate_side_bar():
    routes = st.session_state.data["route_id"].unique()
    with st.sidebar:
        st.button(key="button0", label="CLEAR SELECTION", on_click=reset_state_callback)
        st.session_state.route_filters = st.multiselect("Show routes", routes, routes)
        st.markdown("**Update route assignments**")
        new_route_id = st.selectbox("Change selected stops to route", routes)
        cap_button = st.button(
            key="button1",
            label=f"Confirm change",
        )
        if cap_button:
            update_selected_points(new_route_id)


def update_selected_points(new_route_id):
    if len(st.session_state.selected_data) > 0:
        st.session_state.data.loc[
            st.session_state.data["selected"], "route_id"
        ] = new_route_id
        st.experimental_rerun()
    else:
        st.warning(f"No points were selected...")


def return_selection_summary():
    df = st.session_state.selected_data
    df_sum = (
        df.groupby(["route_id"])
        .agg(
            n_selected=("route_id", "count"),
            # average_car_hours=("car_hours", "mean"),
            # peak_hours=("peak_hour", "unique"),
        )
        .reset_index()
    )
    if df_sum.shape[0] > 0:
        total_row = (
            df_sum.assign(temp_id=1)
            .groupby("temp_id")
            .agg(route=("route_id", "count"), n_selected=("n_selected", "sum"))
        )
        # .assign(
        #     average_car_hours=df["car_hours"].mean(),
        #     peak_hours=df["peak_hour"].nunique(),
        # )
        total_row.index = ["Total/average"]
        df_sum = pd.concat([df_sum, total_row])
    return df_sum


def main():
    if "data" not in st.session_state:
        logging.info(
            "logging::::session data not yet loaded, initialising state and load data"
        )
        initialize_state()
        load_transform_data_full2()
    elif st.session_state.data is None:
        load_transform_data_full2()
    else:
        load_transform_data2()
    activate_side_bar()
    c1, c2 = st.columns(2)
    query_data_map()
    with c1:
        render_plotly_map_ui()
        st.write("Selection summary:")
        st.write(return_selection_summary())
    with c2:
        selection_dataframe()
        st.write("Selected stops:")
        st.write(st.session_state.selected_data)
    update_state()
