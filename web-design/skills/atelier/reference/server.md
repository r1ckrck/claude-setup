# Server — by kind

Activated at **T2+**, when a project "talks back to the frontend and stores stuff." Choose by *kind* — escalating from no server to a full one. Defaults lean **own-it / dependency-light**.

## The kinds

| Kind | When | Default | Reach for |
|---|---|---|---|
| **Serverless / API routes** | just a bit of backend — forms, webhooks, mutations (T2) | Next API routes + **Server Actions** | Cloudflare Workers (edge) |
| **BaaS** (DB+auth+storage bundled) | need a backend, don't want to operate one (T2–T3) | **Supabase** (Postgres, RLS, open-source, self-hostable) | Convex (reactive realtime) · PocketBase (single-binary self-host) |
| **Standalone backend** | want full control / own the server (T3) | **Hono** (14 KB, runs anywhere) + Drizzle | NestJS (large, structured) · Elysia (all-in Bun) |
| **Edge** | global low-latency reads (T3–T4) | Cloudflare Workers + Turso (SQLite) | Deno Deploy |

## Cross-cutting defaults

| Concern | Default | Note |
|---|---|---|
| Database | **Postgres** (Neon / Supabase) | SQLite/Turso for edge & per-user DBs |
| ORM | **Drizzle** | SQL-first, serverless-friendly, lighter than Prisma's query engine |
| Auth | **Better-Auth** | self-hosted, lives in *your* DB — fits own-your-stack. Clerk only for speed (<50K MAU, accepting lock-in) |
| Transport | **Server Actions** (first-party) | tRPC for end-to-end types in a TS monorepo; REST only for public/mobile clients |
| Storage | **Cloudflare R2** | zero egress |
| Background jobs | **Upstash QStash** · Supabase Queues + `pg_cron` | — |

## Rules

- **Least power**: don't stand up a standalone backend if Server Actions + a BaaS cover it. Most T2–T3 projects never need more than Supabase.
- Auth and DB belong **in your control** by default (Better-Auth in your Postgres) — reach for hosted (Clerk) only to trade ownership for speed.
- Don't reach for tRPC unless there's a shared TS codebase to justify it; REST is for clients that aren't your Next app.

## Recipes (mapped to tier)

- **Form + storage** (T2) — Next + Server Actions · Supabase (DB+Auth) · R2.
- **Indie SaaS** (T3) — Next + Server Actions/tRPC · Neon Postgres · Drizzle · Better-Auth · Polar billing · R2.
- **Realtime collaborative** (T3) — Convex (reactive backend, realtime built-in).
- **Global edge-first** (T3–T4) — Hono on Cloudflare Workers · Turso · Drizzle.
