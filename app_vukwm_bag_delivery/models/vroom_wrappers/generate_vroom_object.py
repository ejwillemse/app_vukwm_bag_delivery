import numpy as np
import pandas as pd
import vroom
from vroom.input import input

problem_instance = input.Input()


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


def add_stops(vroom_object, stops_df):
    stops_df = stops_df.copy()
    stops_df = add_midnight_seconds_time_windows(stops_df)
    stops_df["stop_id"] = stops_df["stop_id"].astype(str)
    add_stop_to_vroom(vroom_object, stops_df)
    return vroom_object
