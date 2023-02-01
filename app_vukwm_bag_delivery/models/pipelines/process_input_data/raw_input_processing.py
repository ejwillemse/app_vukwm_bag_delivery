"""
Process input data, simple pipeline, converts to data-time and does some high-level aggregation.
"""
import numpy as np
import pandas as pd
import streamlit as st

INPUT_DATE_COLUMNS_FORMAT = {
    "Created Date": "%%d/%m/%Y",
    "Required Date": "%%d/%m/%Y",
    "Scheduled Date": "%d/%m/%Y",
    "Completed Date": "%d/%m/%Y",
}
OUTPUT_DATE_FORMAT = "%Y-%m-%d"
UNASSIGNED_NAN_COLUMN = (
    "Completed Date"  # nan volumes in here indicates that it should be scheduled
)
AGGREGATION_IDs = ["Site Bk", "completed"]


def add_excel_time_dates(df, excel_df):
    excel_df = excel_df.assign(
        **{
            "Created Date": pd.to_datetime(
                excel_df["Created Date"], format="%d/%m/%Y"
            ).dt.strftime(OUTPUT_DATE_FORMAT),
            "Required Date": pd.to_datetime(
                excel_df["Required Date"], format="%d/%m/%Y"
            ).dt.strftime(OUTPUT_DATE_FORMAT),
            "Scheduled Date": pd.to_datetime(
                excel_df["Scheduled Date"], format="%d/%m/%Y"
            ).dt.strftime(OUTPUT_DATE_FORMAT),
            "Completed Date": pd.to_datetime(
                excel_df["Completed Date"], format="%d/%m/%Y"
            ).dt.strftime(OUTPUT_DATE_FORMAT),
        }
    )
    df[
        [
            "Required Date",
            "Created Date",
            "Scheduled Date",
            "Completed Date",
        ]
    ] = excel_df[
        [
            "Required Date",
            "Created Date",
            "Scheduled Date",
            "Completed Date",
        ]
    ]
    return df


def add_completed_flag(df):
    """Check if stops are completed or not, with those not completed used for routing"""
    return df.assign(completed=~df[UNASSIGNED_NAN_COLUMN].isna())


def extract_transport_number(df):
    """Extract transport area number, which is first part of transport area code.
    This is used to assign bicycle skills.
    """
    return df.assign(
        transport_area_number=df["Transport Area Code"].str[:-1].astype(int)
    )


def assign_bicycle_skills(df):
    return df.assign(
        skills=(df["transport_area_number"] == 2).replace(
            {True: "bicycle", False: np.nan}
        )
    )


def combine_product_name_quantity(df):
    """We combine all orders assigned to a site into one row, with key info concatinated with `';'`."""
    product_names = df["Product Name"].values
    quantity = df["Quantity"].values
    ticket_numbers = df["Ticket No"].values
    boxes = df["Quantity"].sum()
    descriptions = []
    for i in range(product_names.shape[0]):
        descriptions.append(f"{product_names[i]}: {quantity[i]}")
    descriptions = "\n".join(descriptions)
    df = df.iloc[:1]  # TODO: this stores key info, but also assigns the same date info
    df["Product description"] = descriptions
    df["Ticket No"] = "; ".join(ticket_numbers)
    df["Total boxes"] = boxes
    df["Product Name"] = "; ".join(product_names)
    df["Quantity"] = "; ".join(quantity.astype(str))
    return df


def filter_unassigned(df):
    """Return unassigned jobs for routing"""
    return df.loc[~df["completed"]]


def combine_orders(df):
    orders_grouped = (
        df.groupby(AGGREGATION_IDs)
        .apply(combine_product_name_quantity)
        .reset_index(drop=True)
    )
    return orders_grouped


def process_input_data(df, excel_df):
    df = df.copy()
    df = add_excel_time_dates(df, excel_df)
    df = add_completed_flag(df)
    df = filter_unassigned(df)
    df = extract_transport_number(df)
    df = assign_bicycle_skills(df)
    return df
