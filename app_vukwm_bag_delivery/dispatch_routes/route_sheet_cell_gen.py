import datetime

import numpy as np
import pandas as pd
import streamlit as st


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
    if page == 1:
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
                f"G:{get_row_number(stop_i, 0, page_i, start_row=7)}": stop_row[
                    "Visit sequence"
                ],
                f"G:{get_row_number(stop_i, 0, page_i, start_row=6)}": stop_row[
                    "Arrival time"
                ][:5],
                f"G:{get_row_number(stop_i, 0, page_i, start_row=5)}": stop_row[
                    "Delivery time window"
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
                "Delivery time window",
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


def generate_vehicle_sheet_info(route_totals, product_totals, route_id):
    product_total_route = product_totals.loc[product_totals["Vehicle Id"] == route_id]
    route_totals_route = route_totals.loc[route_totals["Vehicle Id"] == route_id].iloc[
        0
    ]
    route_cell = {
        "B:1": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "E:1": route_id,
        "B:4": route_id,
        "B:5": route_totals_route["Vehicle type"],
        "B:6": route_totals_route["Vehicle type"],
        "C:13": int(route_totals_route["Total stops"]),
    }

    if product_total_route.shape[0] > 9:
        st.warning(
            "The vehicle will deliver more than 9 different products. Only the first 9 will be written in the stock block."
        )
        st.write(product_total_route)
    for i, product_quant in product_total_route.reset_index(drop=True).iterrows():
        route_cell[f"G:{4 + i}"] = product_quant["Product Name"]
        route_cell[f"I:{4 + i}"] = product_quant["Product totals"]
    return route_cell


def generate_sheet_cells():
    assigned_jobs = st.session_state.data_07_reporting["assigned_jobs_download"].copy()
    route_totals = st.session_state.data_07_reporting[
        "assigned_jobs_download_total_stops"
    ]
    product_totals = st.session_state.data_07_reporting[
        "assigned_jobs_download_product_totals"
    ]
    assigned_jobs = assigned_jobs.assign(
        **{
            "Vehicle Id": assigned_jobs["Vehicle Id"]
            + " "
            + assigned_jobs["Trip Id"].astype(int).astype(str).str.zfill(2)
        }
    )
    route_ids = assigned_jobs["Vehicle Id"].unique()
    sheet_cells = {}
    for route_id in route_ids:
        assigned_route_jobs = assigned_jobs.loc[assigned_jobs["Vehicle Id"] == route_id]
        assigned_route_jobs = return_route_info(assigned_route_jobs)
        stop_info = return_stop_info(assigned_route_jobs)
        stop_cells = create_stop_cells(stop_info)
        job_cells = get_job_row_info(assigned_route_jobs)
        summary_info = generate_vehicle_sheet_info(
            route_totals, product_totals, route_id
        )
        sheet_cells[route_id] = {
            "job_cells": job_cells,
            "stop_cells": stop_cells,
            "summary_info": summary_info,
        }
    st.session_state.data_07_reporting["route_sheet_cell_values"] = sheet_cells
