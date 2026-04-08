# FCO Engine

Local Docker sidecar architecture for Fuel Cost Optimization.

## Components
- n8n: intake/orchestration
- fco-api: job intake/status/download API
- fco-worker: single-run background worker

## Runtime model
- shared persistent host folder
- SQLite queue/state database (WAL enabled)
- async callback back to n8n
- one active run at a time
- external Docker network shared with n8n

## Step 6 status
Included:
- production FastAPI + worker scaffolding
- preprocessing pipeline scaffold
- workbook + PDF generation scaffold
- n8n orchestration guide
- importable n8n workflow JSON scaffold

Still pending for full optimization parity:
- ORS route geometry
- corridor station extraction
- exact lexicographic optimization
- richer fuel/load matching logic
- final production polish after live import testing
