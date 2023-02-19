import pandas as pd


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
    dedicated_transport_zones = [None, None, None, "2", None, None]
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
            "Depot": depot,
            "Shift start time": shift_start_time,
            "Shift end time": shift_end_time,
            "Average TAT per delivery (min)": ave_duration,
            "Dedicated transport zones": dedicated_transport_zones,
            "Cost (£) per km": cost_per_km,
            "Cost (£) per hour": cost_per_h,
            "lat": lat,
            "lon": lon,
        }
    )
    return vehicle_df
