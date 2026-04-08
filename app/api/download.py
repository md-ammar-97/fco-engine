from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.paths import get_run_output_dir

router = APIRouter()


@router.get("/runs/{run_id}/download/workbook")
def download_workbook(run_id: str):
    workbook_path = get_run_output_dir(run_id) / "final_workbook.xlsx"
    if not workbook_path.exists():
        raise HTTPException(status_code=404, detail="Workbook not found")
    return FileResponse(path=workbook_path, filename=workbook_path.name)


@router.get("/runs/{run_id}/download/pdf")
def download_pdf(run_id: str):
    pdf_path = get_run_output_dir(run_id) / "final_report.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(path=pdf_path, filename=pdf_path.name)
