import pandas as pd


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
    "Vehicle id": "string",
    "Type": pd.CategoricalDtype(categories=["Van", "Bicycle"], ordered=True),
    "Capacity (kg)": "int64",
    "Max stops": "int64",
    "Depot": pd.CategoricalDtype(categories=["Mandela Way", "Soho"], ordered=True),
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
    vehicle_ids = ["W01", "W02", "W03", "W04", "W05", "W06"]
    vehicle_type = ["Van", "Van", "Van", "Bicycle", "Van", "Van"]
    depot = [
        "Mandela Way",
        "Mandela Way",
        "Mandela Way",
        "Soho",
        "Mandela Way",
        "Mandela Way",
    ]
    lon = [-0.07962670, -0.07962670, -0.07962670, -0.13748230, -0.07962670, -0.07962670]
    lat = [51.49175400, 51.49175400, 51.49175400, 51.51358620, 51.49175400, 51.49175400]
    capacity = [1000, 1000, 1000, 150, 1000, 1000]
    max_stops = [40, 40, 40, 50, 40, 40]
    dedicated_transport_zones = [None, None, None, "2", None, None]
    stock_replenish_duration = [30, 30, 30, 30, 30, 30]
    cost_per_km = [1, 1, 1, 0.5, 1, 1]
    cost_per_h = [10, 10, 10, 10, 10, 10]
    shift_start_time = ["09:00:00"] * 6
    shift_end_time = ["17:00:00"] * 6
    ave_duration = [5] * 6

    vehicle_df = pd.DataFrame(
        {
            "Vehicle id": vehicle_ids,
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
    return vehicle_df
