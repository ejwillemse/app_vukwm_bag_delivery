import pandas as pd


def route_summary(assigned_stops):
    return assigned_stops.groupby(["route_id"]).agg(
        start_time=("arrival_time", "min"),
        end_time=("departure_time", "max"),
        total_distance__m=("travel_distance_to_stop_meters", "sum"),
    )


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
    print(route_summary(assigned_stops))
