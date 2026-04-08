from pathlib import Path
from typing import Any, Dict

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def write_pdf_report(output_path: Path, client_name: str, report_month: str, summary: Dict[str, Any]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "Fuel Cost Optimization Analysis")
    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"For: {client_name}")
    y -= 18
    c.drawString(50, y, f"Month: {report_month}")
    y -= 30

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Summary")
    y -= 20
    c.setFont("Helvetica", 11)
    for key, value in summary.items():
        c.drawString(60, y, f"{key}: {value}")
        y -= 16

    y -= 20
    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Note: Step 4 includes preprocessing/workbook/PDF generation and heuristic scenario outputs.")
    y -= 14
    c.drawString(50, y, "Full ORS-based route optimization and detailed fuel-load matching remain for later hardening.")
    c.save()
    return output_path
