"""
Decode vroom solution
"""
import logging
import sys

import numpy as np
import pandas as pd
import streamlit as st
from shapely import wkt

sys.path.insert(0, ".")

import app_vukwm_bag_delivery.models.osrm_wrappers.osrm_get_routes as osrm_get_routes

VROOM_ROUTES_MAPPING_OLD_TO_NEW = {
    "vehicle_id": "route_index",
    "trip_id": "trip_id",
    "type": "activity_type",
    "location_index": "location_index",
    "arrival": "arrival_time__seconds",
    "service": "service_duration__seconds",
    "waiting_time": "waiting_duration__seconds",
}

TYPE_CONVERSION = {"stop_id": "str"}

VROOM_ACTIVITY_TYPE_MAPPING = {
    "start": "DEPOT_START_END",
    "end": "DEPOT_START_END",
    "job": "DELIVERY",
    "delivery": "DELIVERY",
    "pickup": "PICKUP",
}
JOB_ACTIVITIES = ["JOB"]

# REQUIRED FUNCTIONS
MAPPING = {
    "route_id": "route_id",
    "trip_id": "trip_id",
    "profile": "vehicle_profile",
    "stop_id": "stop_id",
    "stop_sequence": "stop_sequence",
    "job_sequence": "job_sequence",
    "arrival_time": "arrival_time",
    "service_start_time": "service_start_time",
    "departure_time": "departure_time",
    "travel_duration_to_stop__seconds": "travel_duration_to_stop__seconds",
    "travel_distance_to_stop__meters": "travel_distance_to_stop__meters",
    "service_duration__seconds": "service_duration__seconds",
    "waiting_duration__seconds": "waiting_duration__seconds",
    "activity_type": "activity_type",
    "demand": "demand",
    "skills": "skills",
    "latitude": "latitude",
    "longitude": "longitude",
    "travel_path_to_stop": "travel_path_to_stop",
    "road_snap_longitude": "road_longitude",
    "road_snap_latitude": "road_latitude",
    "road_snap_distance__meters": "road_snap_distance__meters",
    "time_window_start": "time_window_start",
    "time_window_end": "time_window_end",
    "service_issue": "service_issue",
    "demand_cum": "demand_cum",
    "travel_distance_cum__meters": "travel_distance_cum__meters",
    "duration_cum__seconds": "duration_cum__seconds",
    "travel_speed__kmh": "travel_speed__kmh",
    "location_type": "location_type",
}


def add_trip_index(solution_routes):
    """Add trip index to solution routes"""
    pickups = solution_routes["activity_type"] == "PICKUP"
    solution_routes = solution_routes.assign(new_trip=pickups)
    solution_routes = solution_routes.assign(
        trip_id=solution_routes.groupby("route_index")["new_trip"].cumsum() + 1
    )
    return solution_routes


def process_pickups(solution_routes):
    pickups = solution_routes["type"] == "pickup"
    solution_routes = solution_routes.assign(
        service=solution_routes["service"] + solution_routes["setup"]
    )
    # drop pickup stops without setup costs
    solution_routes = solution_routes[(solution_routes["setup"] > 0) | (~pickups)]
    # add stop id (which will be the vehicle id)
    solution_routes = solution_routes.assign(new_trip=pickups)
    solution_routes = solution_routes.assign(
        trip_id=solution_routes.groupby("vehicle_id")["new_trip"].cumsum() + 1
    )
    return solution_routes


def convert_solution_routes(
    solution_routes: pd.DataFrame,
    mapping: dict = VROOM_ROUTES_MAPPING_OLD_TO_NEW,
    activity_mapping: dict = VROOM_ACTIVITY_TYPE_MAPPING,
) -> pd.DataFrame:
    assigned_stops = solution_routes.rename(columns=mapping)[mapping.values()]
    assigned_stops = assigned_stops.assign(
        activity_type=assigned_stops["activity_type"].replace(activity_mapping)
    )
    return assigned_stops


def calc_times(
    assigned_stops: pd.DataFrame,
    time_horizon_start: str = "00:00:00",
    output_format: str = "%H:%M:%S",
) -> pd.DataFrame:
    """Calc formatted arrival, service start times and departure times."""

    def hms_from_seconds(seconds_series):
        return (
            time_horizon_dt + pd.to_timedelta(seconds_series, unit="s")
        ).dt.strftime(output_format)

    time_horizon_dt = pd.to_datetime(time_horizon_start)
    arrival_time__seconds = assigned_stops["arrival_time__seconds"]
    service_start_time__seconds = (
        arrival_time__seconds + assigned_stops["waiting_duration__seconds"]
    )
    departure_time__seconds = (
        service_start_time__seconds + assigned_stops["service_duration__seconds"]
    )
    assigned_stops = assigned_stops.assign(
        arrival_time=hms_from_seconds(arrival_time__seconds),
        service_start_time=hms_from_seconds(service_start_time__seconds),
        departure_time=hms_from_seconds(departure_time__seconds),
    )
    return assigned_stops


def add_location_info(
    assigned_stops: pd.DataFrame,
    locations: pd.DataFrame,
    location_column_drop=["activity_type", "service_duration__seconds"],
) -> pd.DataFrame:
    assigned_stops = assigned_stops.merge(
        locations.drop(columns=location_column_drop), how="left", validate="m:1"
    )
    return assigned_stops


def add_route_info(
    assigned_stops: pd.DataFrame, unassigned_routes: pd.DataFrame
) -> pd.DataFrame:
    """Add minimum route info (profile and capacity) for further processing"""
    # unassigned_routes = unassigned_routes.assign(
    #     route_index=np.arange(unassigned_routes.shape[0])
    # )
    assigned_stops = assigned_stops.merge(
        unassigned_routes.assign(vehicle_skills=unassigned_routes["skills"])[
            ["route_index", "route_id", "profile", "capacity", "vehicle_skills"]
        ],
        how="left",
        left_on="route_index",
        right_on="route_index",
        validate="m:m",
    )
    return assigned_stops


def add_sequences(assigned_stops: pd.DataFrame, job_activities=None) -> pd.DataFrame:
    """Add stop and job only visit sequences"""

    def cal_route_sequences(df):
        return df.groupby(["route_id"]).cumcount()

    if job_activities is None:
        job_activities = JOB_ACTIVITIES

    assigned_stops = assigned_stops.assign(
        stop_sequence=cal_route_sequences(assigned_stops)
    )
    job_stops = assigned_stops.loc[
        assigned_stops["location_type"].isin(job_activities)
    ].copy()
    job_stops = job_stops.assign(job_sequence=cal_route_sequences(job_stops))
    assigned_stops = assigned_stops.merge(
        job_stops[["route_id", "stop_sequence", "job_sequence"]], how="left"
    )
    return assigned_stops


def format_vroom_solution_routes(
    solution_routes: pd.DataFrame,
    locations: pd.DataFrame,
    unassigned_routes: pd.DataFrame,
) -> pd.DataFrame:
    """Convert solution into correct format"""
    solution_routes = process_pickups(solution_routes)
    assigned_stops = convert_solution_routes(solution_routes)
    assigned_stops = calc_times(assigned_stops)
    assigned_stops = add_location_info(assigned_stops, locations)
    assigned_stops = add_route_info(assigned_stops, unassigned_routes)
    assigned_stops = add_sequences(assigned_stops)
    return assigned_stops


def partial_format_vroom_solution_routes(
    solution_routes: pd.DataFrame,
    locations: pd.DataFrame,
    unassigned_routes: pd.DataFrame,
) -> pd.DataFrame:
    """Convert solution into correct format"""
    assigned_stops = add_trip_index(solution_routes)
    assigned_stops = convert_solution_routes(assigned_stops)
    assigned_stops = calc_times(assigned_stops)
    assigned_stops = add_location_info(assigned_stops, locations)
    assigned_stops = add_route_info(assigned_stops, unassigned_routes)
    assigned_stops = add_sequences(assigned_stops)
    return assigned_stops


class DecodeVroomSolution:
    def __init__(
        self,
        solution_routes,
        locations,
        unassigned_routes,
        unassigned_stops,
        matrix,
        osrm_ports,
    ):
        self.locations = locations
        self.unassigned_routes = unassigned_routes
        self.unassigned_stops = unassigned_stops
        self.solution_routes = solution_routes
        self.matrix = matrix
        self.assigned_stops = pd.DataFrame()
        self.unused_routes = pd.DataFrame()
        self.travel_leg_info = pd.DataFrame()
        self.stop_sequence_info = pd.DataFrame()
        self.route_summary = pd.DataFrame()
        self.unserviced_stops = pd.DataFrame()
        self.osrm_port = osrm_ports

    def format_solution_routes(self):
        self.assigned_stops = format_vroom_solution_routes(
            self.solution_routes, self.locations, self.unassigned_routes
        )

    def extract_unused_routes(self):
        self.unused_routes = self.unassigned_routes.loc[
            ~self.unassigned_routes["route_id"].isin(self.assigned_stops["route_id"])
        ]

    def extract_unserviced_stops(self):
        self.unserviced_stops = self.unassigned_stops.loc[
            ~self.unassigned_stops["stop_id"].isin(self.assigned_stops["stop_id"])
        ]

    def add_matrix_info(self):
        route_ids = self.assigned_stops["route_id"].unique()
        routes_kpis = []
        for route_id in route_ids:
            stops = self.assigned_stops.loc[
                self.assigned_stops["route_id"] == route_id
            ].copy()
            profile = stops["profile"].unique()
            assert len(profile) == 1
            profile = profile[0]
            time_matrix = self.matrix[profile]["time_matrix"]
            distance_matrix = self.matrix[profile]["distance_matrix"]

            location_index = stops["location_index"].values

            travel_times = [
                time_matrix[location_index[i - 1], location_index[i]]
                for i in range(1, location_index.shape[0])
            ]
            travel_times.insert(0, 0)

            travel_distances = [
                distance_matrix[location_index[i - 1], location_index[i]]
                for i in range(1, location_index.shape[0])
            ]
            travel_distances.insert(0, 0)

            stops["travel_duration_to_stop__seconds"] = travel_times
            stops["travel_distance_to_stop__meters"] = travel_distances
            routes_kpis.append(stops)
        routes_kpis = pd.concat(routes_kpis)
        routes_kpis["travel_speed__kmh"] = (
            routes_kpis["travel_distance_to_stop__meters"]
            / routes_kpis["travel_duration_to_stop__seconds"]
            * 3.6
        ).fillna(0)
        self.assigned_stops = routes_kpis

    def get_geo_info(self):
        travel_path_info = osrm_get_routes.return_route_osrm_info(
            self.assigned_stops, self.osrm_port
        )
        self.travel_leg_info = travel_path_info["travel_leg_info"]
        self.stop_sequence_info = travel_path_info["stop_sequence_info"]
        self.route_summary = travel_path_info["route_summary"]

    def add_travel_leg(self):
        stop_info = self.assigned_stops.copy()
        travel_leg = self.travel_leg_info.copy()
        travel_leg = travel_leg.assign(
            travel_path_to_stop=travel_leg["geometry"].apply(wkt.dumps),
            stop_sequence=travel_leg["travel_sequence"] + 1,
        )
        stop_info = stop_info.merge(
            travel_leg[["route_id", "stop_sequence", "travel_path_to_stop"]], how="left"
        )
        self.assigned_stops = stop_info

    def add_road_snap_info(self):
        self.assigned_stops = self.assigned_stops.merge(
            self.stop_sequence_info.drop(columns=["original_index"]).rename(
                columns={
                    "route_sequence": "stop_sequence",
                    "road_snap_distance_m": "road_snap_distance__meters",
                }
            )
        )

    def add_duration_capacity_cumsum(self):
        self.assigned_stops = self.assigned_stops.assign(
            duration_cum=self.assigned_stops[
                [
                    "travel_duration_to_stop__seconds",
                    "waiting_duration__seconds",
                    "service_duration__seconds",
                ]
            ]
            .fillna(0)
            .sum(axis=1)
        )
        self.assigned_stops = self.assigned_stops.assign(
            demand_cum=self.assigned_stops.groupby(["route_id", "trip_id"])[
                "demand"
            ].cumsum(),
            travel_distance_cum__meters=self.assigned_stops.groupby(["route_id"])[
                "travel_distance_to_stop__meters"
            ].cumsum(),
            duration_cum__seconds=self.assigned_stops.groupby(["route_id"])[
                "duration_cum"
            ].cumsum(),
        )

    def assign_service_issues(self):
        early_flag = self.assigned_stops["waiting_duration__seconds"].fillna(0) > 0
        late_flag = pd.to_datetime(
            self.assigned_stops["arrival_time"]
        ) > pd.to_datetime(self.assigned_stops["time_window_end"])
        self.assigned_stops = self.assigned_stops.assign(service_issue="ON-TIME")
        self.assigned_stops.loc[early_flag, "service_issue"] = "EARLY"
        self.assigned_stops.loc[late_flag, "service_issue"] = "LATE"

    def format_assigned_stops(self, ignore_missing_columns=False):
        self.assigned_stops = self.assigned_stops.rename(columns=MAPPING)
        if not ignore_missing_columns:
            self.assigned_stops = self.assigned_stops.rename(columns=MAPPING)[
                MAPPING.values()
            ]
        else:
            values = [x for x in MAPPING.values() if x in self.assigned_stops.columns]
            self.assigned_stops = self.assigned_stops[values]

    def convert_solution(self):
        self.format_solution_routes()
        self.assign_service_issues()
        self.extract_unused_routes()
        self.extract_unserviced_stops()
        self.add_matrix_info()
        self.get_geo_info()
        self.add_travel_leg()
        self.add_road_snap_info()
        self.add_duration_capacity_cumsum()
        self.format_assigned_stops()
        return self.assigned_stops

    def speed_convert_solution(self):
        self.format_solution_routes()
        self.assign_service_issues()
        self.extract_unused_routes()
        self.extract_unserviced_stops()
        self.add_matrix_info()
        self.add_duration_capacity_cumsum()
        self.format_assigned_stops(True)
        return self.assigned_stops

    def extend_solution(self):
        self.assigned_stops = partial_format_vroom_solution_routes(
            self.solution_routes, self.locations, self.unassigned_routes
        )
        self.assign_service_issues()
        self.extract_unused_routes()
        self.extract_unserviced_stops()
        self.add_matrix_info()
        self.get_geo_info()
        self.add_travel_leg()
        self.add_road_snap_info()
        self.add_duration_capacity_cumsum()
        self.format_assigned_stops()
        return self.assigned_stops


if __name__ == "__main__":
    import pickle

    import geopandas as gpd

    unassigned_stops = pd.read_csv(
        "data/local_test/03_Generate_Routes/unassigned_stops.csv",
        dtype={"stop_id": str},
    )
    unassigned_routes_test = pd.read_csv(
        "data/local_test/03_Generate_Routes/unassigned_routes.csv",
        dtype={"route_id": str},
    )
    locations_test = pd.read_csv(
        "data/local_test/03_Generate_Routes/locations.csv", dtype={"stop_id": str}
    )
    solution_routes_test = pd.read_csv(
        "data/local_test/03_Generate_Routes/vroom_routes.csv",
    )

    with open("data/local_test/03_Generate_Routes/matrix.pickle", "br") as f:
        matrix = pickle.load(f)

    decoder = DecodeVroomSolution(
        solution_routes_test,
        locations_test,
        unassigned_routes_test,
        unassigned_stops,
        matrix,
        osrm_ports={
            "bicycle": "http://34.216.224.175:8001",
            "auto": "http://34.216.224.175:8000",
            "default": "http://34.216.224.175:8000",
        },
    )
    assigned_stops = decoder.convert_solution()
    assigned_stops.to_csv(
        "data/local_test/03_Generate_Routes/assigned_stops.csv", index=False
    )
