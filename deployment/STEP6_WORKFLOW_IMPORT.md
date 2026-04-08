# Step 6 - Importable n8n workflow

Files added:
- `deployment/fco_n8n_workflow_step6.json`

## How to use
1. Import `deployment/fco_n8n_workflow_step6.json` into n8n.
2. Review the `Wait for FCO Callback` node after import and configure resume-by-webhook according to your n8n version.
3. Make sure the n8n container has:
   - `FCO_API_BASE_URL=http://fco-api:8000`
   - `FCO_SHARED_CONTAINER_PATH=/shared/fco`
   - shared volume mount to `/shared/fco`
   - access to the shared external Docker network

## Important notes
- This workflow is aligned to the Step 5 architecture.
- It assumes the same file field names used in the form.
- It writes uploaded files into the shared volume before submitting the run.
- It includes callback validation and timeout fallback to `GET /runs/{run_id}`.
- Depending on your exact n8n build/version, the Wait node may need a quick manual review after import.
