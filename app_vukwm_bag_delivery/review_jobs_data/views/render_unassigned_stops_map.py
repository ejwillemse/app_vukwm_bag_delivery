from keplergl import KeplerGl

import app_vukwm_bag_delivery.aggregates as aggregates


def return_order_config():
    config = {
        "version": "v1",
        "config": {
            "visState": {
                "filters": [],
                "layers": [
                    {
                        "id": "o4a1e2",
                        "type": "point",
                        "config": {
                            "dataId": "orders",
                            "label": "Orders",
                            "color": [241, 92, 23],
                            "highlightColor": [252, 242, 26, 255],
                            "columns": {
                                "lat": "Site Latitude",
                                "lng": "Site Longitude",
                                "altitude": None,
                            },
                            "isVisible": True,
                            "visConfig": {
                                "radius": 10,
                                "fixedRadius": False,
                                "opacity": 0.5,
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
                            "colorField": {"name": "Transport area", "type": "string"},
                            "colorScale": "ordinal",
                            "strokeColorField": None,
                            "strokeColorScale": "quantile",
                            "sizeField": None,
                            "sizeScale": "linear",
                        },
                    }
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
                "latitude": 51.50854710208261,
                "longitude": -0.163391534356915,
                "pitch": 0,
                "zoom": 11.5406604813537,
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


def return_order_map_html(df):
    df_map = df.copy()
    df_map["Transport area"] = "#" + df_map["Transport Area"].astype(str).str.zfill(2)
    m = KeplerGl(data={"orders": df_map.fillna("")}, config=return_order_config())
    return m._repr_html_(center_map=True, read_only=False)
