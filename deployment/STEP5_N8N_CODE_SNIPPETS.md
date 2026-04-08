# Step 5 - n8n code snippets

## Generate callback token and run context
See `deployment/STEP5_N8N_FLOW.md`.

## Submit payload config target format

```json
{
  "run_id": "fco_client_20260408123456",
  "input_dir": "/shared/fco/runs/fco_client_20260408123456/input",
  "output_dir": "/shared/fco/runs/fco_client_20260408123456/output",
  "callback_url": "http://n8n:5678/webhook/...",
  "callback_token": "random-token",
  "config": {},
  "mappings": {}
}
```

## Callback manifest expected by n8n

```json
{
  "success": true,
  "run_id": "fco_client_20260408123456",
  "workbook_path": "/shared/fco/runs/fco_client_20260408123456/output/final_workbook.xlsx",
  "pdf_path": "/shared/fco/runs/fco_client_20260408123456/output/final_report.pdf",
  "google_sheet_url": null,
  "summary": {
    "eligible_trips": 0,
    "eligible_miles": 0,
    "old_cpg": 0,
    "avg_new_cpg": 0,
    "savings_abs": 0,
    "savings_pct": 0
  },
  "exceptions": {
    "unmapped_cities": 0,
    "unmatched_fuel_rows": 0
  },
  "error": null
}
```
