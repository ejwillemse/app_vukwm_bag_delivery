"""
Add time window data
"""


def extract_short_name_key(df):
    return (
        df["Site Name"]
        .apply(lambda x: x.replace(".", ""))
        .apply(lambda x: x[: x.rfind("[")] if "[" in x else x)
        .apply(lambda x: x[: x.rfind("(")] if "(" in x else x)
        .str.strip()
        .str.lower()
        .replace("caffe concert", "caffe concerto")
        .replace("leon's carnaby", "leon's")
        .replace("leon's waterloo bridge - veolia es uk ltd", "leon's")
    )


def merge_time_window_info(df, df_time_window):
    df = df.assign(**{"Customer short name": extract_short_name_key(df)})
    df = df.merge(
        df_time_window,
        how="left",
        left_on="Customer short name",
        right_on="Customer short name",
    )
    return df
