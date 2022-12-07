import logging
from typing import AnyStr, Dict, List
import re
import googlemaps
import numpy as np
import pandas as pd
import logging


logger = logging.getLogger(__name__)


def geocode_addresses_via_google_maps(
    search_strings: List[str], api_key: str = None, city_string: str = ""
) -> List[dict]:
    """Geocode addresses using google-maps API.

    Args:
        search_strings: address info to be used for searching
        api_key: API key for geocoding

    Returns:
        all_geocode_results: list with a dictionary of google search results, the form
            {`search_address`:..., `geocode_results`:...}
    """
    gmaps = googlemaps.Client(key=api_key)
    n_search_strings = len(search_strings)
    logger.info(f"Geocoding {n_search_strings} locations..")
    all_geocode_results = []
    for i, search_address in enumerate(search_strings):
        if (i + 1) % 25 == 0:
            logging.info(f"Geocoded {i + 1} of {n_search_strings} locations.")
        geocode_result = gmaps.geocode(search_address + city_string)
        if not geocode_result:
            logger.warning(
                f"Search string {search_address} hard failed on google-API side"
            )
        else:
            all_geocode_results.append(
                {"search_address": search_address, "geocode_results": geocode_result}
            )
    return all_geocode_results


def expand_df(data: pd.DataFrame, expand_columns: list) -> pd.DataFrame:
    """Expand data frame that has columns with values fof type dictionary"""
    data = data.copy()
    for c in expand_columns:
        data = pd.concat(
            [data.drop([c], axis="columns"), data[c].apply(pd.Series)],
            axis="columns",
        )
    return data


def google_map_results_to_dataframe(geocode_results: list) -> pd.DataFrame:
    """Transform geocode results into data-frame.

    Args:
        geocode_results: json results from google-maps API
    """
    geo_data = pd.DataFrame(geocode_results)

    # expand results and explode key columns
    geo_data = geo_data.explode("geocode_results", ignore_index=True).reset_index(
        drop=True
    )

    # flag single match and multiple match results
    geo_data["match_type"] = "single_match"
    geo_data.loc[
        geo_data.duplicated(["search_address"], keep=False), "match_type"
    ] = "multiple_matches"
    geo_data = expand_df(geo_data, ["geocode_results", "geometry", "location"]).dropna(
        how="all", axis=1
    )
    geo_data = geo_data.explode("types", ignore_index=True).reset_index(drop=True)
    return geo_data


def extract_address_types(
    geo_data: pd.DataFrame, components_of_interest: list
) -> pd.DataFrame:
    """Extract address components of interest into wide table format.

    Args:
        geo_data: json results from google-maps API
        components_of_interest: components to search of and retrieve in address components dictionary.
    """

    def wide_apply_address_types(data, value_type):
        data["__temp_id"] = data.reset_index(drop=True).index
        data_non_nan = data.dropna(subset=["address_components"]).copy()
        value_type_extract = (
            data_non_nan["address_components"]
            .dropna()
            .apply(
                lambda x: [y for y in x if "types" in y and value_type in y["types"]]
            )
        )
        value_type_extract = value_type_extract.apply(
            lambda x: x[0]["long_name"] if len(x) > 0 else np.nan
        )
        data_non_nan[value_type] = value_type_extract
        data_non_nan = data_non_nan[["__temp_id", value_type]]
        data = data.merge(
            data_non_nan,
            how="left",
            left_on="__temp_id",
            right_on="__temp_id",
            validate="1:1",
        )
        data = data.drop(columns="__temp_id")
        return data

    for component in components_of_interest:
        geo_data = wide_apply_address_types(geo_data, component)
    return geo_data


def add_main_types_category(
    data: pd.DataFrame,
    main_types: list,
    main_location_types: list,
    non_main_type_value: str = "other",
) -> pd.DataFrame:
    """Add ordered category values for types and location types.
    :param data:
    :param main_types:
    :param main_location_types:
    :param non_main_type_value:
    :return:
    """
    data["types_category"] = data["types"].where(
        data["types"].isin(main_types), non_main_type_value
    )  # all values in main types are kept, rest are replaced with other

    # make types category ordinal for sorting
    main_types_order = main_types + [non_main_type_value]
    data["types_category"] = pd.Categorical(
        data["types_category"],
        categories=main_types_order,
        ordered=True,
    )

    #  repeat for location type category
    data["location_type_category"] = data["location_type"].where(
        data["location_type"].isin(main_location_types), non_main_type_value
    )

    main_location_types_order = main_location_types + [non_main_type_value]

    data["location_type_category"] = pd.Categorical(
        data["location_type_category"],
        categories=main_location_types_order,
        ordered=True,
    )

    return data


def drop_duplicates_add_match_type(data: pd.DataFrame, column_order_sequence: list):
    """Drop duplicates based on column order sequence (keep first).

    Args:
        data: duplicates to be dropped
        column_order_sequence: columns to use to sort values.
    """
    data = data.sort_values(column_order_sequence)
    data = data.drop_duplicates(["search_address"], keep="first")

    data["no_match_found"] = (
        (data["types_category"] == "other")
        | (data["location_type_category"] == "other")
        | (data["location_type_category"].isna())
    )
    data["match_found"] = ~data["no_match_found"]
    data.loc[data["no_match_found"], "match_type"] = "no_match_found"
    return data


def transform_geocode_results(
    search_results: list,
) -> Dict[AnyStr, pd.DataFrame]:
    """Transform geocode results into expanded pandas data-frame with new features."""
    components_of_interest = [
        "subpremise",
        "premise",
        "establishment",
        "street_number",
        "route",
        "postal_code",
        "neighborhood",
        "administrative_area_level_1",
    ]

    main_types = ["premise", "subpremise", "establishment", "street_address"]
    main_location_types = ["ROOFTOP", "GEOMETRIC_CENTER"]
    column_order_sequence = ["location_type_category", "types_category"]

    data = google_map_results_to_dataframe(search_results)
    data = extract_address_types(data, components_of_interest)
    data = add_main_types_category(data, main_types, main_location_types)
    data = drop_duplicates_add_match_type(data, column_order_sequence)
    return data


def find_geocoded_addresses(df, address_column="address"):
    df = df[[address_column]].drop_duplicates()
    n = df.shape[0]
    logger.info(f"Addresses to geocode: {n}")
    return df[address_column].values


def merge_addresses(df, google_results):
    df = df.copy()
    # singapore_bounding_box = [1.1304753, 1.4504753, 103.6920359, 104.0120359]
    # google_results = google_results.loc[
    #     (google_results["lat"] >= singapore_bounding_box[0])
    #     & (google_results["lat"] <= singapore_bounding_box[1])
    #     & (google_results["lng"] >= singapore_bounding_box[2])
    #     & (google_results["lng"] <= singapore_bounding_box[3])
    # ]
    new_address_info = df.merge(
        google_results.rename(columns={"lat": "google_lat", "lng": "google_long"})[
            [
                "search_address",
                "formatted_address",
                "postal_code",
                "google_lat",
                "google_long",
            ]
        ],
        how="left",
        left_on="address",
        right_on="search_address",
        validate="m:1",
    )
    new_address_info[["lat", "lon"]] = new_address_info[
        ["google_lat", "google_long"]
    ].values
    return new_address_info


def geocode_unknown_addresses(df, google_api):
    df = df.copy()
    addresses_to_geocode = find_geocoded_addresses(df)
    if len(addresses_to_geocode) > 0:
        geocoded_addresses = geocode_addresses_via_google_maps(
            addresses_to_geocode, google_api
        )
        geocode_results = transform_geocode_results(geocoded_addresses)
        google_results = geocode_results
        df_geocoded = merge_addresses(df, google_results)
        df_geocoded["geocoded"] = True
    return df_geocoded


def add_geocoded_features(df):
    df_feature = df.assign(
        address=df[
            [
                "Site Address1",
                "Site Address2",
                "Site Address3",
                "Site Address4",
                "Site Address5",
                "Site Post Town",
                "Site Post Code",
            ]
        ]
        .fillna("")
        .astype(str)
        .agg(",".join, axis=1)
        .apply(lambda x: re.sub(r"(\W)(?=\1)", "", x))
    )
    return df_feature


def return_missing_coordinate_addresses(df):
    unknown_address = df.loc[df["latitude"].isna() | df["longitude"].isna()].copy()
    return unknown_address


def geocode_addresses(
    df, api_key, test=False, test_file="data/test/elias_test_geocoded.csv"
):
    if test is True:
        return pd.read_csv(test_file)
    df = df.assign(latitude=df["Site Latitude"], longitude=df["Site Longitude"])
    df["index"] = df.index
    df["geocoded"] = False
    df_missing_coordinate = return_missing_coordinate_addresses(df)
    df_missing_coordinate = add_geocoded_features(df_missing_coordinate)
    df_geocoded = geocode_unknown_addresses(df_missing_coordinate, api_key)
    df_geocoded = df_geocoded.assign(
        latitude=df_geocoded["google_lat"],
        longitude=df_geocoded["google_long"],
    )
    known_addresses = df.dropna(subset=["latitude"]).dropna(subset=["longitude"])
    df_full_geocoded = (
        pd.concat([known_addresses, df_geocoded[known_addresses.columns]])
        .sort_values("index")
        .reset_index(drop=True)
        .drop(columns=["index"])
    )
    return df_full_geocoded


if __name__ == "__main__":
    import toml

    secrets = toml.load(".streamlit/secrets.toml")
    gmaps_api = secrets["google_maps_api"]
    test_data = pd.read_excel("data/test/elias_test.xlsx")
    test_data = test_data.assign(
        latitude=test_data["Site Latitude"], longitude=test_data["Site Longitude"]
    )
    df_full_geocoded = geocode_addresses(test_data, api_key=gmaps_api)
    df_full_geocoded.to_csv("data/test/elias_test_geocoded.csv", index=False)
    pass
