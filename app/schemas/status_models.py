from pydantic import BaseModel


class RunStatusResponse(BaseModel):
    run_id: str
    status: str
    error_message: str | None = None
    created_at: str
    updated_at: str
