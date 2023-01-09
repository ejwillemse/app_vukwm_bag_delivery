"""
Decode vroom solution
"""
import numpy as np
import pandas as pd
import vroom.job


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
