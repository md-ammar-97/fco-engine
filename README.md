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

## Step 3 status
Included:
- production API endpoints for submit/status/manifest/download
- queue/state transitions
- callback contract from worker to n8n
- placeholder run executor for Step 4 migration of full FCO logic
