import pandas as pd

from app.utils.dataframe_utils import clean_text, clean_upper, normalize_date_key, to_float


def process_loads(loads_df: pd.DataFrame, eligibility_miles: float = 1000.0) -> pd.DataFrame:
    df = loads_df.copy()

    for col in ["Pickup2", "PSt", "Delivery3", "DSt", "Truck1", "Trailer1", "Truck2", "Trailer2", "Pickup", "Delivery"]:
        if col not in df.columns:
            df[col] = ""

    df["Pickup2"] = df["Pickup2"].map(clean_text)
    df["PSt"] = df["PSt"].map(clean_upper)
    df["Delivery3"] = df["Delivery3"].map(clean_text)
    df["DSt"] = df["DSt"].map(clean_upper)

    miles_col = "Miles" if "Miles" in df.columns else "Miles/Units"
    if miles_col not in df.columns:
        df[miles_col] = ""

    df["Miles_Num"] = df[miles_col].map(to_float).fillna(0.0)
    df["Eligible"] = df["Miles_Num"].apply(lambda x: "Yes" if x >= float(eligibility_miles) else "No")
    df["Visible_Flag"] = 1

    df["Pickup_Date_Key"] = df["Pickup"].map(normalize_date_key) if "Pickup" in df.columns else ""
    df["Delivery_Date_Key"] = df["Delivery"].map(normalize_date_key) if "Delivery" in df.columns else ""

    df["Load_ID"] = [f"LOAD_{i:06d}" for i in range(1, len(df) + 1)]
    df["Route_Key"] = ""
    df["Start_Cluster"] = ""
    df["End_Cluster"] = ""
    return df
