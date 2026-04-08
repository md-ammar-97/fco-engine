from typing import Any, Dict, Optional

from pydantic import BaseModel


class CallbackManifest(BaseModel):
    success: bool
    run_id: str
    workbook_path: Optional[str] = None
    pdf_path: Optional[str] = None
    google_sheet_url: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None
    exceptions: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
