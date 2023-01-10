"""
Convert input data into waste labs data schema
"""
from typing import Tuple

import numpy as np
import pandas as pd

FILTER_COLUMNS = "Ticket No"
AGGREGATION_IDs = ["stop_id"]

UNASSIGNED_STOPS_COLUMN_MAPPING = [
    {"new_column": "stop_id", "old_column": "Site Bk"},
    {"new_column": "latitude", "old_column": "Site Latitude"},
    {"new_column": "longitude", "old_column": "Site Longitude"},
    {"new_column": "demand", "old_column": "Quantity", "default": 0},
    {"new_column": "skills", "old_column": "transport_area_number", "default": np.nan},
    {
        "new_column": "activity_type",
        "old_column": "activity_type",
        "default": "DELIVERY",
    },
    {
        "new_column": "duration",
        "old_column": "service_duration__seconds",
        "default": 5 * 60,
    },
    {
        "new_column": "time_window_start",
        "old_column": "time_window_start",
        "default": "09:00:00",
    },
    {
        "new_column": "time_window_end",
        "old_column": "time_window_end",
        "default": "16:00:00",
    },
]


def combine_product_name_quantity(df):
    """We combine all orders assigned to a site into one row, with key info concatinated with `';'`."""
    duration = df["duration"].max()
    demand = df["demand"].sum()
    df = df.iloc[:1]  # TODO: this stores key info, but also assigns the same date info
    df["demand"] = demand
    df["duration"] = duration
    return df


def combine_orders(df):
    orders_grouped = (
        df.groupby(AGGREGATION_IDs)
        .apply(combine_product_name_quantity)
        .reset_index(drop=True)
    )
    return orders_grouped


def unassigned_jobs_convert(df, drop_columns=True):
    columns = df.columns
    new_columns = []
    for column_mapping in UNASSIGNED_STOPS_COLUMN_MAPPING:
        if column_mapping["old_column"] not in columns:
            df[column_mapping["new_column"]] = column_mapping["default"]
        else:
            df[column_mapping["new_column"]] = df[column_mapping["old_column"]]
        new_columns.append(column_mapping["new_column"])
    if drop_columns:
        df = df[new_columns]
    return df


def remove_unselected_stops(df, df_remove):
    df = df.loc[~df[FILTER_COLUMNS].isin(df_remove[FILTER_COLUMNS].values)].copy()
    return df


def unassigned_stops_convert(df, df_remove=None):
    if df_remove is not None and df_remove.shape[0] > 0:
        df = remove_unselected_stops(df, df_remove)
    df = unassigned_jobs_convert(df)
    df = df.assign(stop_id=df["stop_id"].astype(str))
    df = combine_orders(df)
    return df


def add_skills(stops, routes):
    skills = routes["skills"].dropna()
    stops.loc[~stops["skills"].isin(skills), "skills"] = np.nan
    return stops


def create_locations(
    unassigned_stops: pd.DataFrame, unassigned_routes: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create singular location object that include all route stops such as depots"""
    unassigned_stops = unassigned_stops.assign(location_type="JOB")
    route_stops = (
        unassigned_routes[
            [
                "route_id",
                "time_window_start",
                "time_window_end",
                "latitude",
                "longitude",
                "activity_type",
            ]
        ]
        .rename(columns={"route_id": "stop_id"})
        .assign(location_type="INFRASTRUCTURE")
    )
    locations = pd.concat([route_stops, unassigned_stops]).reset_index(drop=True)
    locations = locations.assign(location_index=np.arange(0, locations.shape[0]))
    unassigned_stops = unassigned_stops.merge(
        locations[["stop_id", "location_index"]], how="left", validate="1:1"
    )
    unassigned_routes = unassigned_routes.merge(
        locations[["stop_id", "location_index"]]
    )
    return locations, unassigned_stops, unassigned_routes
