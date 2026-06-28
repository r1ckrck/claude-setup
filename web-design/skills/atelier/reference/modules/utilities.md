# Utility shelf

Small, single-purpose picks. Reach for one when its feature appears; each is a default, not a debate.

| Need | Default | Posture |
|---|---|---|
| Toasts / notifications | **Sonner** | import (tiny) |
| Command palette | **cmdk** | vendor (headless; style with tokens) |
| Drag and drop | **dnd-kit** | import |
| Rich text editor | **Tiptap** | import (headless; markup is yours) |
| Transactional email | **Resend + React Email** | import + vendored email components |
| i18n | **next-intl** | import |
| Search | **Pagefind** (static sites) · **Orama** (in-app) · Algolia (hosted scale) | mixed |
| Analytics | **Plausible / Umami** (privacy-first) · Vercel Analytics | external service |
| Date / time | **date-fns** (tree-shakable) | import |

**Rules**
- Headless utilities (cmdk, Tiptap, dnd-kit) get styled with **your tokens** — own the markup.
- Privacy-first analytics by default; reach for heavier analytics only when the data need is real.
- One toast lib, one editor — don't accumulate duplicates.

**Tier** → as the feature appears (mostly T2+).
