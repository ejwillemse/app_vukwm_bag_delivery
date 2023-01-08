"""
Process input data, simple pipeline, converts to data-time and does some high-level aggregation.
"""

import pandas as pd

INPUT_DATE_COLUMNS_FORMAT = {
    "Created Date": "%Y-%d-%m",
    "Required Date": "%Y-%d-%m",
    "Scheduled Date": "%d/%m/%Y",
    "Completed Date": "%d/%m/%Y",
}
OUTPUT_DATE_FORMAT = "%Y-%m-%d"
UNASSIGNED_NAN_COLUMN = (
    "Completed Date"  # nan volumes in here indicates that it should be scheduled
)
AGGREGATION_IDs = ["Site Bk", "completed"]


def date_to_string(df):
    """Convert all date columns to correct string formatting"""
    for date_column in INPUT_DATE_COLUMNS_FORMAT:
        df = df.assign(
            **{
                date_column: lambda x: pd.to_datetime(
                    df[date_column], format=INPUT_DATE_COLUMNS_FORMAT[date_column]
                ).dt.strftime(OUTPUT_DATE_FORMAT)
            }
        )
    return df


def add_completed_flag(df):
    """Check if stops are completed or not, with those not completed used for routing"""
    return df.assign(completed=~df[UNASSIGNED_NAN_COLUMN].isna())


def extract_transport_number(df):
    """Extract transport area number, which is first part of transport area code.
    This is used to assign bicycle skills.
    """
    return df.assign(
        tansport_area_number=df["Transport Area Code"].str[:-1].astype(int)
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


def combine_orders(df):
    orders_grouped = (
        df.groupby(AGGREGATION_IDs)
        .apply(combine_product_name_quantity)
        .reset_index(drop=True)
    )
    return orders_grouped


def process_input_data(df):
    df = df.copy()
    df = date_to_string(df)
    df = add_completed_flag(df)
    df = extract_transport_number(df)
    return df
