import pandas as pd
import streamlit as st


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


def get_route_totals():
    assigned_jobs = st.session_state.data_07_reporting["assigned_jobs_download"]
    assigned_jobs_sum = (
        assigned_jobs.assign(
            **{
                "Vehicle Id": assigned_jobs["Vehicle Id"].fillna("Unassigned"),
                "Vehicle type": assigned_jobs["Vehicle type"].fillna(""),
            }
        )
        .groupby(["Vehicle Id", "Vehicle type"])
        .agg(
            **{
                "Total stops": ("Site Bk", "nunique"),
            }
        )
    ).reset_index()

    route_product_totals = (
        assigned_jobs.assign(
            **{"Vehicle Id": assigned_jobs["Vehicle Id"].fillna("Unassigned")}
        )
        .groupby(["Vehicle Id", "Product Name"])
        .agg(**{"Product totals": ("Quantity", "sum")})
    ).reset_index()

    st.session_state.data_07_reporting[
        "assigned_jobs_download_total_stops"
    ] = assigned_jobs_sum.copy()

    st.session_state.data_07_reporting[
        "assigned_jobs_download_product_totals"
    ] = route_product_totals.copy()
