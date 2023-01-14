import numpy as np
import pandas as pd
from keplergl import KeplerGl
from shapely import wkt


def return_route_config():
    config = {
        "version": "v1",
        "config": {
            "visState": {
                "filters": [
                    {
                        "dataId": ["orders"],
                        "id": "yt10dkouq",
                        "name": ["arrival_time"],
                        "type": "timeRange",
                        "value": [1671613200000, 1671626666000],
                        "enlarged": True,
                        "plotType": "histogram",
                        "animationWindow": "free",
                        "yAxis": None,
                        "speed": 1,
                    },
                    {
                        "dataId": ["orders"],
                        "id": "wrkhad0sp",
                        "name": ["Registration No"],
                        "type": "multiSelect",
                        "value": [],
                        "enlarged": False,
                        "plotType": "histogram",
                        "animationWindow": "free",
                        "yAxis": None,
                        "speed": 1,
                    },
                ],
                "layers": [
                    {
                        "id": "o4a1e2",
                        "type": "point",
                        "config": {
                            "dataId": "orders",
                            "label": "Stops",
                            "color": [241, 92, 23],
                            "highlightColor": [252, 242, 26, 255],
                            "columns": {
                                "lat": "Site Latitude",
                                "lng": "Site Longitude",
                                "altitude": None,
                            },
                            "isVisible": True,
                            "visConfig": {
                                "radius": 15,
                                "fixedRadius": False,
                                "opacity": 0.81,
                                "outline": True,
                                "thickness": 2,
                                "strokeColor": [25, 20, 16],
                                "colorRange": {
                                    "name": "Uber Viz Qualitative 4",
                                    "type": "qualitative",
                                    "category": "Uber",
                                    "colors": [
                                        "#12939A",
                                        "#DDB27C",
                                        "#88572C",
                                        "#FF991F",
                                        "#F15C17",
                                        "#223F9A",
                                        "#DA70BF",
                                        "#125C77",
                                        "#4DC19C",
                                        "#776E57",
                                        "#17B8BE",
                                        "#F6D18A",
                                        "#B7885E",
                                        "#FFCB99",
                                        "#F89570",
                                        "#829AE3",
                                        "#E79FD5",
                                        "#1E96BE",
                                        "#89DAC1",
                                        "#B3AD9E",
                                    ],
                                },
                                "strokeColorRange": {
                                    "name": "Global Warming",
                                    "type": "sequential",
                                    "category": "Uber",
                                    "colors": [
                                        "#5A1846",
                                        "#900C3F",
                                        "#C70039",
                                        "#E3611C",
                                        "#F1920E",
                                        "#FFC300",
                                    ],
                                },
                                "radiusRange": [0, 50],
                                "filled": True,
                            },
                            "hidden": False,
                            "textLabel": [
                                {
                                    "field": {
                                        "name": "route_sequence",
                                        "type": "integer",
                                    },
                                    "color": [205, 201, 191],
                                    "size": 18,
                                    "offset": [0, 0],
                                    "anchor": "start",
                                    "alignment": "center",
                                }
                            ],
                        },
                        "visualChannels": {
                            "colorField": {"name": "Registration No", "type": "string"},
                            "colorScale": "ordinal",
                            "strokeColorField": None,
                            "strokeColorScale": "quantile",
                            "sizeField": None,
                            "sizeScale": "linear",
                        },
                    },
                    {
                        "id": "h5ysd8s",
                        "type": "geojson",
                        "config": {
                            "dataId": "orders",
                            "label": "Routes",
                            "color": [255, 203, 153],
                            "highlightColor": [252, 242, 26, 255],
                            "columns": {"geojson": "geometry"},
                            "isVisible": True,
                            "visConfig": {
                                "opacity": 0.8,
                                "strokeOpacity": 0.8,
                                "thickness": 0.5,
                                "strokeColor": None,
                                "colorRange": {
                                    "name": "Global Warming",
                                    "type": "sequential",
                                    "category": "Uber",
                                    "colors": [
                                        "#5A1846",
                                        "#900C3F",
                                        "#C70039",
                                        "#E3611C",
                                        "#F1920E",
                                        "#FFC300",
                                    ],
                                },
                                "strokeColorRange": {
                                    "name": "Uber Viz Qualitative 4",
                                    "type": "qualitative",
                                    "category": "Uber",
                                    "colors": [
                                        "#12939A",
                                        "#DDB27C",
                                        "#88572C",
                                        "#FF991F",
                                        "#F15C17",
                                        "#223F9A",
                                        "#DA70BF",
                                        "#125C77",
                                        "#4DC19C",
                                        "#776E57",
                                        "#17B8BE",
                                        "#F6D18A",
                                        "#B7885E",
                                        "#FFCB99",
                                        "#F89570",
                                        "#829AE3",
                                        "#E79FD5",
                                        "#1E96BE",
                                        "#89DAC1",
                                        "#B3AD9E",
                                    ],
                                },
                                "radius": 10,
                                "sizeRange": [0, 10],
                                "radiusRange": [0, 50],
                                "heightRange": [0, 500],
                                "elevationScale": 5,
                                "enableElevationZoomFactor": True,
                                "stroked": True,
                                "filled": False,
                                "enable3d": False,
                                "wireframe": False,
                            },
                            "hidden": False,
                            "textLabel": [
                                {
                                    "field": None,
                                    "color": [255, 255, 255],
                                    "size": 18,
                                    "offset": [0, 0],
                                    "anchor": "start",
                                    "alignment": "center",
                                }
                            ],
                        },
                        "visualChannels": {
                            "colorField": None,
                            "colorScale": "quantile",
                            "strokeColorField": {
                                "name": "Registration No",
                                "type": "string",
                            },
                            "strokeColorScale": "ordinal",
                            "sizeField": None,
                            "sizeScale": "linear",
                            "heightField": None,
                            "heightScale": "linear",
                            "radiusField": None,
                            "radiusScale": "linear",
                        },
                    },
                ],
                "interactionConfig": {
                    "tooltip": {
                        "fieldsToShow": {
                            "orders": [
                                {"name": "Customer Bk", "format": None},
                                {"name": "Site Bk", "format": None},
                                {"name": "Site Name", "format": None},
                                {"name": "Transport Area Code", "format": None},
                                {"name": "Site Address", "format": None},
                                {"name": "Notes", "format": None},
                                {"name": "Product description", "format": None},
                                {"name": "Registration No", "format": None},
                                {"name": "route_sequence", "format": None},
                                {"name": "Transport area", "format": None},
                                {"name": "Type", "format": None},
                                {"name": "arrival_time", "format": None},
                                {"name": "depart_time", "format": None},
                            ]
                        },
                        "compareMode": False,
                        "compareType": "absolute",
                        "enabled": True,
                    },
                    "brush": {"size": 0.5, "enabled": False},
                    "geocoder": {"enabled": False},
                    "coordinate": {"enabled": False},
                },
                "layerBlending": "normal",
                "splitMaps": [],
                "animationConfig": {"currentTime": None, "speed": 1},
            },
            "mapState": {
                "bearing": 0,
                "dragRotate": False,
                "latitude": 51.503679000596435,
                "longitude": -0.11381729292045753,
                "pitch": 0,
                "zoom": 12.5,
                "isSplit": False,
            },
            "mapStyle": {
                "styleType": "dark",
                "topLayerGroups": {},
                "visibleLayerGroups": {
                    "label": True,
                    "road": True,
                    "border": False,
                    "building": True,
                    "water": True,
                    "land": True,
                    "3d building": False,
                },
                "threeDBuildingColor": [
                    9.665468314072013,
                    17.18305478057247,
                    31.1442867897876,
                ],
                "mapStyles": {},
            },
        },
    }
    return config


def generate_route_data(
    assigned_stops, unassigned_routes, unassigned_stops, travel_legs
):
    assigned_stops["Registration No"] = assigned_stops["Vehicle id"]
    assigned_stops = assigned_stops[
        list(unassigned_stops.columns) + ["route_sequence", "Vehicle id"]
    ]

    assigned_stops_route = assigned_stops.merge(
        unassigned_routes.drop(columns=["lat", "lon"])
    )

    assigned_stops_route = assigned_stops_route.assign(
        route_id=assigned_stops_route["Vehicle id"],
        latitude=assigned_stops_route["lat"],
        longitude=assigned_stops_route["lon"],
        vehicle_type=assigned_stops_route["Type"],
        stop_id=np.arange(0, assigned_stops_route.shape[0]),
    )

    unassigned_routes = unassigned_routes.assign(
        route_id=unassigned_routes["Vehicle id"], vehicle_type=unassigned_routes["Type"]
    )

    travel_legs["geometry"] = travel_legs["geometry"].apply(wkt.dumps)
    travel_legs = pd.DataFrame(travel_legs)

    travel_legs["route_sequence"] = travel_legs["travel_sequence"] + 1
    assigned_stops_route_paths = assigned_stops_route.merge(travel_legs, how="left")
    assigned_stops_route_paths["duration_seconds"] = assigned_stops_route_paths[
        "duration_seconds"
    ].fillna(0)
    assigned_stops_route_paths["distance_km"] = assigned_stops_route_paths[
        "distance_km"
    ].fillna(0)

    assigned_stops_route_paths["service_duration_seconds"] = (
        assigned_stops_route_paths["Average TAT per delivery (min)"]
        * 60
        * (~assigned_stops_route_paths["Ticket No"].isna())
    )

    assigned_stops_route_paths["travel_to_service_duration"] = (
        assigned_stops_route_paths["duration_seconds"]
        + assigned_stops_route_paths["service_duration_seconds"]
    )
    assigned_stops_route_paths["total_duration"] = assigned_stops_route_paths.groupby(
        ["route_id"]
    )["travel_to_service_duration"].cumsum()

    assigned_stops_route_paths["depart_stop_seconds"] = assigned_stops_route_paths[
        "total_duration"
    ]
    assigned_stops_route_paths["arrive_stop_seconds"] = (
        assigned_stops_route_paths["total_duration"]
        - assigned_stops_route_paths["service_duration_seconds"]
    )
    assigned_stops_route_paths["arrival_time"] = pd.to_datetime(
        assigned_stops_route_paths["Shift start time"]
    ) + pd.to_timedelta(assigned_stops_route_paths["arrive_stop_seconds"], unit="s")
    assigned_stops_route_paths["depart_time"] = pd.to_datetime(
        assigned_stops_route_paths["Shift start time"]
    ) + pd.to_timedelta(assigned_stops_route_paths["depart_stop_seconds"], unit="s")

    return assigned_stops_route_paths


def return_map_html(df):
    df = df.copy()
    df["arrival_time"] = df["arrival_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    df["depart_time"] = df["depart_time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    m = KeplerGl(
        data={"orders": df},
        config=return_route_config(),
    )
    html = m._repr_html_(center_map=True, read_only=False)
    return html


if __name__ == "__main__":
    import pandas as pd

    unassigned_stops = pd.read_csv("data/test/unassigned_jobs.csv")
    assigned_stops = pd.read_csv("data/test/route_test.csv")
    unassigned_routes = pd.read_csv("data/test/fleet_test.csv")
    results = generate_route_data(assigned_stops, unassigned_routes, unassigned_stops)
    print(return_map_html(results))
