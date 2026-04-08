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

## Step 4 status
Included:
- real preprocessing pipeline scaffold for loads/fuel/city mapping/routes
- workbook generation
- PDF generation
- heuristic scenario outputs
- callback + manifest integration

Still pending for full optimization parity:
- ORS route geometry
- corridor station extraction
- exact multi-stop optimization
- richer fuel/load matching logic
