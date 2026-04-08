# Step 5 - n8n production orchestration flow

This step redesigns n8n to:
- accept the FCO intake form
- save files to the shared volume
- submit a small JSON job to `fco-api`
- wait for a webhook callback
- validate callback token and run_id
- fall back to API status if callback never arrives

## Required n8n runtime prerequisites

1. `n8n` container must mount the same shared host path as the API/worker:
   - container path: `/shared/fco`

2. `n8n` must join the same external Docker network as `fco-api`:
   - network name example: `fco_net`

3. `fco-api` must be reachable from n8n at:
   - `http://fco-api:8000`

4. Add these environment variables to the n8n project:
   - `FCO_API_BASE_URL=http://fco-api:8000`
   - `FCO_SHARED_CONTAINER_PATH=/shared/fco`
   - `FCO_CALLBACK_SECRET=<same shared secret used in FastAPI env>`

---

## Final flow

```text
FCO Intake Form
-> Normalize Inputs
-> Generate Run Context
-> Create Run Folders
-> Write uploaded files into input folder
-> Build Submit Payload
-> Submit Job to FastAPI
-> Wait for Callback (with expiration)
-> Validate Callback
-> If callback valid and success => complete
-> If callback valid and failure => fail
-> On wait timeout => Check Status API
   -> completed => fetch manifest and complete
   -> failed => fail
   -> otherwise => timeout/orphaned message
```

---

## Recommended node names

1. `FCO Intake Form`
2. `Normalize Inputs`
3. `Generate Run Context`
4. `Create Run Folders`
5. `Write Loads File`
6. `Write Fuel Statement File`
7. `Write Fuel Prices File`
8. `Write Axestrack Logo`
9. `Write Client Logo`
10. `Build Submit Payload`
11. `Submit Job`
12. `Wait for FCO Callback`
13. `Validate Callback`
14. `If Callback Success`
15. `Check Run Status`
16. `Get Manifest`
17. `Build Success Response`
18. `Build Failure Response`
19. `Form Completion`

---

## Node details

### 1) FCO Intake Form
Use your existing form fields.

Required file field names:
- `Loads_File`
- `Fuel_Statement_File`
- `Fuel_Prices_File`
- `Axestrack_Logo`
- `Client_Logo`

Required config fields should map to:
- `Client_Full_Name`
- `Fueling_Partner_Name`
- `Report_Month`
- `Assumed_MPG`
- `Starting_Fuel_1`
- `Starting_Fuel_2`
- `Starting_Fuel_3`
- `Ending_Fuel_Reserve`
- `Tank_Capacity`
- `Route_Cluster_Radius_Miles`
- `Corridor_Radius_Miles`
- `Rough_Cost_Decision_Threshold`
- `Current_CPG_Override`
- `ORS_API_Key`
- `Publish_To_Google_Sheets`
- `Google_Drive_Folder_Id`
- `Google_Sheets_Target_Id`
- `Google_Sheet_Name_Prefix`
- `Output_File_Base_Name`
- `Loads_Sheet_Name`
- `Fuel_Statement_Sheet_Name`
- `Fuel_Prices_Sheet_Name`
- `Force_Rerun`
- `Loads_Mapping_JSON`
- `Fuel_Statement_Mapping_JSON`
- `Fuel_Prices_Mapping_JSON`

---

### 2) Normalize Inputs (Code node)
Use a Code node that converts Yes/No, parses numeric fields, and standardizes strings.

```javascript
const boolYesNo = (v) => String(v || '').trim().toLowerCase() === 'yes';
const toNum = (v, fallback = 0) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : fallback;
};

const item = $input.first().json;

return [{
  json: {
    ...item,
    Publish_To_Google_Sheets_Bool: boolYesNo(item.Publish_To_Google_Sheets),
    Force_Rerun_Bool: boolYesNo(item.Force_Rerun),
    Assumed_MPG_Num: toNum(item.Assumed_MPG, 5),
    Starting_Fuel_1_Num: toNum(item.Starting_Fuel_1, 100),
    Starting_Fuel_2_Num: toNum(item.Starting_Fuel_2, 150),
    Starting_Fuel_3_Num: toNum(item.Starting_Fuel_3, 180),
    Ending_Fuel_Reserve_Num: toNum(item.Ending_Fuel_Reserve, 40),
    Tank_Capacity_Num: toNum(item.Tank_Capacity, 240),
    Route_Cluster_Radius_Miles_Num: toNum(item.Route_Cluster_Radius_Miles, 50),
    Corridor_Radius_Miles_Num: toNum(item.Corridor_Radius_Miles, 15),
    Rough_Cost_Decision_Threshold_Num: toNum(item.Rough_Cost_Decision_Threshold, 5000),
    Current_CPG_Override_Num: toNum(item.Current_CPG_Override, 0),
  },
  binary: $input.first().binary
}];
```

---

### 3) Generate Run Context (Code node)

```javascript
function slugify(s) {
  return String(s || 'client')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '') || 'client';
}

function rand(len = 24) {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let out = '';
  for (let i = 0; i < len; i++) out += chars[Math.floor(Math.random() * chars.length)];
  return out;
}

const j = $input.first().json;
const now = new Date();
const stamp = now.toISOString().replace(/[-:.TZ]/g, '').slice(0, 14);
const baseShared = $env.FCO_SHARED_CONTAINER_PATH || '/shared/fco';
const runId = `fco_${slugify(j.Client_Full_Name)}_${stamp}`;
const callbackToken = rand(32);

const runRoot = `${baseShared}/runs/${runId}`;
const inputDir = `${runRoot}/input`;
const outputDir = `${runRoot}/output`;
const logsDir = `${runRoot}/logs`;
const stateDir = `${runRoot}/state`;

return [{
  json: {
    ...j,
    run_id: runId,
    callback_token: callbackToken,
    run_root: runRoot,
    input_dir: inputDir,
    output_dir: outputDir,
    logs_dir: logsDir,
    state_dir: stateDir,
  },
  binary: $input.first().binary
}];
```

---

### 4) Create Run Folders (Execute Command)
Command:

```bash
mkdir -p "{{$json.input_dir}}" "{{$json.output_dir}}" "{{$json.logs_dir}}" "{{$json.state_dir}}"
```

Set:
- `On Error`: Stop workflow

---

### 5-9) Write file nodes
Use **Read/Write Files from Disk** nodes, one for each binary property.

#### Write Loads File
- Operation: `Write File to Disk`
- Input Binary Field: `Loads_File`
- File Path and Name:

```text
{{$json.input_dir}}/loads{{$binary.Loads_File.fileExtension ? '.' + $binary.Loads_File.fileExtension : '.bin'}}
```

#### Write Fuel Statement File
- Input Binary Field: `Fuel_Statement_File`
- File Path and Name:

```text
{{$json.input_dir}}/fuel_statement{{$binary.Fuel_Statement_File.fileExtension ? '.' + $binary.Fuel_Statement_File.fileExtension : '.bin'}}
```

#### Write Fuel Prices File
- Input Binary Field: `Fuel_Prices_File`
- File Path and Name:

```text
{{$json.input_dir}}/fuel_prices{{$binary.Fuel_Prices_File.fileExtension ? '.' + $binary.Fuel_Prices_File.fileExtension : '.bin'}}
```

#### Write Axestrack Logo
- Input Binary Field: `Axestrack_Logo`
- File Path and Name:

```text
{{$json.input_dir}}/axestrack_logo{{$binary.Axestrack_Logo.fileExtension ? '.' + $binary.Axestrack_Logo.fileExtension : '.bin'}}
```

#### Write Client Logo
- Input Binary Field: `Client_Logo`
- File Path and Name:

```text
{{$json.input_dir}}/client_logo{{$binary.Client_Logo.fileExtension ? '.' + $binary.Client_Logo.fileExtension : '.bin'}}
```

---

### 10) Build Submit Payload (Code node)

```javascript
const j = $input.first().json;

return [{
  json: {
    run_id: j.run_id,
    input_dir: j.input_dir,
    output_dir: j.output_dir,
    callback_url: j.callback_url,
    callback_token: j.callback_token,
    config: {
      client_full_name: j.Client_Full_Name,
      fueling_partner_name: j.Fueling_Partner_Name,
      report_month: j.Report_Month,
      assumed_mpg: j.Assumed_MPG_Num,
      start_fuel_scenarios: [
        j.Starting_Fuel_1_Num,
        j.Starting_Fuel_2_Num,
        j.Starting_Fuel_3_Num
      ],
      ending_fuel_reserve: j.Ending_Fuel_Reserve_Num,
      tank_capacity: j.Tank_Capacity_Num,
      eligibility_miles: 1000,
      route_cluster_radius_miles: j.Route_Cluster_Radius_Miles_Num,
      corridor_radius_miles: j.Corridor_Radius_Miles_Num,
      decision_threshold: j.Rough_Cost_Decision_Threshold_Num,
      current_cpg_override: j.Current_CPG_Override_Num,
      ors_api_key: j.ORS_API_Key,
      publish_to_google_sheets: j.Publish_To_Google_Sheets_Bool,
      google_drive_folder_id: j.Google_Drive_Folder_Id,
      google_sheets_target_id: j.Google_Sheets_Target_Id,
      google_sheet_name_prefix: j.Google_Sheet_Name_Prefix,
      output_file_base_name: j.Output_File_Base_Name,
      force_rerun: j.Force_Rerun_Bool,
      loads_sheet_name: j.Loads_Sheet_Name,
      fuel_statement_sheet_name: j.Fuel_Statement_Sheet_Name,
      fuel_prices_sheet_name: j.Fuel_Prices_Sheet_Name
    },
    mappings: {
      loads: JSON.parse(j.Loads_Mapping_JSON),
      fuel_statement: JSON.parse(j.Fuel_Statement_Mapping_JSON),
      fuel_prices: JSON.parse(j.Fuel_Prices_Mapping_JSON)
    }
  }
}];
```

---

### 11) Submit Job (HTTP Request)
- Method: `POST`
- URL:

```text
{{$env.FCO_API_BASE_URL}}/run-fco
```

- Send Body: JSON
- Body: current JSON

Expected response:
```json
{
  "run_id": "...",
  "status": "accepted",
  "message": "Run queued successfully"
}
```

---

### 12) Wait for FCO Callback
Use a **Wait** node configured to resume via webhook.

#### Expiration
Set an explicit expiration, e.g.:
- 60 minutes

This protects against worker crash/OOM/no callback.

The wait node’s callback URL should be used as the `callback_url`.

### How to populate `callback_url`
Before `Build Submit Payload`, add a small Code or Set node that stores the wait-resume URL once available in your flow design. If your n8n version exposes the webhook resume URL through the Wait node differently, use your instance’s generated URL and store it alongside `run_id` and `callback_token`.

---

### 13) Validate Callback (Code node)
Use this after the wait-resume node.

```javascript
const body = $input.first().json;
const headers = $input.first().json.headers || {};
const expectedToken = $('Generate Run Context').first().json.callback_token;
const expectedRunId = $('Generate Run Context').first().json.run_id;

const receivedToken =
  headers['x-fco-callback-token'] ||
  headers['X-FCO-Callback-Token'] ||
  '';

const valid = String(body.run_id || '') === String(expectedRunId)
  && String(receivedToken || '') === String(expectedToken);

return [{
  json: {
    valid_callback: valid,
    callback_body: body,
    expected_run_id: expectedRunId
  }
}];
```

---

### 14) If Callback Success
Use IF nodes to split:
- invalid callback
- valid callback + success
- valid callback + failure

---

### 15) Check Run Status (HTTP Request)
This is the timeout fallback path.

- Method: `GET`
- URL:

```text
{{$env.FCO_API_BASE_URL}}/runs/{{$('Generate Run Context').first().json.run_id}}
```

If status is:
- `completed` -> fetch manifest or use embedded manifest
- `failed` -> fail
- `callback_pending` / `running` / `queued` -> return timeout/orphaned message

---

### 16) Get Manifest (optional HTTP Request)
If needed:
- Method: `GET`
- URL:

```text
{{$env.FCO_API_BASE_URL}}/runs/{{$('Generate Run Context').first().json.run_id}}/manifest
```

---

### 17) Build Success Response (Code node)
Build a user-facing final payload:

```javascript
const m = $input.first().json.manifest || $input.first().json.callback_body || $input.first().json;

return [{
  json: {
    success: true,
    run_id: m.run_id,
    message: 'FCO run completed successfully.',
    workbook_download_url: `${$env.FCO_API_BASE_URL}/runs/${m.run_id}/download/workbook`,
    pdf_download_url: `${$env.FCO_API_BASE_URL}/runs/${m.run_id}/download/pdf`,
    google_sheet_url: m.google_sheet_url || '',
    summary: m.summary || {}
  }
}];
```

---

### 18) Build Failure Response (Code node)
```javascript
const j = $input.first().json;
return [{
  json: {
    success: false,
    run_id: j.run_id || $('Generate Run Context').first().json.run_id,
    message: j.error || j.error_message || 'FCO run failed.',
    details: j
  }
}];
```

---

### 19) Form Completion
Use the final success/failure payload to show completion text.

Success example:
- Title: `FCO run completed`
- Message: include run_id, workbook link, PDF link, and Google Sheet link if present

Failure example:
- Title: `FCO run failed`
- Message: include run_id and the failure reason

---

## Timeout fallback behavior
If the wait node expires:
1. call `GET /runs/{run_id}`
2. if `completed`, continue to success path
3. if `failed`, continue to failure path
4. else return:
   - `Run timed out waiting for callback. Status is still running or callback was not received.`

This is your safety net for zombie/OOM/missed callback scenarios.

---

## Callback security
Require both:
- run-specific callback token in header
- matching `run_id` in payload

Header:
```text
X-FCO-Callback-Token: {callback_token}
```

This prevents accidental or fake completions.

---

## Same repo rule
These Step 5 files belong in the **same GitHub repo** as Steps 1-4.
