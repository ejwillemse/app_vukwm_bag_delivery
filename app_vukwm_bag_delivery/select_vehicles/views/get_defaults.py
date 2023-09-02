import numpy as np
import pandas as pd
import streamlit as st


def gen_time_range(min=0, max=25):
    if max > 24:
        max = 24
        add_midnight = True
    else:
        add_midnight = False
    times = []
    for i in range(min, max):
        for j in [0, 1]:
            times.append(f"{str(i).zfill(2)}:{str(30 * j).zfill(2)}:00")
    if add_midnight is True:
        times.append("23:59:59")
    return times


VEHICLE_COLUMNS_DATA_TYPE = {
    "Selected": "bool",
    "Vehicle id": "string",
    "Driver name": "string",
    "Driver email": pd.CategoricalDtype(
        categories=st.secrets["driver_emails"],
        ordered=True,
    ),
    "Type": pd.CategoricalDtype(categories=["Van", "Bicycle"], ordered=True),
    "Capacity (kg)": "int64",
    "Max stops": "int64",
    "Depot": pd.CategoricalDtype(categories=["Mandela Way", "Soho", "Farm Street"], ordered=True),
    "Shift start time": pd.CategoricalDtype(categories=gen_time_range(), ordered=True),
    "Shift end time": pd.CategoricalDtype(categories=gen_time_range(), ordered=True),
    "Average TAT per delivery (min)": "float64",
    "Stock replenish duration (min)": "float64",
    "Dedicated transport zones": "string",
    "Cost (£) per km": "float64",
    "Cost (£) per hour": "float64",
    "lat": "float64",
    "lon": "float64",
}


def return_vehicle_default():
    if "vehicle_defaults" in st.session_state:
        return st.session_state["vehicle_defaults"].copy()
    selected = [False] * 6
    vehicle_ids = ["W01", "W02", "W03", "W04", "W05", "W06"]
    vehicle_type = ["Van", "Van", "Van", "Bicycle", "Van", "Van"]
    driver_name = [np.nan] * 6
    driver_email = st.secrets["driver_emails"] + [
        np.nan,
        np.nan,
    ]
    depot = [
        "Mandela Way",
        "Mandela Way",
        "Mandela Way",
        "Farm Street",
        "Mandela Way",
        "Mandela Way",
    ]
    lon = [-0.07962670, -0.07962670, -0.07962670, -0.14815635852522954, -0.07962670, -0.07962670]
    lat = [51.49175400, 51.49175400, 51.49175400, 51.50975907369495, 51.49175400, 51.49175400]
    capacity = [1000, 1000, 1000, 150, 1000, 1000]
    max_stops = [50, 50, 50, 50, 50, 50]
    dedicated_transport_zones = [None, None, None, "1,2,3,5", None, None]
    stock_replenish_duration = [30, 30, 30, 30, 30, 30]
    cost_per_km = [1, 1, 1, 0.5, 1, 1]
    cost_per_h = [10, 10, 10, 10, 10, 10]
    shift_start_time = ["09:00:00"] * 6
    shift_end_time = ["17:00:00"] * 6
    ave_duration = [5] * 6

    vehicle_df = pd.DataFrame(
        {
            "Selected": selected,
            "Vehicle id": vehicle_ids,
            "Driver name": driver_name,
            "Driver email": driver_email,
            "Type": vehicle_type,
            "Capacity (kg)": capacity,
            "Max stops": max_stops,
            "Depot": depot,
            "Shift start time": shift_start_time,
            "Shift end time": shift_end_time,
            "Average TAT per delivery (min)": ave_duration,
            "Dedicated transport zones": dedicated_transport_zones,
            "Stock replenish duration (min)": stock_replenish_duration,
            "Cost (£) per km": cost_per_km,
            "Cost (£) per hour": cost_per_h,
            "lat": lat,
            "lon": lon,
        }
    ).astype(VEHICLE_COLUMNS_DATA_TYPE)
    vehicle_df = vehicle_df.iloc[:4]
    return vehicle_df
