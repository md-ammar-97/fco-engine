# FCO Engine

Local Docker sidecar architecture for Fuel Cost Optimization.

## Components
- n8n: intake/orchestration
- fco-api: job intake/status/download API
- fco-worker: single-run background worker

## Runtime model
- shared persistent volume
- SQLite queue/state database (WAL enabled)
- async callback back to n8n
- one active run at a time

## Status
Bootstrapped scaffold created from the approved architecture plan.
