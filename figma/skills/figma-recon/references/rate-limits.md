# Rate limits & smart usage

Two separate budgets. Don't conflate them.

## REST API

A per-minute **leaky bucket** keyed by endpoint tier (not a credit system). When the
bucket is full the endpoint returns **HTTP 429** with a `Retry-After` header (seconds to
wait). Other signal headers: `X-Figma-Plan-Tier`, `X-Figma-Rate-Limit-Type`,
`X-Figma-Upgrade-Link`. The engine honors `Retry-After` automatically and retries with
backoff.

Per-minute allowances rise with plan; representative figures for Dev/Full seats:

| Tier | Endpoints | Roughly |
|---|---|---|
| Tier 1 (tightest) | file GET, node render (`/images`), image fills | ~10–20 / min |
| Tier 2 | comments, webhooks | ~25–100 / min |
| Tier 3 (most generous) | projects, files list, components, styles, users | ~50–150 / min |

Implication: breadth (Tier 3 listing) is effectively free at our scale; the throttled
work is full-file reads and image renders (Tier 1) — do those deliberately.

## MCP

On a Professional plan with a Full/Dev seat: **200 tool calls/day, 15/min**. View/Collab
seats get only ~6/month. `whoami`, `generate_figma_design`, and `add_code_connect_map` are
exempt from the limit. This is the scarce budget — guard it.

## Will we hit a limit?

For inventorying one team once: `1 (projects) + N (one per project)` REST calls — even 50
projects is ~50 cheap Tier-3 calls. Nowhere near any ceiling. Limits only bite if you bulk
full-file reads, bulk image renders, or open many files with the MCP.

## The five laws

1. **Fetch once, cache, treat the cache as truth.** Re-read `docs/figma/`, don't re-call.
2. **Refresh incrementally.** Compare `last_modified` to cached `last_pulled`; skip unchanged.
3. **Skip thumbnails / renders unless asked.** They're Tier 1, the tightest tier.
4. **Narrow with REST, deepen with MCP.** Cheap listing finds candidates; MCP is spent only
   on the chosen few.
5. **Pace, never burst.** The engine spaces calls; on the MCP side, stay under 15/min and
   stop near 200/day, reporting remaining headroom.
