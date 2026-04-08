from pathlib import Path

import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from sklearn.cluster import DBSCAN

from app.core.config import settings
from app.core.logging import get_logger
from app.utils.cache_utils import load_json_file, save_json_file
from app.utils.dataframe_utils import clean_text, clean_upper

logger = get_logger(__name__)

EARTH_RADIUS_MILES = 3958.8


def _cache_path() -> Path:
    return Path(settings.cache_dir) / "geocode_cache.json"


def _geocode_pairs(pairs: pd.DataFrame) -> pd.DataFrame:
    cache = load_json_file(_cache_path(), {})
    geolocator = Nominatim(user_agent="fco_engine")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1)

    latitudes = []
    longitudes = []

    for _, row in pairs.iterrows():
        key = f"{row['City'].upper()}|{row['State'].upper()}"
        cached = cache.get(key)
        if cached:
            latitudes.append(cached.get("lat"))
            longitudes.append(cached.get("lon"))
            continue

        query = f"{row['City']}, {row['State']}, USA"
        lat = None
        lon = None
        try:
            location = geocode(query)
            if location:
                lat = float(location.latitude)
                lon = float(location.longitude)
        except Exception as exc:
            logger.warning("Geocode failed for %s: %s", query, exc)

        cache[key] = {"lat": lat, "lon": lon}
        latitudes.append(lat)
        longitudes.append(lon)

    save_json_file(_cache_path(), cache)
    pairs["Latitude"] = latitudes
    pairs["Longitude"] = longitudes
    return pairs


def build_city_mapping(loads_df: pd.DataFrame) -> pd.DataFrame:
    pickups = loads_df[["Pickup2", "PSt"]].rename(columns={"Pickup2": "City", "PSt": "State"})
    deliveries = loads_df[["Delivery3", "DSt"]].rename(columns={"Delivery3": "City", "DSt": "State"})
    combined = pd.concat([pickups, deliveries], ignore_index=True)
    combined["City"] = combined["City"].map(clean_text)
    combined["State"] = combined["State"].map(clean_upper)
    combined = combined[(combined["City"] != "") & (combined["State"] != "")]
    counts = combined.value_counts(["City", "State"]).reset_index(name="Count")

    if counts.empty:
        return pd.DataFrame(columns=["Cluster No.", "City", "State", "Cluster City", "Cluster State", "Map_Key", "Visible_Flag"])

    counts = _geocode_pairs(counts)

    resolved = counts.dropna(subset=["Latitude", "Longitude"]).copy()
    unresolved = counts[counts["Latitude"].isna() | counts["Longitude"].isna()].copy()

    rows = []
    if not resolved.empty:
        coords = np.radians(resolved[["Latitude", "Longitude"]].astype(float).values)
        eps = 50.0 / EARTH_RADIUS_MILES
        model = DBSCAN(eps=eps, min_samples=1, algorithm="ball_tree", metric="haversine")
        resolved["Cluster_ID"] = model.fit_predict(coords)
        cluster_ids = sorted(resolved["Cluster_ID"].unique())
        cluster_map = {cid: i + 1 for i, cid in enumerate(cluster_ids)}
        resolved["Cluster No."] = resolved["Cluster_ID"].map(cluster_map)

        for cluster_no, group in resolved.groupby("Cluster No."):
            hub = group.sort_values(["Count", "City", "State"], ascending=[False, True, True]).iloc[0]
            for _, row in group.iterrows():
                rows.append({
                    "Cluster No.": cluster_no,
                    "City": row["City"],
                    "State": row["State"],
                    "Cluster City": hub["City"],
                    "Cluster State": hub["State"],
                    "Map_Key": f"{row['City'].upper()}|{row['State'].upper()}",
                    "Visible_Flag": 1,
                })

    for _, row in unresolved.iterrows():
        rows.append({
            "Cluster No.": "Unresolved",
            "City": row["City"],
            "State": row["State"],
            "Cluster City": row["City"],
            "Cluster State": row["State"],
            "Map_Key": f"{row['City'].upper()}|{row['State'].upper()}",
            "Visible_Flag": 1,
        })

    return pd.DataFrame(rows)
