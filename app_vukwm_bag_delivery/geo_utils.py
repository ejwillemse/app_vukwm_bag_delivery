"""
Utility functions for geo-processing.
"""
from typing import Union

import geopandas as gpd
import pandas as pd
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info


def get_crs_code(df: pd.DataFrame) -> str:
    """Get appropriate coordinate reference system for lat-lon points.

    Args:
        df: data frame with "latitude" and "longitude" columns.

    Returns:
        utm_crs.code: crs code, something like 32640

    Examples:
        '''python
        print(get_crs_code(pd.DataFrame({"latitude": [0, 0], "longitude": [0, 0]})))
        '''

        Output

        '''
        32630
        '''
    """
    utm_crs_list = query_utm_crs_info(
        datum_name="WGS 84",
        area_of_interest=AreaOfInterest(
            west_lon_degree=df["lon"].min(),
            south_lat_degree=df["lat"].min(),
            east_lon_degree=df["lon"].max(),
            north_lat_degree=df["lat"].max(),
        ),
    )
    utm_crs = utm_crs_list[0]
    return utm_crs.code


def add_xy_projected_coordinate_point_features(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Converts latitude longitude data-frame points into geodata-frame projected points.

    Args:
        df: has to have "latitude" and "longitude" coordinates
    Return:
        df_geo: same data-frame but with geometry and projects "x" and "y" coordinates.

    Example:
        '''python
        print(
            add_xy_projected_coordinate_point_features(
                pd.DataFrame({"latitude": [0, 0], "longitude": [0, 0]})
            )
        '''

        Output:

        '''
        latitude  longitude                  geometry              x    y
        0         0          0  POINT (833978.557 0.000)  833978.556919  0.0
        1         0          0  POINT (833978.557 0.000)  833978.556919  0.0
        '''
    """
    crs_code = get_crs_code(df)
    df_geo = gpd.GeoDataFrame(
        df.copy(),
        geometry=gpd.points_from_xy(x=df["lon"], y=df["lat"]),
        crs="EPSG:4326",
    ).to_crs(  # type: ignore
        crs_code
    )  # type: ignore
    df_geo = df_geo.assign(x=df_geo.geometry.x, y=df_geo.geometry.y)  # type: ignore
    return df_geo


if __name__ == "__main__":
    print(get_crs_code(pd.DataFrame({"latitude": [0, 0], "longitude": [0, 0]})))
    print(
        add_xy_projected_coordinate_point_features(
            pd.DataFrame({"latitude": [0, 0], "longitude": [0, 0]})
        )
    )
