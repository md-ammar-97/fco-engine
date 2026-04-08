from typing import Any, Dict, Optional

from pydantic import BaseModel


class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    error_message: Optional[str] = None
    created_at: str
    updated_at: str
    callback_url: Optional[str] = None
    input_dir: Optional[str] = None
    output_dir: Optional[str] = None
    manifest: Optional[Dict[str, Any]] = None
