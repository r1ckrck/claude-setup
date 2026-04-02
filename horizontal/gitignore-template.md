# =============================================================================
# gitignore-template
# Reference file — copy relevant sections into per-project .gitignore files.
# Intentionally relaxed. Only include what you're confident you never want.
# =============================================================================


# --- OS metadata ---
.DS_Store
Thumbs.db


# --- Environment & secrets ---
.env
.env.local
.env.*.local
# .env.example is intentionally tracked — don't ignore it


# --- Dependencies ---
node_modules/
.pnpm-store/


# --- Logs ---
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*


# --- Editor & IDE ---
.idea/
*.swp
*.swo
*~
# .vscode/ is project-specific — include only if the team doesn't commit editor settings


# --- Claude Code local settings ---
.claude/settings.local.json
.claude/plans/


# --- Common build outputs (add per-project as needed) ---
# dist/
# build/
# out/
# .next/


# --- Coverage & test artifacts (add per-project as needed) ---
# coverage/
# .nyc_output/


# --- Deployment (add per-project as needed) ---
# .vercel/
# .netlify/


# --- Cache (add per-project as needed) ---
# .turbo/
# .cache/
# .eslintcache
# *.tsbuildinfo
