# Official SendCutSend Source Map

Use these sources as live evidence, not as a stable API. Field coverage, value types, and `N/A` usage can vary. Before making pass/fail claims, cite the exact source URL and, for JSON facts, the field path used.

## Core Entry Points (machine-readable JSON — currently unreachable)

- Ordering guide: https://cdn.sendcutsend.com/specs/sendcutsend-ordering-guide.md
- Catalog JSON: https://cdn.sendcutsend.com/specs/sendcutsend-catalog.json
- Engineering specs JSON: https://cdn.sendcutsend.com/specs/sendcutsend-specs.json

The `cdn.sendcutsend.com/specs/*` endpoints return HTTP 403 to programmatic fetches and do not load in a browser either — treat them as unavailable. Try them first in case access is restored; on 403/404, fall back to the live human-readable sources below.

## Live human-readable sources (working — primary path)

These official pages return HTTP 200 and carry the same material and service facts as the JSON feeds, in HTML tables. Use them as the evidence path while the JSON feeds are down.

- Guidelines hub: https://sendcutsend.com/guidelines/
- Material gauge / thickness chart: https://sendcutsend.com/materials/gauge-sizes-for-sheet-metal/
- Min / max part sizes: https://sendcutsend.com/materials/min-max/
- Processing min / max part sizes: https://sendcutsend.com/materials/processing-min-max/
- Drill / hole size reference: https://sendcutsend.com/guidelines/drill-chart/
- Hardware catalog: https://sendcutsend.com/guidelines/hardware/catalog/
- Bend calculator: https://sendcutsend.com/bending-calculator/

Fetch the relevant page(s) directly before each review. Use the current response bodies as the evidence for material/service checks, and cite the URL plus the access date in the report. Parse HTML tables defensively — column order and units can vary.

## Source Roles

- Ordering guide: use for ordering flow, accepted file formats, plain-language design rules, and general service explanations.
- Catalog JSON: use for orderability facts such as material SKUs, material names, thicknesses, stock status, cutting process, min/max part size, available services, hardware items, and finish options.
- Engineering specs JSON: use for SKU-keyed design validation facts such as tolerances, minimum hole/bridge/edge values, bending parameters, tapping, countersinking, hardware insertion, dimple forming, finishing constraints, and material properties.

## Provenance To Capture

- Source URL
- Access date
- JSON `_meta.schema_version`
- JSON `_meta.generated_at`
- JSON `_meta.source_data_generated_at` when present
- Field path for row-level citations, such as `sendcutsend-specs.json materials[sku=ALU-063].cutting_specs.min_hole_size`

## Conflict Handling

Prefer exact SKU joins across catalog and specs. If source facts conflict or a field is missing, unparsable, or `N/A`, report the uncertainty and mark the dependent row `❓ need more info` unless another more specific, cited source resolves it.

Use this precedence for source facts:

1. material/thickness/service-specific configurator or current quote/upload result
2. exact SKU entry in engineering specs JSON (when reachable)
3. exact SKU entry in catalog JSON (when reachable)
4. ordering guide (when reachable)
5. live human-readable sources listed above — currently the working evidence path while the JSON feeds 403

Record the conflict and the page you relied on.
