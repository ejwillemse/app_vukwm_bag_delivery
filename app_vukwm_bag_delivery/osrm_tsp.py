"""
Solving a single TSP instance using OSRM.

Input -> lat-lon data-frame, with start point and start and end point at end + vehicle type for OSRM profile purposes.
Output -> sequenced lat-lon data-frame + travel leg info.
"""
import logging
from typing import Dict, Tuple

import geopandas as gpd
import pandas as pd
import requests

try:
    import app_vukwm_bag_delivery.osrm as osrm
except:
    import osrm

import numpy as np

OSRM_DRIVING_DEFAULTS = {
    "roundtrip": "false",
    "source": "first",
    "destination": "last",
    "steps": "true",
    "annotations": "true",
    "overview": "full",
    "geometries": "geojson",
}
BOUNDING_BOX = {
    "min_lon": -0.2432798003,
    "min_lat": 51.4463733546,
    "max_lon": -0.0372096046,
    "max_lat": 51.5727989572,
}
TIMEOUT_LIMIT = 300  # seconds


def check_bounding_area(
    stops: pd.DataFrame, bounding_box: Dict = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Check if points fall within bounding box, and if not remove and send seperately"""
    if bounding_box is None:
        bounding_box = BOUNDING_BOX
    outside_bounds = (
        (stops["lon"] > bounding_box["max_lon"])
        | (stops["lon"] < bounding_box["min_lon"])
        | (stops["lat"] > bounding_box["max_lat"])
        | (stops["lat"] < bounding_box["min_lat"])
    )

    if outside_bounds.sum() > 0:
        logging.warning(
            "%i of %i stops fall outside the bounding box area and will be returned is unassigned.",
            outside_bounds.sum(),
            outside_bounds.shape[0],
        )

    inside_bounds_stops = stops.loc[~outside_bounds]
    outside_bounds_stops = stops.loc[outside_bounds]
    return inside_bounds_stops, outside_bounds_stops


def generate_osrm_defaults(osrm_driving_defaults: Dict = None) -> str:
    """Generate OSRM input parameter string"""
    if osrm_driving_defaults is None:
        osrm_driving_defaults = OSRM_DRIVING_DEFAULTS
    return "&".join(
        [f"{key}={osrm_driving_defaults[key]}" for key in osrm_driving_defaults]
    )


def generate_osrm_point_inputs(
    stops: pd.DataFrame, lon_col="lon", lat_col="lat"
) -> str:
    """Generate OSRM lon-lat point info for routing"""
    coordinates = ";".join(stops[[lon_col, lat_col]].astype(str).agg(",".join, axis=1))
    return coordinates


def get_osrm_request(
    port: str, coordinates: str, defaults: str, timeout: float = 30
) -> dict:
    """Get OSRM response"""
    request = f"{port}/trip/v1/driving/{coordinates}?{defaults()}"
    with requests.get(request, timeout=timeout) as req:
        results = req.json()
    print(request)
    if results["code"] != "Ok":
        message = results["message"]
        raise ValueError(f"OSRM request failed: '{message}'")
    return results


def generate_osrm_tsp_route(
    route_stops: pd.DataFrame, vehicle_type: str = None, ports=None
) -> Tuple[dict, bool]:
    """Solve route using OSRM solver, based on route type."""
    if vehicle_type is None:
        port = ports["default"]
    else:
        port = ports[vehicle_type]
    coordinates = generate_osrm_point_inputs(route_stops)
    results = get_osrm_request(port, coordinates, generate_osrm_defaults)
    osrm_tsp_success = True
    return results, osrm_tsp_success


def generate_trip_info(
    results: dict,
) -> Tuple[gpd.GeoDataFrame, pd.DataFrame, gpd.GeoDataFrame]:
    """Convert results into data-frames."""
    normalizer = osrm.OsrmRoutePathNormalizer(
        results, route_path_type="trips", order_sequence=False
    )
    leg_info = normalizer.extract_travel_leg_info()
    stop_sequence_info = normalizer.extract_road_snap_info()
    route_summary_info = normalizer.extract_travel_summary_info()
    return leg_info, stop_sequence_info, route_summary_info


def assign_to_from_stop_ids(assigned_route_stops: pd.DataFrame):
    """Assign to and from stops for merging with travel leg info."""
    assigned_route_stops["stop_from_id"] = (
        assigned_route_stops["stop_id"].shift().values
    )
    assigned_route_stops["stop_to_id"] = assigned_route_stops["stop_id"].values
    return assigned_route_stops


def generate_tsp_route(
    unsequenced_route_stops: pd.DataFrame, route_id=None, route_column=None, ports=None
) -> Tuple[pd.DataFrame, gpd.GeoDataFrame, pd.DataFrame]:
    """Generate tsp route and all related information.
    Send stops outside area back as unassigned stops."""
    vehicle_type = "Van"
    inside_stops, unassigned_route_stops = check_bounding_area(unsequenced_route_stops)
    route_results, _ = generate_osrm_tsp_route(inside_stops, vehicle_type, ports)
    travel_leg_info, stop_sequence_info, route_summary_info = generate_trip_info(
        route_results
    )
    unassigned_route_stops = unassigned_route_stops.reset_index(drop=True)
    assigned_route_stops = inside_stops.copy().reset_index(drop=True)
    assigned_route_stops = (
        pd.concat([assigned_route_stops, stop_sequence_info], axis=1)
        .sort_values(["route_sequence"])
        .reset_index(drop=True)
    )

    assigned_route_stops = assign_to_from_stop_ids(assigned_route_stops)
    travel_leg_info[["stop_from_id", "stop_to_id"]] = assigned_route_stops.iloc[1:][
        ["stop_from_id", "stop_to_id"]
    ].values

    if route_id is not None and route_column is not None:
        travel_leg_info[route_column] = route_id
        route_summary_info[route_column] = route_id
    return (
        assigned_route_stops,
        travel_leg_info,
        unassigned_route_stops,
        route_summary_info,
    )


def sequence_routes(df, route_column="Registration No", ports=None):
    df = df.copy().dropna(subset=route_column)
    df["stop_id"] = np.arange(0, df.shape[0])
    all_routes_assigned_stops = []
    all_routes_travel_legs = []
    all_routes_unassigned_stops = []
    all_routes_summary_info = []
    routes = df[route_column].sort_values().unique()
    for route_i in routes:
        df_route_i = df.loc[df[route_column] == route_i]
        (
            assigned_route_stops,
            travel_leg_info,
            unassigned_route_stops,
            route_summary_info,
        ) = generate_tsp_route(df_route_i, route_i, route_column, ports)
        all_routes_assigned_stops.append(assigned_route_stops)
        all_routes_travel_legs.append(travel_leg_info)
        all_routes_unassigned_stops.append(unassigned_route_stops)
        all_routes_summary_info.append(route_summary_info)

    all_routes_assigned_stops = pd.concat(all_routes_assigned_stops)
    all_routes_assigned_stops = all_routes_assigned_stops.rename(
        columns={"travel_sequence": "Delivery sequence"}
    )

    all_routes_travel_legs = pd.concat(all_routes_travel_legs).reset_index(drop=True)
    all_routes_unassigned_stops = pd.concat(all_routes_unassigned_stops).reset_index(
        drop=True
    )
    all_routes_summary_info = (
        pd.concat(all_routes_summary_info)
        .rename(
            columns={
                "total_distance_km": "Total route distance (km)",
                "total_travel_duration_hours": "Total route travel time (h)",
            }
        )[
            [
                route_column,
                "Total route distance (km)",
                "Total route travel time (h)",
                "geometry",
            ]
        ]
        .reset_index(drop=True)
    )

    return (
        all_routes_assigned_stops,
        all_routes_travel_legs,
        all_routes_unassigned_stops,
        all_routes_summary_info,
    )


if __name__ == "__main__":
    test_stops = pd.read_csv(
        "test.csv",
        dtype={"stop_id": str},
    )
    test_stops = test_stops.loc[test_stops["Required Date"] == "17/11/2022"]
    results = sequence_routes(test_stops)
    print(results[-1])
