"""
Addapted from https://blog.streamlit.io/auto-generate-a-dataframe-filtering-ui-in-streamlit-with-filter_dataframe/
"""

import pandas as pd
import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)


def filter_dataframe(
    df: pd.DataFrame,
    base=st,
    special_categorical=None,
    exclude_columns=None,
    include_columns=None,
    prefilter=None,
    key="",
) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """

    modify = base.checkbox("Add filters", value=True, key=key + "__modify")

    if not modify:
        return df

    keepnan = False
    # base.checkbox(
    #     "Keep empty values",
    #     value=False,
    #     help="Empty string values are replacend by `NaN`, and empty numeric values are replaced by `0`",
    #     key=key + "__keepnan",
    # )

    use_cols = df.columns
    if exclude_columns:
        use_cols = [col for col in df.columns if col not in exclude_columns]
    elif include_columns is not None:
        use_cols = [col for col in df.columns if col in include_columns]

    if special_categorical is None:
        special_categorical = []

    df = df.copy()
    df_search = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    # for col in use_cols:
    #     if is_object_dtype(df[col]):
    #         try:
    #             df[col] = pd.to_datetime(df[col])
    #         except Exception:
    #             pass

    #     if is_datetime64_any_dtype(df[col]):
    #         df[col] = df[col].dt.tz_localize(None)

    modification_container = base.container()

    with modification_container:
        to_filter_columns = base.multiselect(
            "Filter data on",
            use_cols,
            default=prefilter,
            key=key + "__to_filter_columns",
        )
        for column in to_filter_columns:
            left, right = base.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if (
                is_categorical_dtype(df[column])
                or df[column].nunique() < 10
                or column in special_categorical
            ):
                if keepnan and not is_categorical_dtype(df[column]):
                    df_search = df_search.assign(
                        **{column: df_search[column].fillna("NaN")}
                    )
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df_search[column].unique(),
                    default=list(df_search[column].unique()),
                    key=key + "__" + column,
                )
                df = df[df_search[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                if keepnan:
                    df_search = df_search.assign(
                        **{column: df_search[column].fillna(0)}
                    )
                _min = float(df_search[column].min())
                _max = float(df_search[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                    key=key + "__" + column,
                )
                df = df[df_search[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                    key=key + "__" + column,
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                    key=key + "__" + column,
                )
                if keepnan:
                    df_search = df_search.assign(
                        **{column: df_search[column].fillna("NaN")}
                    )
                if user_text_input:
                    df = df[
                        df_search[column]
                        .astype(str)
                        .str.lower()
                        .str.contains(user_text_input.lower())
                    ]

    return df


def filter_df_widget(
    data,
    special_categorical=None,
    exclude_columns=None,
    include_columns=None,
    base=st,
    key="",
    prefilter=None,
):
    if prefilter is None:
        prefilter = ["Site Name"]
    data_filtered = filter_dataframe(
        data,
        base=base,
        special_categorical=special_categorical,
        exclude_columns=exclude_columns,
        include_columns=include_columns,
        key=key,
        prefilter=prefilter,
    )
    return data_filtered
