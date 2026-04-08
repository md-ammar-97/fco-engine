from pathlib import Path
from typing import Dict, Iterable

import pandas as pd

from app.core.logging import get_logger

logger = get_logger(__name__)


def discover_input_files(input_dir: Path) -> Dict[str, Path]:
    files = [p for p in input_dir.iterdir() if p.is_file()]
    if not files:
        raise FileNotFoundError(f"No input files found in {input_dir}")

    csv_files = [p for p in files if p.suffix.lower() == ".csv"]
    excel_files = [p for p in files if p.suffix.lower() in {".xlsx", ".xls"}]
    image_files = [p for p in files if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg"}]

    def pick_by_name(candidates, include_words):
        for p in candidates:
            lower = p.name.lower()
            if all(word in lower for word in include_words):
                return p
        return None

    loads_file = pick_by_name(excel_files + csv_files, ["load"])
    fuel_prices_file = pick_by_name(files, ["price"]) or pick_by_name(files, ["cp"])
    fuel_statement_file = pick_by_name(files, ["fuel"]) or pick_by_name(files, ["statement"])

    if loads_file is None and excel_files:
        loads_file = excel_files[0]

    remaining_excel = [p for p in excel_files if p != loads_file]
    if fuel_statement_file is None and remaining_excel:
        fuel_statement_file = remaining_excel[0]

    if fuel_prices_file is None and csv_files:
        fuel_prices_file = csv_files[0]

    axestrack_logo = pick_by_name(image_files, ["axestrack"]) or pick_by_name(image_files, ["setup"])
    client_logo = None
    for p in image_files:
        if p != axestrack_logo:
            client_logo = p
            break

    discovered = {
        "loads_file": loads_file,
        "fuel_statement_file": fuel_statement_file,
        "fuel_prices_file": fuel_prices_file,
        "axestrack_logo": axestrack_logo,
        "client_logo": client_logo,
    }

    missing = [k for k in ["loads_file", "fuel_statement_file", "fuel_prices_file"] if discovered[k] is None]
    if missing:
        raise FileNotFoundError(f"Missing required input file(s): {missing}")

    logger.info("Discovered input files: %s", {k: str(v) if v else None for k, v in discovered.items()})
    return discovered


def read_table(path: Path, sheet_name: str | None = None) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, sheet_name=sheet_name if sheet_name else 0)
    raise ValueError(f"Unsupported table format: {path}")
