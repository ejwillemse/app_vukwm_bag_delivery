"""
Decode vroom solution
"""
import sys

import numpy as np
import pandas as pd
from shapely import wkt

sys.path.insert(0, ".")

import app_vukwm_bag_delivery.models.osrm_wrappers.osrm_get_routes as osrm_get_routes

VROOM_ROUTES_MAPPING_OLD_TO_NEW = {
    "vehicle_id": "route_index",
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
}
JOB_ACTIVITIES = ["JOB"]

# REQUIRED FUNCTIONS
MAPPING = {
    "route_id": "route_id",
    "vehicle_profile": "profile",
    "stop_id": "stop_id",
    "visit_sequence": "visit_sequence",
    "job_sequence": "job_sequence",
    "arrival_time": "arrival_time",
    "service_start_time": "service_start_time",
    "departure_time": "departure_time",
    "waiting_duration__seconds": "waiting_duration_seconds",
    "travel_duration_to_stop__seconds": "travel_duration_to_stop_seconds",
    "travel_distance_to_stop__meters": "travel_distance_to_stop_meters",
    "service_duration__seconds": "service_duration_seconds",
    "waiting_time__seconds": "waiting_time",
    "activity_type": "activity_type",
    "demand": "demand",
    "skills": "skills",
    "latitude": "latitude",
    "longitude": "longitude",
    "travel_path_to_stop": "travel_path_to_stop",
    "road_longitude": "road_longitude",
    "road_latitude": "road_latitude",
    "road_snap_distance__meters": "road_snap_distance_meters",
    "time_window_start": "time_window_start",
    "time_window_end": "time_window_end",
    "service_issues": "service_issues",
}


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
    location_column_drop=["service_duration__seconds"],
) -> pd.DataFrame:
    assigned_stops = assigned_stops.merge(
        locations.drop(columns=location_column_drop), how="left", validate="m:1"
    )
    return assigned_stops


def add_route_info(
    assigned_stops: pd.DataFrame, unassigned_routes: pd.DataFrame
) -> pd.DataFrame:
    """Add minimum route info (profile and capacity) for further processing"""
    unassigned_routes = unassigned_routes.assign(
        route_index=np.arange(unassigned_routes.shape[0])
    )
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
    assigned_stops = convert_solution_routes(solution_routes)
    assigned_stops = calc_times(assigned_stops)
    assigned_stops = add_location_info(assigned_stops, locations)
    assigned_stops = add_route_info(assigned_stops, unassigned_routes)
    assigned_stops = add_sequences(assigned_stops)
    return assigned_stops


class DecodeVroomSolution:
    def __init__(
        self, solution_routes, locations, unassigned_routes, unassigned_stops, matrix
    ):
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

    def format_solution_routes(self):
        self.assigned_stops = format_vroom_solution_routes(
            self.solution.routes,
            # self.unassigned_routes,
            # self.matrix_data,
            # self.unassigned_stops,
        )

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

    # stop_sequence_info_test = pd.read_csv(
    #     "data/test/stop_sequence_info.csv", dtype={"stop_id": str}
    # )
    # travel_leg = gpd.read_file("data/test/travel_leg_info.geojson")

    # assigned_stops = convert_solution_routes(solution_routes_test)
    # assigned_stops = calc_times(assigned_stops)
    # assigned_stops = add_location_info(assigned_stops, locations_test)
    # assigned_stops = add_route_info(assigned_stops, unassigned_routes_test)
    # assigned_stops = add_sequences(assigned_stops)
    routes_test = format_vroom_solution_routes(
        solution_routes_test, locations_test, unassigned_routes_test
    )
    pass
