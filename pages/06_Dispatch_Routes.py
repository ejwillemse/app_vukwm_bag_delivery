import datetime
from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st

import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status
import app_vukwm_bag_delivery.util_views.side_bar_progress as side_bar_progress
from app_vukwm_bag_delivery.util_presenters.check_password import check_password


def set_page_config():
    st.set_page_config(
        layout="wide",
        page_title="Dispatch routes",
        initial_sidebar_state="expanded",
    )
    st.title("Dispatch and download routes")


if not check_password():
    st.warning("Please log-in to continue.")
    st.stop()  # App won't run anything after this line


def view_instructions():
    with st.expander("Instructions"):
        st.markdown(
            """
        Perform the following steps to edit vehicle information and select the vehicles to be routed. If no vehicles are selected, it is assumed that the entire fleet is available for routing.

        * Step 1: Inspect the vehicle information in the table.
        * Step 2: Edit the vehicle informaiton where required.
        * Step 3: Select active vehicles by clicking on the boxes next to the vehicle ID.
        * Step 4: Click on "Update" to load the vehicles.
        """
        )


def check_previous_steps_completed():
    stop = False
    if not return_session_status.check_intermediate_unassigned_jobs_loaded():
        st.warning("Job data not loaded during session. Please go back to `Home` page")
        stop = True  # App won't run anything after this line
    if not return_session_status.check_intermediate_unassigned_fleet_loaded():
        st.warning(
            "Vehicles have not yet been configured and selected. Please go to the `Select Vehicles` page."
        )
        stop = True
    if not return_session_status.check_route_generation_completed():
        st.warning(
            "Routes have not yet been generated. Please go to the `Generate Routes` page."
        )
        stop = True  # App won't run anything after this line
    if stop:
        st.stop()


def create_formatted_assigned_jobs():
    original_jobs = st.session_state.data_01_raw["raw_input"]
    unassigned_jobs = st.session_state.data_02_intermediate["unassigned_jobs"]
    if (
        "user_confirmed_removed_unassigned_stops"
        in st.session_state.data_02_intermediate
        and st.session_state.data_02_intermediate[
            "user_confirmed_removed_unassigned_stops"
        ].shape[0]
        > 0
    ):
        deselected_jobs = st.session_state.data_02_intermediate[
            "user_confirmed_removed_unassigned_stops"
        ]
    else:
        deselected_jobs = pd.DataFrame(columns=unassigned_jobs.columns)

    assigned_stops = st.session_state.data_07_reporting["assigned_stops"]

    to_scheduled_jobs = (
        original_jobs.loc[
            original_jobs["Ticket No"].isin(unassigned_jobs["Ticket No"])
            & (~original_jobs["Ticket No"].isin(deselected_jobs["Ticket No"]))
        ]
        .drop(columns=["Site Latitude", "Site Longitude"])
        .merge(unassigned_jobs[["Ticket No", "Site Latitude", "Site Longitude"]])
    )
    assigned_jobs = (
        to_scheduled_jobs.assign(
            **{"Site Bk": to_scheduled_jobs["Site Bk"].astype(str)}
        )
        .merge(
            assigned_stops[
                ["route_id", "vehicle_profile", "job_sequence", "arrival_time"]
            ]
            .rename(
                columns={
                    "stop_id": "Site Bk",
                    "route_id": "Vehicle Id",
                    "vehicle_profile": "Vehicle type",
                    "job_sequence": "Visit sequence",
                    "arrival_time": "Arrival time",
                }
            )
            .assign(
                **{
                    "Site Bk": assigned_stops["stop_id"].astype(str),
                    "Vehicle type": assigned_stops["vehicle_profile"].replace(
                        {"auto": "Van", "bicycle": "Bicycle"}
                    ),
                }
            ),
            how="left",
        )
        .sort_values(["Vehicle Id", "Visit sequence"])
        .reset_index(drop=True)
    )
    assigned_jobs = assigned_jobs.assign(
        **{
            "Visit sequence": (assigned_jobs["Visit sequence"] + 1)
            .fillna(0)
            .astype(int),
            "Vehicle Id": assigned_jobs["Vehicle Id"].fillna("Unassigned"),
        }
    )
    st.session_state.data_07_reporting["assigned_jobs_download"] = assigned_jobs.copy()


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


def show_assigned_routes():
    with st.expander(
        "Click here to view job lists with vehicle and sequence assignments"
    ):
        st.write(st.session_state.data_07_reporting["assigned_jobs_download"])


def download_results():
    assigned_jobs = st.session_state.data_07_reporting["assigned_jobs_download"]
    df_xlsx = to_excel(assigned_jobs)
    st.download_button(
        label="Download job list",
        data=df_xlsx,
        file_name=f"vukwm_bag_delivery_job_list_{datetime.datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss')}.xlsx",
    )


set_page_config()
side_bar_status = side_bar_progress.view_sidebar()
check_previous_steps_completed()
view_instructions()
create_formatted_assigned_jobs()
show_assigned_routes()
download_results()
side_bar_progress.update_side_bar(side_bar_status)

assigned_jobs = st.session_state.data_07_reporting["assigned_jobs_download"].copy()

st.write(assigned_jobs)

date = datetime.datetime.today().strftime("%d/%m/%Y %H:%M:%S")
st.write(date)

route_totals = (
    assigned_jobs.assign(
        **{
            "Vehicle Id": assigned_jobs["Vehicle Id"].fillna("Unassigned"),
            "Vehicle type": assigned_jobs["Vehicle type"].fillna(""),
        }
    )
    .groupby(["Vehicle Id", "Vehicle type"])
    .agg(
        **{
            "total_stops": ("Site Bk", "nunique"),
            "total_stops2": ("Visit sequence", "max"),
        }
    )
).reset_index()
st.write(route_totals)


route_product_totals = (
    assigned_jobs.assign(
        **{"Vehicle Id": assigned_jobs["Vehicle Id"].fillna("Unassigned")}
    )
    .groupby(["Vehicle Id", "Product Name"])
    .agg(**{"product_total": ("Quantity", "sum")})
).reset_index()
st.write(route_product_totals)


def calc_page_number(stop_i):
    return int(np.floor((stop_i - 4) / 5) + 2)


def page1_formula(stop_i, job_i, page, start_row):
    return 18 + start_row + job_i + (stop_i - 1) * 7


def page2_formula(stop_i, job_i, page, start_row):
    return 44 + start_row + job_i + (stop_i - 4) * 7 + 6 * (page - 2)


def create_job_id_cells(stop_i, job_i, page, row_formula):
    start_row = 2
    return f"A:{row_formula(stop_i, job_i, page, start_row)}"


def create_product_cells(stop_i, job_i, page, row_formula):
    start_row = 2
    return f"D:{row_formula(stop_i, job_i, page, start_row)}"


def create_product_quantity_cells(stop_i, job_i, page, row_formula):
    start_row = 2
    return f"E:{row_formula(stop_i, job_i, page, start_row)}"


def get_row_number(stop_i, job_i, page, start_row):
    if page == 0:
        return page1_formula(stop_i, job_i, page, start_row)
    else:
        return page2_formula(stop_i, job_i, page, start_row)


def create_job_cells(site_jobs, stop_i, page_i):
    cell_values = []
    if site_jobs.shape[0] > 6:
        st.warning(
            f"Site {site_jobs['Site Bk'].unique()[0]} has {site_jobs.shape[0]} jobs. Only six jobs can fit in the route sheet.."
        )
        st.write(site_jobs)
    for job_i, job_row in (
        site_jobs[["Ticket No", "Product Name", "Quantity"]].reset_index().iterrows()
    ):
        if job_i >= 6:
            break
        if page_i == 1:
            row_formula = page1_formula
        else:
            row_formula = page2_formula
        cell_values.append(
            {
                create_job_id_cells(stop_i, job_i, page_i, row_formula): job_row[
                    "Ticket No"
                ]
            }
        )
        cell_values.append(
            {
                create_product_cells(stop_i, job_i, page_i, row_formula): job_row[
                    "Product Name"
                ]
            }
        )
        cell_values.append(
            {
                create_product_quantity_cells(
                    stop_i, job_i, page_i, row_formula
                ): job_row["Quantity"]
            }
        )
    return cell_values


def group_types(df):
    grouped_tickets = (
        df.groupby(["Product Name"])
        .agg(**{"Ticket No": ("Ticket No", "unique"), "Quantity": ("Quantity", "sum")})
        .reset_index()
    )
    grouped_tickets = grouped_tickets.assign(
        **{"Ticket No": grouped_tickets["Ticket No"].apply(lambda x: ";".join(x))}
    )
    return grouped_tickets


def get_job_row_info(assigned_route_jobs):
    sites = assigned_route_jobs["Site Bk"].unique()
    job_cells = []
    for route_site in sites:
        site_jobs = assigned_route_jobs.loc[
            assigned_route_jobs["Site Bk"] == route_site
        ]
        stop_i = site_jobs["stop_number"].unique()[0]
        page_i = calc_page_number(stop_i)
        job_cells += create_job_cells(group_types(site_jobs), stop_i, page_i)
    return job_cells


def return_route_info(assigned_route_jobs):
    assigned_route_jobs = assigned_route_jobs.assign(
        sort_site=assigned_route_jobs["Site Name"].str.lower().str.strip()
    )
    assigned_route_jobs = assigned_route_jobs.sort_values(
        ["Visit sequence", "sort_site", "Site Bk"]
    ).assign(
        stop_number=assigned_route_jobs.groupby(
            ["Visit sequence", "sort_site", "Site Bk"]
        ).ngroup()
        + 1
    )
    return assigned_route_jobs


def create_stop_cells(stop_info):
    stop_cells = []
    for _, stop_row in stop_info.iterrows():
        stop_i = stop_row["stop_number"]
        page_i = calc_page_number(stop_i)
        stop_cells += [
            {
                f"job_number": stop_i,
                f"B:{get_row_number(stop_i, 0, page_i, start_row=1)}": stop_row[
                    "Site Name"
                ],
                f"B:{get_row_number(stop_i, 0, page_i, start_row=3)}": stop_row[
                    "Site Address"
                ],
                f"B:{get_row_number(stop_i, 0, page_i, start_row=4)}": stop_row[
                    "Site Post Town"
                ],
                f"B:{get_row_number(stop_i, 0, page_i, start_row=5)}": stop_row[
                    "Site Post Code"
                ],
                f"B:{get_row_number(stop_i, 0, page_i, start_row=6)}": stop_row[
                    "Transport Area Code"
                ],
                f"F:{get_row_number(stop_i, 0, page_i, start_row=1)}": stop_row[
                    "Notes"
                ],
                f"G:{get_row_number(stop_i, 0, page_i, start_row=6)}": stop_row[
                    "Visit sequence"
                ],
                f"G:{get_row_number(stop_i, 0, page_i, start_row=7)}": stop_row[
                    "Arrival time"
                ],
            }
        ]
    return stop_cells


def return_stop_info(assigned_jobs):
    stop_info = (
        assigned_jobs[
            [
                "Site Name",
                "Notes",
                "Arrival time",
                "Site Address1",
                "Site Address2",
                "Site Address3",
                "Site Post Town",
                "Site Post Code",
                "Transport Area Code",
                "Visit sequence",
                "stop_number",
            ]
        ]
        .drop_duplicates()
        .sort_values(["Notes"])
    )
    stop_info = (
        stop_info.assign(
            **{
                "Site Address": stop_info[
                    ["Site Address1", "Site Address2", "Site Address3"]
                ].apply(
                    lambda x: ", ".join([y for y in x if y is not pd.np.nan]), axis=1
                )
            }
        )
        .drop(columns=["Site Address1", "Site Address2", "Site Address3"])
        .fillna("")
    )
    return stop_info


def generate_sheet_cells():
    assigned_jobs = st.session_state.data_07_reporting["assigned_jobs_download"].copy()
    route_ids = assigned_jobs["Vehicle Id"].unique()
    sheet_cells = {}
    for route_id in route_ids:
        assigned_route_jobs = assigned_jobs.loc[assigned_jobs["Vehicle Id"] == route_id]
        assigned_route_jobs = return_route_info(assigned_route_jobs)
        stop_info = return_stop_info(assigned_route_jobs)
        stop_cells = create_stop_cells(stop_info)
        job_cells = get_job_row_info(assigned_route_jobs)
        sheet_cells[route_id] = {"job_cells": job_cells, "stop_cells": stop_cells}
    return sheet_cells


sheet_cells = generate_sheet_cells()
st.write(sheet_cells)
