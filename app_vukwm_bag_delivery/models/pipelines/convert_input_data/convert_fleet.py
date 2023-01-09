"""
Convert fleet data into standard data model
"""

UNASSIGNED_ROUTE_COLUMN_MAPPING = [
    {"new_column": "route_id", "old_column": "Vehicle id"},
    {"new_column": "profile", "old_column": "Type"},
    {"new_column": "depot_id", "old_column": "Depot"},
    {"new_column": "skills", "old_column": "Dedicated transport zones"},
    {"new_column": "latitude", "old_column": "lat"},
    {"new_column": "longitude", "old_column": "lon"},
    {"new_column": "capacity", "old_column": "Capacity (#boxes)"},
    {
        "new_column": "time_window_start",
        "old_column": "Shift start time",
        "default": "09:00:00",
    },
    {
        "new_column": "time_window_end",
        "old_column": "Shift end time",
        "default": "17:00:00",
    },
]
PROFILE_MAPPING = {"Van": "auto", "Bicycle": "bicycle"}


def unassigned_route_convert(df, drop_columns=True):
    columns = df.columns
    new_columns = []
    for column_mapping in UNASSIGNED_ROUTE_COLUMN_MAPPING:
        if column_mapping["old_column"] not in columns:
            df[column_mapping["new_column"]] = column_mapping["default"]
        else:
            df[column_mapping["new_column"]] = df[column_mapping["old_column"]]
        new_columns.append(column_mapping["new_column"])
    if drop_columns:
        df = df[new_columns]
    return df


def convert_fleet(df):
    df = df.copy()
    df = unassigned_route_convert(df)
    df = df.assign(profile=df["profile"].replace(PROFILE_MAPPING))
    return df
