import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

import app_vukwm_bag_delivery.models.pipelines.process_input_data.add_time_window_info as add_time_window_info

OPEN_DEFAULT = "10:00:00"
CLOSE_DEFAULT = "17:00:00"
OPEN_MAX = "15:00:00"

INSPECT_ORDER = [
    "Site Bk",
    "Site Name",
    "Notes",
    "Transport Area Code",
    "Delivery open time",
    "Delivery close time",
    "Typical open time",
    "Typical close time",
    "Unknown open times",
    "Site Address",
]


def add_min_open_time(df):
    df = df.assign(**{"Delivery open time": df["Typical open time"]})
    df.loc[df["Delivery open time"] < "01:00:00", "Delivery open time"] = "01:00:00"
    df = df.assign(
        **{"Delivery open time": df["Delivery open time"].fillna(OPEN_DEFAULT)}
    )
    df.loc[df["Delivery open time"] >= OPEN_MAX, "Delivery open time"] = "16:00:00"
    df = df.assign(
        **{
            "Delivery open time": (
                pd.to_datetime(df["Delivery open time"]) - pd.Timedelta(hours=1)
            ).dt.strftime("%H:%M:%S")
        }
    )
    return df


def add_max_close_time(df):
    df = df.assign(
        **{"Delivery close time": df["Typical close time"].fillna(CLOSE_DEFAULT)}
    )
    return df


def generate_timelines(df):
    hovertemplate1 = (
        "<b>Site Bk: %{customdata[0]}</b><br>"
        + "Site: %{customdata[1]}<br>"
        + "Notes: %{customdata[2]}<br>"
        + "Transport Area Code: %{customdata[3]}<br>"
        + "Delivery open time: %{customdata[4]}<br>"
        + "Delivery close time: %{customdata[5]}<br>"
        + "Typical open time: %{customdata[6]}<br>"
        + "Typical close time: %{customdata[7]}<br>"
        + "Site Address: %{customdata[8]}<br>"
    )

    custom_data = [
        "Site Bk",
        "Site Name",
        "Notes",
        "Transport Area Code",
        "Delivery open time",
        "Delivery close time",
        "Typical open time",
        "Typical close time",
        "Site Address",
    ]
    df = (
        df.assign(
            **{
                "open_time": (
                    datetime.datetime.now().strftime("%Y-%m-%d")
                    + " "
                    + df["Delivery open time"]
                ),
                "close_time": (
                    datetime.datetime.now().strftime("%Y-%m-%d")
                    + " "
                    + df["Delivery close time"]
                ),
            }
        )
        .sort_values(["Site Name"], ascending=False, key=lambda col: col.str.lower())
        .fillna("")
    )
    fig = px.timeline(
        df.sort_values(["Delivery open time", "Delivery close time"]),
        x_start="open_time",
        x_end="close_time",
        y="Site Name",
        height=750,
        custom_data=custom_data,
    )
    _ = fig.update_traces(hovertemplate=hovertemplate1)
    fig.update_xaxes(tickformat="%H:%M")
    fig.update_yaxes(categoryorder="array", categoryarray=df["Site Name"].values)
    return fig


def view_time_window_summary(df_tw):
    time_slot_summary = (
        (
            df_tw.assign(
                **{
                    "Delivery slots": df_tw["Delivery open time"]
                    + " - "
                    + df_tw["Delivery close time"]
                }
            )
            .groupby("Delivery slots")
            .agg(**{"Number of slots": ("Delivery slots", "count")})
        )
        .reset_index()
        .sort_values("Delivery slots")
    )
    return time_slot_summary


def generate_known_unknown(df):
    return {
        "known_open": generate_timelines(df.loc[~df["Unknown open times"]]),
        "unkown_open": generate_timelines(df.loc[df["Unknown open times"]]),
    }


def return_time_window_info():
    unassigned_stops = st.session_state.data_02_intermediate["unassigned_stops"]
    time_windows = st.session_state.data_01_raw["open_time"]
    unassigned_stops_tw = add_time_window_info.merge_time_window_info(
        unassigned_stops, time_windows
    )[
        [
            "Site Bk",
            "Site Name",
            "Notes",
            "Transport Area Code",
            "Typical open time",
            "Typical close time",
            "Site Address",
        ]
    ]
    unassigned_stops_tw = unassigned_stops_tw.assign(
        **{
            "Unknown open times": (unassigned_stops_tw["Typical open time"].isna())
            | (unassigned_stops_tw["Typical close time"].isna())
        }
    )
    unassigned_stops_tw = add_min_open_time(unassigned_stops_tw)
    unassigned_stops_tw = add_max_close_time(unassigned_stops_tw)
    unassigned_stops_tw = unassigned_stops_tw.sort_values(
        ["Notes", "Site Name"], key=lambda col: col.str.lower()
    )[INSPECT_ORDER]
    st.session_state.data_02_intermediate["unassigned_stops_tw"] = unassigned_stops_tw
