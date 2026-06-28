# Tables / data grids

**When** → tabular data with sorting, filtering, pagination, selection.

**Default** → **TanStack Table** — headless; you own the markup and style it with your tokens.

**Reach for**
- **AG Grid** — enterprise data grids: virtualized huge datasets, inline editing, pivoting, when a full grid product is genuinely needed.

**Rules**
- Default to headless (TanStack) so the table looks like *your* design, not a vendor's.
- AG Grid only when the feature set (editing, pivot, million-row virtualization) is the requirement — it's heavy and styled its own way.

**Deps** → TanStack Table is **import** but headless (markup is **vendor**); AG Grid is a full **import**.

**Tier** → T2+.
