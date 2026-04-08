from pathlib import Path
from typing import Dict

import pandas as pd


def write_workbook(output_path: Path, sheets: Dict[str, pd.DataFrame]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        for sheet_name, df in sheets.items():
            safe_name = sheet_name[:31]
            if df is None:
                pd.DataFrame().to_excel(writer, sheet_name=safe_name, index=False)
            else:
                df.to_excel(writer, sheet_name=safe_name, index=False)
    return output_path
