"""
Decode vroom solution
"""
import numpy as np
import pandas as pd
from shapely import wkt

import app_vukwm_bag_delivery.models.osrm_wrappers.osrm_get_routes as osrm_get_routes

# REQUIRED FUNCTIONS
MAPPING = {
    "route_id": "route_id",
    "vehicle_profile": "profile",
    "arrival_time": "arrival_time",
    "service_start_time": "service_start_time",
    "departure_time": "departure_time",
    "waiting_duration__seconds": "waiting_duration_seconds",
    "travel_duration_to_stop__seconds": "travel_duration_to_stop_seconds",
    "travel_distance_to_stop__meters": "travel_distance_to_stop_meters",
    "service_duration__seconds": "service_duration_seconds",
    "wait_time__seconds": "wait_time",
    "activity_type": "activity_type",
    "demand": "demand",
    "skills": "skills",
    "latitude": "latitude",
    "longitude": "longitude",
    "travel_path_to_stop": "travel_path_to_stop",
    "road_longitude": "road_longitude",
    "road_latitude": "road_latitude",
    "road_snap_distance__meters": "road_snap_distance_meters",
    "service_issues": "service_issues",
}


class DecodeVroomSolution:
    def __init__(self, matrix_df, route_df, stop_df, solution, matrix):
        self.matrix_df = matrix_df
        self.unassigned_route_df = route_df
        self.stop_df = stop_df
        self.solution = solution
        self.matrix = matrix
        self.stops_unassigned_df = pd.DataFrame()
        self.routes_unused_df = pd.DataFrame()
        self.routes_extended_df = pd.DataFrame()
        self.travel_leg_info = pd.DataFrame()
        self.stop_sequence_info = pd.DataFrame()
        self.route_summary = pd.DataFrame()

    def extract_unassigned(self):
        unassigned_stops_location_index = [
            stops._location._index() for stops in self.solution.unassigned
        ]

        unassigned_ids = self.matrix_df.loc[
            self.matrix_df["matrix_index"].isin(unassigned_stops_location_index)
        ]["stop_id"].values
        self.stops_unassigned_df = self.stop_df.loc[
            self.stop_df["stop_id"].isin(unassigned_ids)
        ].copy()

    def add_times(self, df):
        start_time = "00:00:00"
        df["arrival_time"] = pd.to_datetime(start_time) + pd.to_timedelta(
            df["arrival"], unit="s"
        )
        df["service_start_time"] = df["arrival_time"] + pd.to_timedelta(
            df["waiting_time"], unit="s"
        )
        df["departure_time"] = df["service_start_time"] + pd.to_timedelta(
            df["service"], unit="s"
        )
        for time in ["arrival_time", "service_start_time", "departure_time"]:
            df[time] = df[time].dt.strftime("%H:%M:%S")
        return df

    def complete_route_df(self):
        unassigned_route = self.unassigned_route_df.copy()
        unassigned_route["vehicle_id"] = np.arange(0, unassigned_route.shape[0])
        route_df = self.solution.routes.copy()
        route_df = route_df.merge(
            self.matrix_df,
            left_on="location_index",
            right_on="matrix_index",
            how="left",
        ).merge(
            unassigned_route[["vehicle_id", "route_id", "profile"]],
            how="left",
        )
        route_df["visit_sequence"] = route_df.groupby("vehicle_id").cumcount()
        route_df = self.add_times(route_df)
        self.routes_extended_df = route_df

    def extract_unused_routes(self):
        routes_unused_df = self.unassigned_route_df.loc[
            ~self.unassigned_route_df["route_id"].isin(
                self.routes_extended_df["route_id"].values
            )
        ].copy()
        self.routes_unused_df = routes_unused_df

    def get_route_kpis(self):
        route_ids = self.routes_extended_df["route_id"].unique()
        routes_kpis = []
        for route_id in route_ids:
            stops = self.routes_extended_df.loc[
                self.routes_extended_df["route_id"] == route_id
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

            stops["travel_time"] = travel_times
            stops["travel_distance"] = travel_distances
            routes_kpis.append(stops)
        routes_kpis = pd.concat(routes_kpis)
        routes_kpis["travel_speed"] = (
            routes_kpis["travel_distance"] / routes_kpis["travel_time"] * 3.6
        ).fillna(0)
        return routes_kpis

    def get_geo_info(self, port_mapping):
        travel_path_info = osrm_get_routes.return_route_osrm_info(
            self.routes_extended_df, port_mapping
        )
        self.travel_leg_info = travel_path_info["travel_leg_info"]
        self.stop_sequence_info = travel_path_info["stop_sequence_info"]
        self.route_summary = travel_path_info["route_summary"]

    def add_travel_leg(self):
        stop_info = self.routes_extended_df.copy()
        travel_leg = self.travel_leg_info.copy()
        travel_leg["geometry"] = travel_leg["geometry"].apply(wkt.dumps)
        travel_leg["visit_sequence"] = travel_leg["travel_sequence"] + 1
        stop_info = stop_info.merge(
            travel_leg[["route_id", "visit_sequence", "geometry"]], how="left"
        )
        self.routes_extended_df = stop_info
