# Dataviz / charts

**When** → the project shows data: charts, dashboards, metrics.

**Default** → **Recharts** — declarative, composable, SVG, the practical default for most React charts.

**Reach for**
- **Tremor** — SaaS dashboards; pre-styled charts + KPI cards that match the shadcn aesthetic out of the box (built on Recharts).
- **visx** — bespoke/custom visualizations; low-level D3+React primitives when you need full control.
- **ECharts** — huge datasets (100k+ points), 3D charts, geo maps, real-time.

**Rules**
- Match the chart palette to **your tokens**, not the library's defaults.
- Don't reach for visx until Recharts genuinely can't express the chart — the control costs you composition time.
- ECharts only when dataset size or chart type forces it; it's the heaviest option.

**Deps** → **import** (all are engines). visx gives you primitives — the chart markup you compose is yours to own.

**Tier** → T2+.
