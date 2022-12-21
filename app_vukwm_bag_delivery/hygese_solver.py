"""
https://github.com/chkwon/PyHygese
"""

import hygese as hgs
import numpy as np
import pandas as pd

from .geo_utils import add_xy_projected_coordinate_point_features
from .orsm_get_table import get_time_dist_matrix


def add_single_depot(df, fleet):
    depot_stop = fleet.iloc[:1][["Depot", "lat", "lon", "Vehicle id"]].rename(
        columns={"Depot": "Site Name"}
    )
    df_routing = pd.concat([depot_stop, df]).reset_index(drop=True)
    return df_routing


def prepare_data(df, fleet, demand_column="Total boxes", capacity_spread=0.1):
    df_routing = add_single_depot(df, fleet)
    df_routing = add_xy_projected_coordinate_point_features(df_routing)
    time_matrix, distance_matrix = get_time_dist_matrix(
        df_routing,
    )
    distance_matrix = distance_matrix / 1000
    n_vehicles = fleet.shape[0]
    total_demand = df_routing[demand_column].sum()

    demand_per_vehicle = int(
        round(total_demand / n_vehicles * (1 + capacity_spread), 0)
    )

    n = df_routing.shape[0]
    data = dict()
    data["x_coordinates"] = ((df_routing["x"] - df_routing["x"].min()) / 1000).values
    data["y_coordinates"] = ((df_routing["y"] - df_routing["y"].min()) / 1000).values
    data["service_times"] = np.zeros(n)
    data["demands"] = df_routing[demand_column].fillna(0).values
    data["depot"] = 0
    data["num_vehicles"] = n_vehicles
    data["vehicle_capacity"] = demand_per_vehicle
    data["distance_matrix"] = distance_matrix
    return data


def solve_vrp(data, time_limit=3):
    ap = hgs.AlgorithmParameters(timeLimit=time_limit)  # seconds
    hgs_solver = hgs.Solver(parameters=ap, verbose=True)
    result = hgs_solver.solve_cvrp(data)
    return result


def decode_solution(df, fleet, results):
    df = df.assign(id=np.arange(0, df.shape[0]) + 1)
    depot_stop = fleet.iloc[:1][["Depot", "lat", "lon", "Vehicle id"]].rename(
        columns={"Depot": "Site Name", "lon": "lon", "lat": "lat"}
    )
    routes = []
    for i, route in enumerate(results.routes):
        route_stops = df.loc[df["id"].isin(route)]

        route_df = pd.DataFrame({"id": route})
        route_df = route_df.merge(route_stops, how="left")
        route_df = pd.concat([depot_stop, route_df, depot_stop])
        route_df = route_df.assign(route_sequence=np.arange(0, route_df.shape[0]))

        vehicle = fleet.iloc[i]
        route_id = vehicle["Vehicle id"]
        route_df["Vehicle id"] = route_id
        route_df["vehicle_type"] = vehicle["Type"]
        routes.append(route_df)
    routes_full = pd.concat(routes).reset_index(drop=True)[
        [
            "Ticket No",
            "Site Name",
            "Vehicle id",
            "vehicle_type",
            "route_sequence",
            "lat",
            "lon",
        ]
    ]
    return routes_full


def generate_routes(df, fleet, time_limit=5):
    data = prepare_data(df, fleet)
    results = solve_vrp(data, time_limit=time_limit)
    routes_full = decode_solution(df, fleet, results)
    assigned_stops = routes_full.merge(df, how="left")
    unassigned_stops = df.loc[~df["Ticket No"].isin(assigned_stops["Ticket No"])]
    return assigned_stops, unassigned_stops


if __name__ == "__main__":
    test_stops = pd.read_csv(
        "data/test/elias_test_geocoded.csv",
        dtype={"stop_id": str},
    )

    vehicle_ids = ["W01", "W02", "W03", "W05", "W06"]
    vehicle_type = ["Van", "Van", "Van", "Van", "Van"]
    depot = [
        "Mandela Way",
        "Mandela Way",
        "Mandela Way",
        "Mandela Way",
        "Mandela Way",
    ]
    lon = [-0.07962670, -0.07962670, -0.07962670, -0.07962670, -0.07962670]
    lat = [51.49175400, 51.49175400, 51.49175400, 51.49175400, 51.49175400]
    capacity = [500, 500, 500, 500, 500]
    dedicated_transport_zones = [None, None, None, None, None]

    vehicle_df = pd.DataFrame(
        {
            "Vehicle id": vehicle_ids,
            "Type": vehicle_type,
            "Capacity (#boxes)": capacity,
            "Depot": depot,
            "Dedicated transport zones": dedicated_transport_zones,
            "lat": lat,
            "lon": lon,
        }
    )

    test_stops = test_stops.loc[test_stops["Required Date"] == "17/11/2022"]
    assigned_stops, unassigned_stops = generate_routes(test_stops, vehicle_df)
    print(assigned_stops)
    print(unassigned_stops)
