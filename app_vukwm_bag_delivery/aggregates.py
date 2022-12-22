import numpy as np
import pandas as pd


def date_to_string(df):
    df = df.assign(
        collection_date=pd.to_datetime(df["Required Date"], dayfirst=True).dt.strftime(
            "%Y-%m-%d",
        )
    )
    return df


def get_day_summary(df):
    df_summary = (
        (
            df.assign(nan_reg=df["Registration No"].isna())
            .sort_values(["collection_date", "Registration No"])
            .groupby(["collection_date"])
            .agg(
                n_stops=("collection_date", "count"),
                n_unassigned=("nan_reg", "sum"),
                n_assigned_vehicles=("Registration No", "nunique"),
                assigned_vehicles=("Registration No", "unique"),
            )
        )
        .reset_index()
        .rename(
            columns={
                "collection_date": "Collection date",
                "n_stops": "Total number of tickets",
                "n_unassigned": "Tickets not assigned to a vehicle",
                "n_assigned_vehicles": "Number of assigned vehicles",
                "assigned_vehicles": "Assigned vehicles",
            }
        )
    )
    df_summary["Assigned vehicles"] = df_summary["Assigned vehicles"].apply(
        lambda x: [x_i for x_i in x if x_i is not np.nan]
    )
    order = [
        "Collection date",
        "Total number of tickets",
        "Tickets not assigned to a vehicle",
        "Fraction of tickets not assigned",
        "Number of assigned vehicles",
        "Assigned vehicles",
    ]
    df_summary["Fraction of tickets not assigned"] = (
        df_summary["Tickets not assigned to a vehicle"]
        / df_summary["Total number of tickets"]
    ).round(2)
    df_summary = df_summary[order]
    return df_summary


def filter_dates(df, max_fraction_cutoff, min_stop_cutoff):
    return (df["Fraction of stops not assigned"] <= max_fraction_cutoff) & (
        df["Total number of stops"] >= min_stop_cutoff
    )


def get_unique_filtered_dates(
    df,
    max_fraction_cutoff,
    min_stop_cutoff,
):
    return (
        df.loc[filter_dates(df, max_fraction_cutoff, min_stop_cutoff)][
            "Collection date"
        ]
        .sort_values()
        .unique()
    )


def get_area_num(df):
    return df.assign(
        tansport_area_num=df["Transport Area Code"].str[:-1].astype(int)
    ).sort_values(["collection_date", "Registration No", "tansport_area_num"])


def get_area_num_format(df):
    return df.assign(
        tansport_area_num=df["Transport Area Code"].str[:-1].astype(int)
    ).sort_values(["collection_date", "Registration No", "tansport_area_num"])


def calc_route_summary(df):
    df = get_area_num(df)
    route_summary = (
        df.groupby(["Registration No"])
        .agg(
            n_stops=("Registration No", "count"),
            assigned_zones=("tansport_area_num", "unique"),
        )
        .reset_index()
    ).rename(
        columns={
            "n_stops": "Total number of tickets",
            "assigned_zones": "Assigned zone numbers",
        }
    )
    return route_summary


def calc_route_product_summary(df):
    route_product_summary = (
        df.groupby(["Registration No", "Product Name"])
        .agg(
            n_stops=("Registration No", "count"),
            n_boxes=("Quantity", "sum"),
        )
        .reset_index()
    ).rename(
        columns={
            "n_stops": "Number of deliveries",
            "n_boxes": "Number of boxes",
        }
    )
    return route_product_summary


def calc_product_summary(df):
    route_product_summary = (
        df.groupby(["Product Name"])
        .agg(
            n_stops=("Product Name", "count"),
            n_boxes=("Total boxes", "sum"),
        )
        .reset_index()
    ).rename(
        columns={
            "n_stops": "Number of stops",
            "n_boxes": "Number of boxes",
        }
    )
    return route_product_summary


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
    df = df.iloc[:1]
    df["Product description"] = descriptions
    df["Ticket No"] = "; ".join(ticket_numbers)
    df["Total boxes"] = boxes
    df["Product Name"] = "; ".join(product_names)
    df["Quantity"] = "; ".join(quantity.astype(str))
    return df


def combine_orders(df):
    orders = date_to_string(df)
    orders = get_area_num(orders)
    orders["Transport area"] = "# " + orders["tansport_area_num"].astype(str).str.pad(
        2, fillchar="0"
    )
    orders_grouped = (
        orders.groupby(["Site Bk"])
        .apply(combine_product_name_quantity)
        .reset_index(drop=True)
    )
    return orders_grouped


if __name__ == "__main__":
    test_df = pd.read_excel("data/test/elias_test.xlsx")
    test_df = date_to_string(test_df)
    day_summary = get_day_summary(test_df)
    cut1 = 0.25
    cut2 = 25
    test_flag = filter_dates(day_summary, cut1, cut2)
    pass
