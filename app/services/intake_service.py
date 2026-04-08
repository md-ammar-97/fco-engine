from pathlib import Path
from typing import Any, Dict

import pandas as pd

from app.core.logging import get_logger
from app.utils.file_utils import discover_input_files, read_table
from app.utils.validation_utils import parse_mapping_json

logger = get_logger(__name__)


def standardize_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    out = pd.DataFrame()
    for canonical, source in mapping.items():
        if source in df.columns:
            out[canonical] = df[source]
        else:
            out[canonical] = ""
    return out


def load_run_inputs(input_dir: Path, config: Dict[str, Any], mappings: Dict[str, Any]) -> Dict[str, Any]:
    files = discover_input_files(input_dir)

    loads_sheet_name = str(config.get("loads_sheet_name") or "").strip() or None
    fuel_statement_sheet_name = str(config.get("fuel_statement_sheet_name") or "").strip() or None
    fuel_prices_sheet_name = str(config.get("fuel_prices_sheet_name") or "").strip() or None

    loads_raw = read_table(files["loads_file"], loads_sheet_name)
    fuel_statement_raw = read_table(files["fuel_statement_file"], fuel_statement_sheet_name)
    fuel_prices_raw = read_table(files["fuel_prices_file"], fuel_prices_sheet_name)

    loads_mapping = parse_mapping_json(mappings.get("loads"), "Loads")
    fuel_statement_mapping = parse_mapping_json(mappings.get("fuel_statement"), "Fuel Statement")
    fuel_prices_mapping = parse_mapping_json(mappings.get("fuel_prices"), "Fuel Prices")

    return {
        "files": files,
        "loads_raw": loads_raw,
        "fuel_statement_raw": fuel_statement_raw,
        "fuel_prices_raw": fuel_prices_raw,
        "loads": standardize_columns(loads_raw, loads_mapping),
        "fuel_statement": standardize_columns(fuel_statement_raw, fuel_statement_mapping),
        "fuel_prices": standardize_columns(fuel_prices_raw, fuel_prices_mapping),
    }
