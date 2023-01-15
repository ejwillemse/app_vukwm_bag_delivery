import numpy as np
import pandas as pd
import streamlit as st
from keplergl import KeplerGl


def return_config():
    config = {
        "version": "v1",
        "config": {
            "visState": {
                "filters": [
                    {
                        "dataId": ["assigned_stops"],
                        "id": "6migbh5d7",
                        "name": ["Arrival time"],
                        "type": "timeRange",
                        "value": [0, 9673451419000],
                        "enlarged": True,
                        "plotType": "histogram",
                        "animationWindow": "incremental",
                        "yAxis": None,
                        "speed": 1,
                    },
                    {
                        "dataId": ["assigned_stops"],
                        "id": "9zf5366ym",
                        "name": ["Vehicle Id"],
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
                        "id": "30wwgdw",
                        "type": "point",
                        "config": {
                            "dataId": "assigned_stops",
                            "label": "Stop",
                            "color": [255, 153, 31],
                            "highlightColor": [252, 242, 26, 255],
                            "columns": {
                                "lat": "latitude",
                                "lng": "longitude",
                                "altitude": None,
                            },
                            "isVisible": True,
                            "visConfig": {
                                "radius": 35,
                                "fixedRadius": False,
                                "opacity": 0.75,
                                "outline": False,
                                "thickness": 2,
                                "strokeColor": None,
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
                                        "name": "Stop sequence",
                                        "type": "integer",
                                    },
                                    "color": [255, 255, 255],
                                    "size": 18,
                                    "offset": [0, 0],
                                    "anchor": "middle",
                                    "alignment": "center",
                                }
                            ],
                        },
                        "visualChannels": {
                            "colorField": {"name": "Vehicle Id", "type": "string"},
                            "colorScale": "ordinal",
                            "strokeColorField": None,
                            "strokeColorScale": "quantile",
                            "sizeField": None,
                            "sizeScale": "linear",
                        },
                    },
                    {
                        "id": "vb8tg8f",
                        "type": "arc",
                        "config": {
                            "dataId": "assigned_stops",
                            "label": "Stop to road link",
                            "color": [146, 38, 198],
                            "highlightColor": [252, 242, 26, 255],
                            "columns": {
                                "lat0": "latitude",
                                "lng0": "longitude",
                                "lat1": "road_latitude",
                                "lng1": "road_longitude",
                            },
                            "isVisible": True,
                            "visConfig": {
                                "opacity": 0.5,
                                "thickness": 3,
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
                                "sizeRange": [0, 10],
                                "targetColor": None,
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
                            "colorField": {"name": "Vehicle Id", "type": "string"},
                            "colorScale": "ordinal",
                            "sizeField": None,
                            "sizeScale": "linear",
                        },
                    },
                    {
                        "id": "uhxkucr",
                        "type": "point",
                        "config": {
                            "dataId": "depots",
                            "label": "Depots",
                            "color": [255, 254, 230],
                            "highlightColor": [252, 242, 26, 255],
                            "columns": {"lat": "lat", "lng": "lon", "altitude": None},
                            "isVisible": True,
                            "visConfig": {
                                "radius": 30.4,
                                "fixedRadius": False,
                                "opacity": 1,
                                "outline": True,
                                "thickness": 3.5,
                                "strokeColor": [214, 214, 213],
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
                                "filled": False,
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
                            "strokeColorField": None,
                            "strokeColorScale": "quantile",
                            "sizeField": None,
                            "sizeScale": "linear",
                        },
                    },
                    {
                        "id": "dvqkcg",
                        "type": "geojson",
                        "config": {
                            "dataId": "assigned_stops",
                            "label": "Travel path",
                            "color": [218, 112, 191],
                            "highlightColor": [252, 242, 26, 255],
                            "columns": {"geojson": "travel_path_to_stop"},
                            "isVisible": True,
                            "visConfig": {
                                "opacity": 0.8,
                                "strokeOpacity": 0.5,
                                "thickness": 0.8,
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
                                "name": "Vehicle Id",
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
                    {
                        "id": "7b21nms",
                        "type": "point",
                        "config": {
                            "dataId": "unserviced_stops",
                            "label": "Unscheduled stops",
                            "color": [187, 0, 0],
                            "highlightColor": [252, 242, 26, 255],
                            "columns": {
                                "lat": "latitude",
                                "lng": "longitude",
                                "altitude": None,
                            },
                            "isVisible": True,
                            "visConfig": {
                                "radius": 15,
                                "fixedRadius": False,
                                "opacity": 0.8,
                                "outline": False,
                                "thickness": 2,
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
                            "strokeColorField": None,
                            "strokeColorScale": "quantile",
                            "sizeField": None,
                            "sizeScale": "linear",
                        },
                    },
                ],
                "interactionConfig": {
                    "tooltip": {
                        "fieldsToShow": {
                            "assigned_stops": [
                                {"name": "Vehicle Id", "format": None},
                                {"name": "Vehicle profile", "format": None},
                                {"name": "Stop sequence", "format": None},
                                {"name": "Site Bk", "format": None},
                                {"name": "Customer Bk", "format": None},
                                {"name": "Site Name", "format": None},
                                {"name": "Site Address", "format": None},
                                {"name": "Arrival time", "format": None},
                                {"name": "Service start time", "format": None},
                                {"name": "Departure time", "format": None},
                                {"name": "Waiting time (minutes)", "format": None},
                                {"name": "Service duration (minutes)", "format": None},
                                {"name": "Product description", "format": None},
                                {"name": "Transport Area Code", "format": None},
                                {"name": "Time window start", "format": None},
                                {"name": "Time window end", "format": None},
                                {"name": "Service issues", "format": None},
                                {"name": "Activity type", "format": None},
                                {"name": "Ticket No", "format": None},
                            ],
                            "depots": [
                                {"name": "Depot", "format": None},
                                {"name": "Vehicles", "format": None},
                            ],
                            "unserviced_stops": [
                                {"name": "Vehicle Id", "format": None},
                                {"name": "Vehicle profile", "format": None},
                                {"name": "Stop sequence", "format": None},
                                {"name": "Site Bk", "format": None},
                                {"name": "Customer Bk", "format": None},
                                {"name": "Site Name", "format": None},
                                {"name": "Site Address", "format": None},
                                {"name": "Product description", "format": None},
                                {"name": "Transport Area Code", "format": None},
                                {"name": "Time window start", "format": None},
                                {"name": "Time window end", "format": None},
                                {"name": "Activity type", "format": None},
                                {"name": "Ticket No", "format": None},
                            ],
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
                "latitude": 51.49872101220479,
                "longitude": -0.14554385480574963,
                "pitch": 0,
                "zoom": 11.81691194273703,
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


MAPPING = {
    "route_id": "Vehicle Id",
    "vehicle_profile": "Vehicle profile",
    "stop_id": "Site Bk",
    "stop_sequence": "Stop sequence",
    "job_sequence": "Job sequence",
    "arrival_time": "Arrival time",
    "service_start_time": "Service start time",
    "departure_time": "Departure time",
    "waiting_duration__seconds": "Waiting time (minutes)",
    "travel_duration_to_stop__seconds": "Travel duration to stop (minutes)",
    "travel_distance_to_stop__meters": "Travel distance to stops (km)",
    "travel_speed__kmh": "Travel speed (km/h)",
    "service_duration__seconds": "Service duration (minutes)",
    "activity_type": "Activity type",
    "skills": "Skills",
    "latitude": "latitude",
    "longitude": "longitude",
    "travel_path_to_stop": "travel_path_to_stop",
    "road_snap_longitude": "road_longitude",
    "road_snap_latitude": "road_latitude",
    "time_window_start": "Time window start",
    "time_window_end": "Time window end",
    "service_issue": "Service issues",
}
VEHICLE_TYPE_MAPPING = {"auto": "Van", "bicycle": "Bicycle"}


def display_format(unassigned_stops):
    unassigned_stops = unassigned_stops[
        [
            "Customer Bk",
            "Site Bk",
            "Site Name",
            "Transport Area Code",
            "Product description",
            "Site Address",
            "Ticket No",
        ]
    ].copy()
    unassigned_stops["Product description"] = unassigned_stops[
        "Product description"
    ].str.replace("\n", "; ")
    unassigned_stops["Site Bk"] = unassigned_stops["Site Bk"].astype(str)
    return unassigned_stops


def display_format_unscheduled_stops(unassigned_stops, unserviced_stops):
    unassigned_stops_display = display_format(unassigned_stops)
    unscheduled_stops_display = unassigned_stops_display.merge(
        unserviced_stops[
            ["latitude", "longitude", "stop_id", "time_window_start", "time_window_end"]
        ]
        .assign(stop_id=unserviced_stops["stop_id"].astype(str))
        .rename(
            columns={
                "stop_id": "Site Bk",
                "time_window_start": "Time window start",
                "time_window_end": "Time window end",
            }
        ),
        how="inner",
        left_on="Site Bk",
        right_on="Site Bk",
        validate="1:1",
    )
    return unscheduled_stops_display


def return_unserviced_stops_display(unassigned_stops, unserviced_stops):
    unserviced_stops_display = display_format_unscheduled_stops(
        unassigned_stops, unserviced_stops
    )
    return unserviced_stops_display


def unit_conversions(assigned_stops):
    assigned_stops = assigned_stops.assign(
        vehicle_profile=assigned_stops["vehicle_profile"].replace(VEHICLE_TYPE_MAPPING),
        waiting_duration__seconds=(
            assigned_stops["waiting_duration__seconds"] / 60
        )  # to minutes
        .round(0)
        .astype(int),
        travel_distance_to_stop__meters=(
            assigned_stops["travel_distance_to_stop__meters"] / 1000
        ).round(2),
        travel_duration_to_stop__seconds=(
            assigned_stops["travel_duration_to_stop__seconds"] / 60
        )  # to minutes
        .round(0)
        .astype(int),
        service_duration__seconds=(
            assigned_stops["service_duration__seconds"] / 60
        )  # to minutes
        .round(0)
        .astype(int),
        travel_speed__kmh=(assigned_stops["travel_speed__kmh"]).round(1),
    )
    return assigned_stops


def return_assigned_stops_display(assigned_stops, unassigned_stops):
    assigned_stops_display = unit_conversions(assigned_stops)
    assigned_stops_display = assigned_stops_display.rename(columns=MAPPING)[
        MAPPING.values()
    ]
    unassigned_stops_display = display_format(unassigned_stops)
    assigned_stops_display = assigned_stops_display.merge(
        unassigned_stops_display, left_on="Site Bk", right_on="Site Bk", how="left"
    ).fillna(" ")
    return assigned_stops_display


def combine_vehicle_id_type(df):
    df = df.sort_values(["Vehicle id"])
    vehicles = df["Vehicle id"].values
    profiles = df["Type"].values
    vehicle_info = "; ".join(
        [f"{vehicles[i]} ({profiles[i]})" for i in range(vehicles.shape[0])]
    )
    return vehicle_info


def display_format_depot(unassigned_routes):
    depots = (
        unassigned_routes.groupby(["Depot", "lon", "lat"])
        .apply(combine_vehicle_id_type)
        .reset_index()
        .rename(columns={0: "Vehicles"})
    )
    return depots


def return_depot_display(unassigned_routes):
    depots = display_format_depot(unassigned_routes)
    return depots


def add_time_windows(df):
    unassigned_stops_formatted = st.session_state.data_03_primary["unassigned_stops"]
    df = df.assign(**{"stop_id": df["stop_id"].astype(str)}).merge(
        unassigned_stops_formatted.assign(
            **{"stop_id": unassigned_stops_formatted["stop_id"].astype(str)}
        )[["stop_id", "time_window_start", "time_window_end"]],
        how="left",
        left_on="stop_id",
        right_on="stop_id",
    )
    return df


def return_map():
    assigned_stops = st.session_state.data_07_reporting["assigned_stops"].copy()
    unassigned_routes = st.session_state.data_02_intermediate[
        "unassigned_routes"
    ].copy()
    unassigned_stops = st.session_state.data_02_intermediate["unassigned_stops"].copy()
    unserviced_stops = st.session_state.data_07_reporting["unserviced_stops"].copy()
    # unserviced_stops = add_time_windows(
    #     unserviced_stops
    # )

    if (
        "view_routes" in st.session_state
        and "filter_vehicles" in st.session_state.view_routes
    ):
        filter_routes = st.session_state.view_routes["filter_vehicles"]
        if filter_routes:
            assigned_stops = assigned_stops.loc[
                assigned_stops["route_id"].isin(filter_routes)
            ]
    assigned_stops_display = return_assigned_stops_display(
        assigned_stops, unassigned_stops
    )
    if unserviced_stops.shape[0] > 0:
        unserviced_stops_display = return_unserviced_stops_display(
            unassigned_stops, unserviced_stops
        )
    else:
        unserviced_stops_display = pd.DataFrame()
    depots = return_depot_display(unassigned_routes)
    assigned_stops_display.loc[
        assigned_stops_display["Activity type"] == "DEPOT_START_END", "latitude"
    ] = np.nan
    assigned_stops_display.loc[
        assigned_stops_display["Activity type"] == "DEPOT_START_END", "lon"
    ] = np.nan
    m = KeplerGl(
        data={
            "assigned_stops": assigned_stops_display.copy().fillna(" "),
            "depots": depots,
            "unserviced_stops": unserviced_stops_display,
        },
        height=750,
        config=return_config(),
    )
    html = m._repr_html_(center_map=True, read_only=False)
    return html
