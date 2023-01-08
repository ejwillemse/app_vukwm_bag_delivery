"""
Convert input data into waste labs data schema
"""
import numpy as np

UNASSIGNED_STOPS_COLUMN_MAPPING = [
    {"new_column": "stop_id", "old_column": "Ticket No"},
    {"new_column": "latitude", "old_column": "Site Latitude"},
    {"new_column": "longitude", "old_column": "Site Longitude"},
    {"new_column": "demand", "old_column": "Total boxes", "default": 0},
    {"new_column": "skills", "old_column": "skills", "default": np.nan},
    {"new_column": "duration", "old_column": "duration", "default": 5 * 60},
    {
        "new_column": "time_window_start",
        "old_column": "time_window_start",
        "default": "09:00:00",
    },
    {
        "new_column": "time_window_end",
        "old_column": "time_window_end",
        "default": "16:00:00",
    },
]


def unassigned_stops_convert(df, drop_columns=True):
    columns = df.columns
    new_columns = []
    for column_mapping in UNASSIGNED_STOPS_COLUMN_MAPPING:
        if column_mapping["old_column"] not in columns:
            df[column_mapping["new_column"]] = column_mapping["default"]
        else:
            df[column_mapping["new_column"]] = df[column_mapping["old_column"]]
        new_columns.append(column_mapping["new_column"])
    if drop_columns:
        df = df[new_columns]
    return df
