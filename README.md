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

## Step 2 status
Production Docker/compose scaffolding is included:
- `Dockerfile.api`
- `Dockerfile.worker`
- `docker-compose.yml`
- `deployment/n8n-compose-snippet.yml`
- `deployment/STEP2_SETUP.md`
