import math
import pandas as pd


def build_scenario_sheet(results_df: pd.DataFrame, start_fuel: float, mpg: float, tank_capacity: float, ending_reserve: float, unit_cost: float) -> pd.DataFrame:
    df = results_df.copy()
    if df.empty:
        return pd.DataFrame(columns=[
            "route_name", "status", "Start", "End", "route_miles", "start_fuel",
            "mpg", "tank_capacity", "ending_reserve", "recommended_stop_count",
            "recommended_total_gallons", "candidate_station_count",
            "routing_profile_used", "Total Cost"
        ])

    out = pd.DataFrame()
    out["route_name"] = df["Route_Key"]
    out["status"] = "heuristic"
    out["Start"] = df["Start"]
    out["End"] = df["End"]
    out["route_miles"] = df["Miles"].fillna(0.0).round(2)
    out["start_fuel"] = float(start_fuel)
    out["mpg"] = float(mpg)
    out["tank_capacity"] = float(tank_capacity)
    out["ending_reserve"] = float(ending_reserve)

    gallons_needed = out["route_miles"] / max(float(mpg), 0.1)
    net_required = gallons_needed + float(ending_reserve) - float(start_fuel)
    net_required = net_required.apply(lambda x: max(0.0, float(x)))
    purchasable_per_stop = max(float(tank_capacity) - float(start_fuel), 1.0)

    out["recommended_stop_count"] = net_required.apply(lambda x: 0 if x <= 0 else math.ceil(x / purchasable_per_stop))
    out["recommended_total_gallons"] = net_required.round(2)
    out["candidate_station_count"] = 0
    out["routing_profile_used"] = "pending_ors"
    out["Total Cost"] = (out["recommended_total_gallons"] * float(unit_cost)).round(2)
    return out
