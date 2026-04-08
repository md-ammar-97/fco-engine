import pandas as pd

from app.utils.dataframe_utils import clean_upper


def apply_clusters_to_loads(loads_df: pd.DataFrame, city_mapping_df: pd.DataFrame) -> pd.DataFrame:
    df = loads_df.copy()
    if city_mapping_df.empty:
        df["Start_Cluster"] = df["Pickup2"] + ", " + df["PSt"]
        df["End_Cluster"] = df["Delivery3"] + ", " + df["DSt"]
        df["Route_Key"] = df["Start_Cluster"] + " -> " + df["End_Cluster"]
        return df

    map_dict = {
        row["Map_Key"]: f"{row['Cluster City']}, {row['Cluster State']}"
        for _, row in city_mapping_df.iterrows()
    }

    df["Start_Cluster"] = df.apply(
        lambda r: map_dict.get(f"{str(r['Pickup2']).upper()}|{str(r['PSt']).upper()}", "Unmapped Start"),
        axis=1,
    )
    df["End_Cluster"] = df.apply(
        lambda r: map_dict.get(f"{str(r['Delivery3']).upper()}|{str(r['DSt']).upper()}", "Unmapped End"),
        axis=1,
    )
    df["Route_Key"] = df["Start_Cluster"] + " -> " + df["End_Cluster"]
    return df


def build_routes_and_results(loads_df: pd.DataFrame, current_cpg: float, decision_threshold: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = loads_df.copy()
    work["From"] = work["PSt"].map(clean_upper)
    work["To"] = work["DSt"].map(clean_upper)

    routes = (
        work.groupby(["From", "To"], dropna=False)
        .agg(
            **{
                "Total Count": ("Load_ID", "count"),
                "Eligible Count": ("Eligible", lambda s: int((s == "Yes").sum())),
                "Avg_Miles (Rough)": ("Miles_Num", "mean"),
            }
        )
        .reset_index()
    )
    routes["Total %"] = routes["Total Count"] / max(routes["Total Count"].sum(), 1)
    routes["Eligible %"] = routes["Eligible Count"] / routes["Eligible Count"].replace(0, pd.NA)
    routes["Eligible / Total"] = routes.apply(
        lambda r: (float(r["Eligible Count"]) / float(r["Total Count"])) if float(r["Total Count"]) else 0.0,
        axis=1,
    )
    routes["Total_Rough_Cost"] = routes["Eligible Count"] * routes["Avg_Miles (Rough)"].fillna(0.0) * float(current_cpg)
    routes["Decision"] = routes["Total_Rough_Cost"].apply(
        lambda x: "Considered" if float(x) >= float(decision_threshold) else "Ignored"
    )

    eligible = work[work["Eligible"] == "Yes"].copy()
    results = (
        eligible.groupby(["Route_Key", "Start_Cluster", "End_Cluster"], dropna=False)
        .agg(Miles=("Miles_Num", "mean"), Count=("Load_ID", "count"))
        .reset_index()
        .sort_values(["Count", "Miles", "Route_Key"], ascending=[False, False, True])
        .reset_index(drop=True)
    )
    results.insert(0, "Route", range(1, len(results) + 1))
    results.rename(columns={"Start_Cluster": "Start", "End_Cluster": "End"}, inplace=True)
    results["Stops"] = ""
    return routes, results[["Route", "Route_Key", "Start", "End", "Miles", "Count", "Stops"]]
