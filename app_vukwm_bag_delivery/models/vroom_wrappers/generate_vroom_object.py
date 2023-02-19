import logging

import numpy as np
import pandas as pd
import streamlit as st
import vroom
from vroom.input import input

problem_instance = input.Input()

PICKUP_DEFAULT = 1800  # 15min


def add_matrix_profiles(vroom_model, matrix):
    for profile in matrix:
        vroom_model.set_durations_matrix(
            profile=profile, matrix_input=matrix[profile]["time_matrix"]
        )
    return vroom_model


def add_midnight_seconds_time_windows(df):
    time_start = pd.to_datetime(df["time_window_start"])
    time_end = pd.to_datetime(df["time_window_end"])
    df = df.assign(
        time_window_start_seconds=(
            (time_start - time_start.dt.normalize()) / pd.Timedelta("1 second")
        ).astype(int),
        time_window_end_seconds=(
            (time_end - time_end.dt.normalize()) / pd.Timedelta("1 second")
        ).astype(int),
    )
    return df


def add_vehicle_to_vroom(vroom_object, route_df):
    route_df["capacity"] = route_df["capacity"].astype(int)
    for i, route in route_df.iterrows():
        if pd.isna(route["skills"]):
            skills = None
        else:
            skills = route["skills"].split(",")
            skills = {int(x) for x in skills}
        vroom_object.add_vehicle(
            [
                vroom.vehicle.Vehicle(
                    route["route_index"],
                    start=route["location_index"],
                    end=route["location_index"],
                    description=route["route_id"],
                    capacity=[route["capacity"] * 1000],
                    profile=route["profile"],
                    skills=skills,
                    time_window=vroom.time_window.TimeWindow(
                        route["time_window_start_seconds"],
                        route["time_window_end_seconds"],
                    ),
                )
            ]
        )
    return vroom_object


def add_vehicles(vroom_object, route_df):
    route_df = add_midnight_seconds_time_windows(route_df)
    vroom_object = add_vehicle_to_vroom(vroom_object, route_df)
    return vroom_object


def add_stop_to_vroom(vroom_object, stop_df):
    for i, stop in stop_df.iterrows():
        if pd.isna(stop["skills"]):
            skill = None
        else:
            skill = set([int(stop["skills"])])
        vroom_object.add_job(
            [
                vroom.job.Job(
                    stop["location_index"],
                    location=stop["location_index"],
                    skills=skill,
                    delivery=[round(stop["demand"] * 1000)],
                    service=stop["service_duration__seconds"],
                    time_windows=[
                        vroom.time_window.TimeWindow(
                            stop["time_window_start_seconds"],
                            stop["time_window_end_seconds"],
                        )  # note that a stop can have multiple time-windows when it has a schedule, for example, between 09:00 and 10:00 or between 12:00 and 15:00
                    ],
                )
            ]
        )
    return vroom_object


def generate_pickup_shipment(pickup_stop_df):
    if pickup_stop_df.shape[0] > 1:
        logging.warning("Shipments can only involve one pickup stop, not multiple.")
    stop = pickup_stop_df.iloc[0]
    pickup_stop = {
        "location": stop["location_index"],
        "setup": PICKUP_DEFAULT,
        "service": 0,
        "time_windows": [
            vroom.time_window.TimeWindow(
                int(stop["time_window_start_seconds"]),
                int(stop["time_window_end_seconds"]),
            )
        ],
    }
    return pickup_stop


def generate_delivery_shipment(stop):
    delivery_stop = {
        "id": stop["location_index"],
        "location": stop["location_index"],
        "service": stop["service_duration__seconds"],
        "time_windows": [
            vroom.time_window.TimeWindow(
                int(stop["time_window_start_seconds"]),
                int(stop["time_window_end_seconds"]),
            )
        ],
    }
    return delivery_stop


def add_bicycle_shipment_to_vroom(vroom_object, deliver_stop_df, pickup_stops_df):
    """Assume that all these stops have to be picked-up from the same bicycle location."""
    master_pickup_stop = generate_pickup_shipment(pickup_stops_df)
    for _, stop in deliver_stop_df.iterrows():
        if pd.isna(stop["skills"]):
            skill = None
        else:
            skill = set([int(stop["skills"])])
        pickup_stop = vroom.ShipmentStep(
            **{**master_pickup_stop, **{"id": 10000 + stop["location_index"]}}
        )
        deliver_stop = vroom.ShipmentStep(**generate_delivery_shipment(stop))
        vroom_object.add_job(
            [
                vroom.job.Shipment(
                    pickup=pickup_stop,
                    delivery=deliver_stop,
                    skills=skill,
                    amount=[stop["demand"] * 1000],
                )
            ]
        )
    return vroom_object


def filter_bicycles(stops_df, route_df):
    bicycle_route_df = route_df[route_df["profile"] == "bicycle"].copy()
    if bicycle_route_df.shape[0] > 1:
        logging.warning(
            "Multiple bicycle routes are not supported, only the first one will be used."
        )
    skills = [float(x) for x in bicycle_route_df.iloc[0]["skills"].split(",")]
    stops_bicycle_df = stops_df[stops_df["skills"].isin(skills)].copy()
    stops_bicycle_df = stops_bicycle_df.assign(
        service_duration__seconds=bicycle_route_df.iloc[0][
            "service_duration_default__seconds"
        ]
    )
    stops_normal = stops_df[
        ~stops_df["stop_id"].isin(stops_bicycle_df["stop_id"].values)
    ].copy()
    return stops_bicycle_df, stops_normal, bicycle_route_df


def add_bicycle_stops(vroom_object, stops_df, route_df):
    stops_df = stops_df.copy()
    route_df = route_df.copy()
    stops_df = add_midnight_seconds_time_windows(stops_df)
    route_df = add_midnight_seconds_time_windows(route_df)
    stops_df["stop_id"] = stops_df["stop_id"].astype(str)
    add_bicycle_shipment_to_vroom(vroom_object, stops_df, route_df)
    return vroom_object


def add_normal_stops(vroom_object, stops_df):
    stops_df = stops_df.copy()
    stops_df = add_midnight_seconds_time_windows(stops_df)
    stops_df["stop_id"] = stops_df["stop_id"].astype(str)
    add_stop_to_vroom(vroom_object, stops_df)


def add_stops(vroom_object, stops_df, route_df, seperate_bicycle_stops=True):
    if seperate_bicycle_stops is True:
        stops_bicycle, stops_normal, route_bicyle_df = filter_bicycles(
            stops_df, route_df
        )
    else:
        stops_bicycle = pd.DataFrame()
        route_bicyle_df = pd.DataFrame()
        stops_normal = stops_df.copy()
    if stops_normal.shape[0] > 0:
        logging.info("Adding bicycle stops")
        add_normal_stops(vroom_object, stops_normal)
    if route_bicyle_df.shape[0] > 0 and stops_bicycle.shape[0] > 0:
        logging.info("Adding bicycle shipments")
        add_bicycle_stops(vroom_object, stops_bicycle, route_bicyle_df)
    return vroom_object
