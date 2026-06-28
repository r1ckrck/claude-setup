# Content / CMS

**When** → the project has written content: case studies, blog, docs, long-form with interactive embeds.

**Default** → **MDX** — Markdown + interactive React embeds, content in-repo.

**Reach for**
- **Velite** / **Fumadocs** — typed local content (schema-validated frontmatter → typed data); Fumadocs when it's a docs site.
- **Sanity** / **Payload** — a real CMS when non-technical editors need to manage content (Payload self-hosts; Sanity is hosted).

**Rules**
- Keep content **in-repo** (MDX/Velite) until a non-developer genuinely needs to edit it — only then take on a CMS.
- **Avoid Contentlayer** — effectively unmaintained; use Velite/Fumadocs instead.
- Validate frontmatter with a schema so content shape is typed, not assumed.

**Deps** → MDX/Velite/Fumadocs are build-time (**vendor**-friendly); a CMS is an external service (**import**).

**Tier** → T1+ (in-repo content), CMS usually T3+.
