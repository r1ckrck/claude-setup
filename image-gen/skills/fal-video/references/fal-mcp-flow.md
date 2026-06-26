# fal MCP — Tool Flow

How fal-video drives the fal MCP. The 9 tools, the canonical async flow for video generation, the i2v upload pattern, the auth gotchas, and the allowlist setup.

---

## Tools

| Tool | Use |
|---|---|
| `mcp__fal-ai__recommend_model` | Get top-ranked candidates for a task |
| `mcp__fal-ai__search_models` | Catalog search by query + category |
| `mcp__fal-ai__get_pricing` | Cost-per-run (video models are usually `unit: "videos"` flat or `unit: "seconds"` per-second) |
| `mcp__fal-ai__get_model_schema` | Verify endpoint exists + read input params |
| `mcp__fal-ai__run_model` | Synchronous generation. **Avoid for video** — sync-poll times out unreliably while fal still queues the job, leaving an unrecoverable orphan |
| `mcp__fal-ai__submit_job` | Async submission. Right tool for video. Returns `request_id` immediately. |
| `mcp__fal-ai__check_job` | Poll status / fetch result for a submitted job |
| `mcp__fal-ai__upload_file` | Upload to fal CDN (`file_path` param fails over HTTP transport — use the REST API for local files) |
| `mcp__fal-ai__search_docs` | Search fal docs |

---

## Canonical flow — video generation (text-to-video and image-to-video)

```
1. recommend_model(task)         → ranked candidate endpoint_ids
2. get_pricing(endpoint_id)      → confirm cost
3. get_model_schema(endpoint_id) → verify endpoint + read params
4. submit_job(endpoint_id, input) → returns {request_id} IMMEDIATELY
5. check_job(endpoint_id, request_id, action="status") at 10–15s intervals
   When status="completed": check_job(..., action="result") returns the video
```

Capture the `request_id` and persist it to `params.request_id` in the sidecar before the first poll. If polling fails or the session disconnects, `request_id` is the only handle that recovers the (still-running or completed) job. Don't re-submit.

---

## Image-to-video upload — direct REST

The MCP `upload_file` tool's `file_path` param fails over HTTP transport. Use the fal REST API instead:

```bash
# 1. Initiate — returns upload_url (signed) + file_url (CDN URL for the model)
curl -X POST https://rest.alpha.fal.ai/storage/upload/initiate \
  -H "Authorization: Key $FAL_KEY" \
  -H "Content-Type: application/json" \
  -d '{"file_name":"poster.png","content_type":"image/png"}'

# 2. PUT the bytes to the signed upload_url
curl -X PUT "$UPLOAD_URL" -H "Content-Type: image/png" --data-binary "@poster.png"
```

Use `file_url` as the `image_url` input to the i2v model.

---

## Auth

fal uses two header formats — different surface, different prefix.

| Surface | Header |
|---|---|
| fal MCP (`https://mcp.fal.ai/mcp`) | `Authorization: Bearer <FAL_KEY>` |
| fal REST (`https://rest.alpha.fal.ai/...`) | `Authorization: Key <FAL_KEY>` |

Wrong format returns a generic `{"error":"Authentication required"}` 401.

---

## Allowlist setup

Skip per-call permission prompts by adding to `.claude/settings.local.json`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": ["mcp__fal-ai"]
  }
}
```

Critical for video — without allowlisting, a rejected `submit_job` or `check_job` poll can leave a job orphaned (running on fal, no recovery handle in your session).

---

## Common errors

| Symptom | Fix |
|---|---|
| `{"error":"Authentication required"}` | Header prefix wrong — `Bearer` to MCP, `Key` to REST |
| `run_model` rejects but fal still queues | Don't use `run_model` for video — use `submit_job`. Recover the orphan via `request_id` if you have it. |
| `check_job` returns 404 | request_id or endpoint_id mistyped — copy from the submit response, not by hand |
