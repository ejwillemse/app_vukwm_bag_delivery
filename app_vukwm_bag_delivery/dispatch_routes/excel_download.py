import datetime
from io import BytesIO

import pandas as pd
import streamlit as st

column_mappings = [
    "TicketNo",
    "CustomerBk",
    "SiteBk",
    "SiteName",
    "TransportAreaCode",
    "ProductName",
    "Quantity",
    "CreatedDate",
    "RequiredDate",
    "Notes",
    "onhold",
    "ScheduleID",
    "ScheduledDate",
    "CompletedDate",
    "RegistrationNo",
    "SiteAddress1",
    "SiteAddress2",
    "SiteAddress3",
    "SiteAddress4",
    "SiteAddress5",
    "SitePostTown",
    "SitePostCode",
    "SiteLatitude",
    "SiteLongitude",
    "RouteNumber",
    "RouteOrder",
    "Round",
    "RoundLogin",
    "Driver",
]

renames = {
    "Driver email": "RoundLogin",
    "Driver name": "Driver",
    "Vehicle Id": "Round",
    "Trip Id": "RouteNumber",
    "Visit sequence": "RouteOrder",
}


def add_driver_info(df):
    unassigned_routes = st.session_state["data_02_intermediate"][
        "unassigned_routes"
    ].rename(columns={"Vehicle id": "Vehicle Id"})
    df = df.merge(unassigned_routes, on="Vehicle Id", how="left", validate="m:1")
    return df


def format_data(df):
    df = df.rename(columns=renames)
    df.columns = [x.replace(" ", "") for x in df.columns]
    df = df[column_mappings]
    return df


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name="Sheet1")
    for column in df:
        column_width = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets["Sheet1"].set_column(col_idx, col_idx, column_width)
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def drop_unassigned(df):
    df = df.loc[df["Vehicle Id"] != "Unassigned"]
    df = df.loc[~df["Trip Id"].isna()]
    return df


def format_routes():
    assigned_jobs = st.session_state.data_07_reporting["assigned_jobs_download"]
    assigned_jobs = drop_unassigned(assigned_jobs)
    assigned_jobs = add_driver_info(assigned_jobs)
    assigned_jobs = format_data(assigned_jobs)
    return assigned_jobs


def download_results():
    assigned_jobs = format_routes()
    df_xlsx = to_excel(assigned_jobs)
    return df_xlsx
