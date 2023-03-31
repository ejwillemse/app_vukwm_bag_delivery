import logging

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
from streamlit_plotly_mapbox_events import plotly_mapbox_events

from app_vukwm_bag_delivery.update_routes.process_assigned_data import (
    return_filtered_route_id_data,
)

MAP_ZOOM = 11
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
        df = df.assign(**{"Vehicle profile": df["Vehicle profile"].astype("string")})
        df = df.loc[df["Activity type"] == "DELIVERY"].sort_values([ROUTE_ID])
        df.loc[df["Service issues"] == "UNSERVICED", "Stop sequence"] = np.nan
        fig = px.scatter_mapbox(
            df.fillna("").assign(
                **{
                    "stop_sequence_txt": df["Stop sequence"]
                    .astype(str)
                    .str[:-2]
                    .replace("n", "x"),
                    " ": df[ROUTE_ID],
                }
            ),
            lat=LAT_COL,
            lon=LON_COL,
            color=" ",
            color_discrete_sequence=px.colors.qualitative.Plotly,
            hover_name=ROUTE_ID,
            hover_data={
                ROUTE_ID: False,
                " ": False,
                "Vehicle profile": True,
                "Skills": True,
                "Site Name": True,
                "Stop sequence": True,
                "Arrival time": True,
                "Departure time": True,
                "Time window start": True,
                "Time window end": True,
                "Transport Area Code": True,
                "stop_sequence_txt": False,
                "latitude": False,
                "longitude": False,
                "Service issues": True,
                LAT_LON_ID: False,
            },
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
            # legend_title=None,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=PLOTLY_HEIGHT,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=0.0,
                xanchor="left",
                x=0.0,
                font=dict(color="white"),
                bgcolor="rgba(0,0,0,0.25)",
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )

    logging.info("logging::::generating map layout")
    center, zoom = return_map_layout_params(return_filtered_route_id_data())
    fig = generate_main_scatter_plot(return_filtered_route_id_data(), center, zoom)
    add_selected_data_trace(return_filtered_route_id_data(), fig)
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
