"""
Get and format OSRM route info. See https://project-osrm.org/docs/v5.24.0/api/#route-service
"""


import logging
from typing import Callable, Dict, Tuple, Union

import geopandas as gpd
import pandas as pd
import requests

try:
    import app_vukwm_bag_delivery.osrm as osrm
except:
    import osrm

BACKUP_PORT = "http://router.project-osrm.org"
PORT_TYPE_MAPPING = {
    "Bicycle": "http://34.216.224.175:8001",
    "Van": "http://34.216.224.175:8000",
    "default": "http://router.project-osrm.org",
}
OSRM_DRIVING_DEFAULTS = {
    "steps": "true",
    "annotations": "true",
    "overview": "full",
    "geometries": "geojson",
    "continue_straight": "false",
}
BOUNDING_BOX = {
    "min_lon": -0.2432798003,
    "min_lat": 51.4463733546,
    "max_lon": -0.0372096046,
    "max_lat": 51.5727989572,
}
TIMEOUT_LIMIT = 300  # seconds


def generate_osrm_defaults(osrm_driving_defaults: Union[Dict, None] = None) -> str:
    """Generate OSRM input parameter string"""
    if osrm_driving_defaults is None:
        osrm_driving_defaults = OSRM_DRIVING_DEFAULTS
    return "&".join(
        [f"{key}={osrm_driving_defaults[key]}" for key in osrm_driving_defaults]
    )


def generate_osrm_point_inputs(
    stops: pd.DataFrame, lon_col="longitude", lat_col="latitude"
) -> str:
    """Generate OSRM lon-lat point info for routing"""
    coordinates = ";".join(stops[[lon_col, lat_col]].astype(str).agg(",".join, axis=1))
    return coordinates


def get_osrm_request(
    port: str, coordinates: str, defaults: Callable, timeout: float = 30
) -> Union[Dict, str]:
    """Get OSRM response"""
    request = f"{port}/route/v1/driving/{coordinates}?{defaults()}"
    logging.info("OSRM request: `%s`" % request)
    with requests.get(request, timeout=timeout) as req:
        results = req.json()

    if results["code"] != "Ok":
        message = results["message"]
        logging.error(message)
        raise ValueError(f"OSRM request failed: `{message}`\n Request: `{request}`")
    return results


def generate_osrm_route(
    route_stops: pd.DataFrame, vehicle_type: Union[str, None] = None
) -> Union[Dict, str]:
    """Solve route using OSRM solver, based on route type."""
    if vehicle_type is None:
        port = PORT_TYPE_MAPPING["default"]
    else:
        port = PORT_TYPE_MAPPING[vehicle_type]
    coordinates = generate_osrm_point_inputs(route_stops)
    results = get_osrm_request(port, coordinates, generate_osrm_defaults)
    return results


def generate_trip_info(
    results: dict,
) -> Tuple[gpd.GeoDataFrame, pd.DataFrame, gpd.GeoDataFrame]:
    """Convert results into data-frames."""
    normalizer = osrm.OsrmRoutePathNormalizer(
        results, route_path_type="routes", order_sequence=False
    )
    leg_info = normalizer.extract_travel_leg_info()
    stop_sequence_info = normalizer.extract_road_snap_info()
    route_summary_info = normalizer.extract_travel_summary_info()
    return leg_info, stop_sequence_info, route_summary_info


def return_route_osrm_info(
    assigned_routes: pd.DataFrame,
    assigned_stops: pd.DataFrame,
    route_id_name: str = "route_id",
    vehicle_type_name: str = "vehicle_type",
) -> Tuple[gpd.GeoDataFrame, pd.DataFrame, gpd.GeoDataFrame]:
    leg_info = []
    stop_sequence_info = []
    route_summary_info = []
    vehicle_id_types = (
        assigned_routes[[route_id_name, vehicle_type_name]].drop_duplicates().values
    )

    n_nans_lon = assigned_stops["longitude"].isna().sum()
    n_nans_lat = assigned_stops["latitude"].isna().sum()
    if n_nans_lon > 0 or n_nans_lat > 0:
        logging.warning(
            f"NaN coordinates present in {n_nans_lon} records and will be dropped"
        )
        assigned_stops = assigned_stops.dropna(subset=["latitude"]).dropna(
            subset=["longitude"]
        )

    for route_id, route_type in vehicle_id_types:
        logging.info("Processing %s" % route_id)
        route_stops = assigned_stops.loc[assigned_stops[route_id_name] == route_id]
        results = generate_osrm_route(route_stops, route_type)
        leg_info_i, stop_sequence_info_i, route_summary_info_i = generate_trip_info(
            results
        )
        leg_info_i[route_id_name] = route_id
        stop_sequence_info_i[route_id_name] = route_id
        route_summary_info_i[route_id_name] = route_id
        leg_info.append(leg_info_i)
        stop_sequence_info.append(stop_sequence_info_i)
        route_summary_info.append(route_summary_info_i)
    leg_info = pd.concat(leg_info).reset_index(drop=True)
    stop_sequence_info = pd.concat(stop_sequence_info).reset_index(drop=True)
    route_summary_info = pd.concat(route_summary_info).reset_index(drop=True)
    return (
        leg_info,
        stop_sequence_info,
        route_summary_info,
    )  # type: ignore
