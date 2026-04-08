# Step 5 - n8n environment values

Add these to the n8n project environment:

```env
FCO_API_BASE_URL=http://fco-api:8000
FCO_SHARED_CONTAINER_PATH=/shared/fco
FCO_CALLBACK_SECRET=replace_me
DOCKER_NETWORK_NAME=fco_net
```

Make sure the n8n container:
- mounts the same host path to `/shared/fco`
- joins the same external Docker network used by `fco-api`
