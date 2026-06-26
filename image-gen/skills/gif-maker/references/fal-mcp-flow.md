# fal MCP — Tool Flow

How gif-maker drives the fal MCP for source-clip generation. The 9 tools, the canonical async flow, the auth gotchas, and the allowlist setup.

> gif-maker uses fal only for the source MP4 — never for the final GIF (that's local ffmpeg).

---

## Tools

| Tool | Use |
|---|---|
| `mcp__fal-ai__recommend_model` | Get top-ranked candidates for a task |
| `mcp__fal-ai__search_models` | Catalog search by query + category |
| `mcp__fal-ai__get_pricing` | Cost-per-run (text-to-video models are usually `unit: "videos"` flat or `unit: "seconds"` per-second) |
| `mcp__fal-ai__get_model_schema` | Verify endpoint exists + read input params |
| `mcp__fal-ai__run_model` | Synchronous generation. **Avoid for video** — sync-poll times out unreliably while fal still queues the job |
| `mcp__fal-ai__submit_job` | Async submission. Right tool for source-clip generation. Returns `request_id` immediately. |
| `mcp__fal-ai__check_job` | Poll status / fetch result for a submitted job |
| `mcp__fal-ai__upload_file` | Not used by gif-maker (text-to-video has no source image input) |
| `mcp__fal-ai__search_docs` | Search fal docs |

---

## Canonical flow — source-clip generation

```
1. recommend_model(task)         → ranked candidate endpoint_ids
2. get_pricing(endpoint_id)      → confirm cost
3. get_model_schema(endpoint_id) → verify endpoint + read params
4. submit_job(endpoint_id, input) → returns {request_id} IMMEDIATELY
5. check_job(endpoint_id, request_id, action="status") at 10–15s intervals
   When status="completed": check_job(..., action="result") returns the video
```

Capture the `request_id` and persist it to `params.request_id` in the sidecar before the first poll. If polling fails, `request_id` is the only handle that recovers the job. Don't re-submit.

---

## Auth

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

Critical for gif-maker — the source-clip pipeline does one `submit_job` plus multiple `check_job` polls per GIF. Without allowlisting, a rejected poll iteration leaves a job orphaned (running on fal, no recovery handle in your session).

---

## Common errors

| Symptom | Fix |
|---|---|
| `{"error":"Authentication required"}` | Header prefix wrong — `Bearer` to MCP, `Key` to REST |
| `run_model` rejects but fal still queues | Use `submit_job` for source clips. Recover the orphan via `request_id` if you have it. |
| `check_job` returns 404 | request_id or endpoint_id mistyped — copy from the submit response, not by hand |
