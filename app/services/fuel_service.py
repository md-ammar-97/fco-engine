import re
import pandas as pd

from app.utils.dataframe_utils import clean_text, clean_upper, normalize_date_key, to_float


def process_fuel_prices(fuel_prices_df: pd.DataFrame) -> pd.DataFrame:
    df = fuel_prices_df.copy()
    for col in ["Site", "City", "State", "Prod", "Partner_Price", "Total_Cost"]:
        if col not in df.columns:
            df[col] = ""

    df["Site"] = df["Site"].map(clean_text)
    df["City"] = df["City"].map(clean_text)
    df["State"] = df["State"].map(clean_upper)
    df["Prod"] = df["Prod"].map(clean_upper)
    df["Partner_Price_Num"] = df["Partner_Price"].map(to_float)
    df["Total_Cost_Num"] = df["Total_Cost"].map(to_float)
    df["Visible_Flag"] = 1
    return df


def process_fuel_statement(fuel_df: pd.DataFrame, fuel_prices_df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    df = fuel_df.copy()
    for col in ["Tran_Date", "Unit", "Driver_Name", "Location_Name", "Pump_Location", "Pump_No", "City", "State", "Item", "Unit_Price", "Qty", "Amt", "Price", "Cost"]:
        if col not in df.columns:
            df[col] = ""

    df["Tran_Date_Key"] = df["Tran_Date"].map(normalize_date_key)
    df["Unit"] = df["Unit"].map(clean_text)
    df["City"] = df["City"].map(clean_text)
    df["State"] = df["State"].map(clean_upper)
    df["Item"] = df["Item"].map(clean_upper)

    df["Pump_No_Extracted"] = df.apply(
        lambda r: clean_text(r["Pump_No"]) or "".join(re.findall(r"\d+", clean_text(r["Pump_Location"]) or clean_text(r["Location_Name"]))),
        axis=1,
    )
    df["Qty_Num"] = df["Qty"].map(to_float).fillna(0.0)
    df["Amt_Num"] = df["Amt"].map(to_float)
    df["Unit_Price_Num"] = df["Unit_Price"].map(to_float)
    df["Price_Num"] = df["Price"].map(to_float)
    df["Cost_Num"] = df["Cost"].map(to_float)

    price_lookup = {}
    if not fuel_prices_df.empty:
        tmp = fuel_prices_df.copy()
        tmp["lookup_key"] = tmp["City"].str.upper() + "|" + tmp["State"].str.upper()
        price_lookup = {
            row["lookup_key"]: row["Partner_Price_Num"] if pd.notna(row["Partner_Price_Num"]) else row["Total_Cost_Num"]
            for _, row in tmp.iterrows()
        }

    def compute_price(row):
        if pd.notna(row["Price_Num"]):
            return row["Price_Num"]
        if pd.notna(row["Unit_Price_Num"]):
            return row["Unit_Price_Num"]
        return price_lookup.get(f"{str(row['City']).upper()}|{str(row['State']).upper()}")

    df["Matched_Price"] = df.apply(compute_price, axis=1)
    df["Matched_Cost"] = df.apply(
        lambda r: (float(r["Qty_Num"]) * float(r["Matched_Price"])) if pd.notna(r["Matched_Price"]) else r["Cost_Num"],
        axis=1,
    )
    df["Visible_Flag"] = 1
    df["Fuel_Key"] = df["Tran_Date_Key"] + "|" + df["Unit"].astype(str) + "|" + df["City"].str.upper() + "|" + df["State"].str.upper()
    df["Matched_Route"] = ""
    df["Assigned_Load_ID"] = ""
    df["Eligible_From_Load"] = ""
    df["Match_Status"] = "Pending"

    usable = df[df["Item"].str.contains("ULSD|DSL", na=False)].copy()
    total_qty = usable["Qty_Num"].sum()
    total_cost = usable["Matched_Cost"].fillna(0.0).sum()
    current_cpg = (total_cost / total_qty) if total_qty else 0.0
    return df, float(current_cpg)
