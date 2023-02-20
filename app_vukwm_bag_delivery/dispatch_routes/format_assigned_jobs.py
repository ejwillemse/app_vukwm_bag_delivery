import pandas as pd
import streamlit as st

import app_vukwm_bag_delivery.generate_routes.presenters.extract_high_level_summary as extract_high_level_summary
import app_vukwm_bag_delivery.util_views.return_session_status as return_session_status


def create_formatted_assigned_jobs():

    locations = st.session_state.data_03_primary["locations"]

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
                [
                    "route_id",
                    "trip_id",
                    "vehicle_profile",
                    "job_sequence",
                    "arrival_time",
                ]
            ]
            .rename(
                columns={
                    "stop_id": "Site Bk",
                    "route_id": "Vehicle Id",
                    "trip_id": "Trip Id",
                    "vehicle_profile": "Vehicle type",
                    "job_sequence": "Visit sequence",
                    "arrival_time": "Arrival time",
                }
            )
            .assign(
                **{
                    "Site Bk": assigned_stops["stop_id"].astype(str),
                    "Vehicle type": assigned_stops["vehicle_profile"].replace(
                        {"auto": "Van", "bicycle": "Bicycle"},
                    ),
                }
            ),
            how="left",
        )
        .sort_values(["Vehicle Id", "Visit sequence"])
        .reset_index(drop=True)
        .merge(
            locations.assign(**{"Site Bk": locations["stop_id"].astype(str)})[
                ["Site Bk", "time_window_start", "time_window_end"]
            ],
            how="left",
        )
    )
    assigned_jobs = assigned_jobs.assign(
        **{
            "Delivery time window": assigned_jobs["time_window_start"].str[:5]
            + " - "
            + assigned_jobs["time_window_end"].str[:5]
        }
    ).drop(columns=["time_window_start", "time_window_end"])
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
    assigned_jobs = assigned_jobs.assign(
        **{
            "Vehicle Id": assigned_jobs["Vehicle Id"].fillna("Unassigned")
            + " "
            + assigned_jobs["Trip Id"].astype(int).astype(str).str.zfill(2)
        }
    )
    assigned_jobs_sum = (
        assigned_jobs.assign(
            **{
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
