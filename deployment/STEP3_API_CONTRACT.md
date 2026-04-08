# Step 3 - FastAPI endpoints, queue/state, and callback contract

## Submit job
`POST /run-fco`

### Request body
```json
{
  "run_id": "fco_20260408_001",
  "input_dir": "/shared/fco/runs/fco_20260408_001/input",
  "output_dir": "/shared/fco/runs/fco_20260408_001/output",
  "callback_url": "http://n8n:5678/webhook/fco-callback/abc123",
  "callback_token": "secure-random-token",
  "config": {},
  "mappings": {}
}
```

### Response
```json
{
  "run_id": "fco_20260408_001",
  "status": "accepted",
  "message": "Run queued successfully"
}
```

## Status
`GET /runs/{run_id}`

Returns:
- queued
- running
- callback_pending
- completed
- failed

## Manifest
`GET /runs/{run_id}/manifest`

## Downloads
- `GET /runs/{run_id}/download/workbook`
- `GET /runs/{run_id}/download/pdf`

## Callback from worker to n8n
The worker will POST the manifest JSON to the `callback_url` supplied in the original request.

### Headers
```text
Content-Type: application/json
X-FCO-Callback-Token: {callback_token}
```

n8n should verify:
- run_id
- callback token
- optional shared secret later
