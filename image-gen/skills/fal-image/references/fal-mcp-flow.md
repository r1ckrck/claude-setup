# fal MCP — Tool Flow

How fal-image drives the fal MCP. The 9 tools, the canonical flow for image generation, the auth gotchas, and the allowlist setup.

---

## Tools

| Tool | Use |
|---|---|
| `mcp__fal-ai__recommend_model` | Get top-ranked candidates for a task |
| `mcp__fal-ai__search_models` | Catalog search by query + category |
| `mcp__fal-ai__get_pricing` | Cost-per-run for an endpoint |
| `mcp__fal-ai__get_model_schema` | Verify endpoint exists + read input params |
| `mcp__fal-ai__run_model` | Synchronous generation (right tool for image — completes in ~150ms) |
| `mcp__fal-ai__submit_job` | Async submission (use only for long jobs — video, 3D, training) |
| `mcp__fal-ai__check_job` | Poll status / fetch result for any submitted job |
| `mcp__fal-ai__upload_file` | Upload to fal CDN (`file_path` param fails over HTTP transport — use the REST API for local files) |
| `mcp__fal-ai__search_docs` | Search fal docs |

---

## Canonical flow — image generation

```
1. recommend_model(task)         → ranked candidate endpoint_ids
2. get_pricing(endpoint_id)      → confirm cost
3. get_model_schema(endpoint_id) → verify endpoint + read params
4. run_model(endpoint_id, input) → result with image URL + seed
```

---

## Auth

fal uses two header formats — different surface, different prefix.

| Surface | Header |
|---|---|
| fal MCP (`https://mcp.fal.ai/mcp`) | `Authorization: Bearer <FAL_KEY>` |
| fal REST (`https://rest.alpha.fal.ai/...`) | `Authorization: Key <FAL_KEY>` |

Where `<FAL_KEY>` is the `key_id:key_secret` pair from your fal dashboard. Wrong format returns a generic `{"error":"Authentication required"}` 401.

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

---

## Common errors

| Symptom | Fix |
|---|---|
| `{"error":"Authentication required"}` | Header prefix wrong — `Bearer` to MCP, `Key` to REST |
| `recommend_model` returns image-editing models when you want text-to-image | Fall back to `search_models(category="text-to-image")` |
| `get_model_schema` errors on the chosen endpoint | Endpoint deprecated or renamed — verify via `search_models` |
