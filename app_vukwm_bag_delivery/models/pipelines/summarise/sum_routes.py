import pandas as pd


def route_summary(assigned_stops):
    return (
        assigned_stops.assign(
            job_flag=assigned_stops["location_type"] == "JOB",
        )
        .groupby(["route_id", "profile"])
        .agg(
            start_time=("arrival_time", "min"),
            end_time=("departure_time", "max"),
            total_distance__meters=("travel_distance_to_stop__meters", "sum"),
            total_duration__seconds=("duration_cum__seconds", "max"),
            waiting_duration__seconds=("waiting_duration__seconds", "sum"),
            average_speed__kmh=("travel_speed__kmh", "mean"),
            stops=("job_flag", "sum"),
            demand=("demand", "sum"),
        )
    ).reset_index()


if __name__ == "__main__":

    unassigned_stops = pd.read_csv(
        "data/local_test/03_Generate_Routes/unassigned_stops.csv",
        dtype={"stop_id": str},
    )
    unassigned_routes_test = pd.read_csv(
        "data/local_test/03_Generate_Routes/unassigned_routes.csv",
        dtype={"route_id": str},
    )

    assigned_stops = pd.read_csv(
        "data/local_test/03_Generate_Routes/assigned_stops.csv"
    )
    print(assigned_stops.columns)
    assigned_stops_sum = route_summary(assigned_stops)
