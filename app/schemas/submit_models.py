from typing import Any, Dict

from pydantic import BaseModel


class SubmitRunRequest(BaseModel):
    run_id: str
    input_dir: str
    output_dir: str
    callback_url: str
    callback_token: str
    config: Dict[str, Any]
    mappings: Dict[str, Any]
