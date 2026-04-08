# Step 2 - Docker and local sidecar setup

## 1) Create the shared host folder

### Windows PowerShell
```powershell
New-Item -ItemType Directory -Force -Path C:\docker\fco-shared\runs
New-Item -ItemType Directory -Force -Path C:\docker\fco-shared\cache
New-Item -ItemType Directory -Force -Path C:\docker\fco-shared\logs
New-Item -ItemType Directory -Force -Path C:\docker\fco-shared\queue
```

### Linux
```bash
sudo mkdir -p /srv/fco-shared/{runs,cache,logs,queue}
sudo chown -R 1000:1000 /srv/fco-shared
```

## 2) Create the shared Docker network

```bash
docker network create fco_net
```

## 3) Copy env example

```bash
cp .env.example .env
```

Then edit:
- `FCO_SHARED_HOST_PATH`
- `ORS_API_KEY`
- `CALLBACK_SHARED_SECRET`

## 4) Build and start FCO services

```bash
docker compose build --no-cache
docker compose up -d
```

## 5) Verify API health

Open:
- http://localhost:8000/health

Expected:
```json
{"status":"ok"}
```

## 6) Update your existing n8n project

Merge `deployment/n8n-compose-snippet.yml` into your existing n8n compose file, then:
- add `.env` values for `FCO_SHARED_HOST_PATH`
- add `.env` value for `DOCKER_NETWORK_NAME=fco_net`

Recreate n8n after the mount/network change.

## 7) What this step gives you

- Debian slim Python base
- shared host path for persistent run data
- UID/GID aligned API + worker containers
- external shared network for n8n sidecar communication
- health-checked FCO API
