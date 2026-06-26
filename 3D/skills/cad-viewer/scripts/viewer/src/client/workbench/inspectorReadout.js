import { buildCadRefToken } from "cadjs/lib/cadRefs.js";

import { SELECT_MODE } from "./constants.js";
import { formatMm, formatNumber, formatXyz } from "./valueUtils.js";

// An axis-aligned direction is "named" (X/Y/Z + sign) when one component dominates.
const AXIS_ALIGN_TOLERANCE = 1e-3;
// Plane bbox extents are treated as zero-thickness below this (mm).
const PLANAR_THICKNESS_TOLERANCE = 1e-3;
// Relative area match for planar rectangle / disc classification.
const SHAPE_AREA_TOLERANCE = 0.03;
// A full circle's perimeter matches 2*pi*r within this relative error.
const FULL_CIRCLE_TOLERANCE = 0.02;
// Below this dihedral angle the two faces read as tangent (fillet / blend).
const TANGENT_DIHEDRAL_DEG = 5;

const AXIS_LABELS = ["X", "Y", "Z"];

export function availableSelectModesFor({ insidePart = false } = {}) {
  return insidePart
    ? [SELECT_MODE.FEATURE]
    : [SELECT_MODE.PART, SELECT_MODE.FEATURE];
}

function vec(point) {
  return Array.isArray(point) && point.length >= 3
    ? [Number(point[0]) || 0, Number(point[1]) || 0, Number(point[2]) || 0]
    : null;
}

function sub(a, b) {
  return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
}

function dot(a, b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

function magnitude(a) {
  return Math.hypot(a[0], a[1], a[2]);
}

function scale(a, factor) {
  return [a[0] * factor, a[1] * factor, a[2] * factor];
}

function add(a, b) {
  return [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
}

// Returns { axis: "X"|"Y"|"Z", sign, index } when the unit vector is axis-aligned, else null.
function namedAxis(direction) {
  const d = vec(direction);
  if (!d) {
    return null;
  }
  const length = magnitude(d);
  if (length < AXIS_ALIGN_TOLERANCE) {
    return null;
  }
  const unit = scale(d, 1 / length);
  for (let index = 0; index < 3; index += 1) {
    if (Math.abs(Math.abs(unit[index]) - 1) < AXIS_ALIGN_TOLERANCE
      && Math.abs(unit[(index + 1) % 3]) < AXIS_ALIGN_TOLERANCE
      && Math.abs(unit[(index + 2) % 3]) < AXIS_ALIGN_TOLERANCE) {
      return { axis: AXIS_LABELS[index], sign: unit[index] < 0 ? -1 : 1, index };
    }
  }
  return null;
}

function bboxExtents(bbox) {
  const min = vec(bbox?.min);
  const max = vec(bbox?.max);
  if (!min || !max) {
    return null;
  }
  return [max[0] - min[0], max[1] - min[1], max[2] - min[2]];
}

function field(key, label, value, { exact = true, unit = "" } = {}) {
  return { key, label, value, unit, exact };
}

function directionText(direction) {
  const named = namedAxis(direction);
  if (named) {
    return `${named.sign < 0 ? "−" : "+"}${named.axis}`;
  }
  return formatXyz(direction);
}

// Axis-angle from a row-major 4x4 (manifest occurrence transform).
function rotationFromTransform(transform) {
  if (!Array.isArray(transform) || transform.length < 16) {
    return null;
  }
  const r = [
    [transform[0], transform[1], transform[2]],
    [transform[4], transform[5], transform[6]],
    [transform[8], transform[9], transform[10]]
  ];
  const trace = r[0][0] + r[1][1] + r[2][2];
  const cosAngle = Math.min(1, Math.max(-1, (trace - 1) / 2));
  const angleRad = Math.acos(cosAngle);
  const angleDeg = (angleRad * 180) / Math.PI;
  if (angleDeg < 1e-3) {
    return { angleDeg: 0, axis: null };
  }
  const sinAngle = Math.sin(angleRad);
  if (Math.abs(sinAngle) < 1e-6) {
    return { angleDeg, axis: null };
  }
  const axis = [
    (r[2][1] - r[1][2]) / (2 * sinAngle),
    (r[0][2] - r[2][0]) / (2 * sinAngle),
    (r[1][0] - r[0][1]) / (2 * sinAngle)
  ];
  return { angleDeg, axis };
}

function translationFromTransform(transform) {
  if (!Array.isArray(transform) || transform.length < 16) {
    return null;
  }
  return [transform[3], transform[7], transform[11]];
}

function cursorReadout(hitPointModelXYZ) {
  const xyz = vec(hitPointModelXYZ);
  return { xyz, onSurface: Boolean(xyz) };
}

function rowFor(selectorRuntime, reference) {
  const rows = reference?.selectorType === "edge" ? selectorRuntime?.edges : selectorRuntime?.faces;
  const index = Number(reference?.rowIndex ?? reference?.pickData?.rowIndex);
  return Array.isArray(rows) && Number.isInteger(index) ? rows[index] || null : null;
}

function refTokenFor(selectorRuntime, selector) {
  const cadPath = String(selectorRuntime?.cadPath || "").trim();
  const cleanSelector = String(selector || "").trim();
  if (!cadPath) {
    return "";
  }
  return cleanSelector ? buildCadRefToken({ cadPath, selector: cleanSelector }) : `@cad[${cadPath}]`;
}

function buildPartEntity(selectorRuntime, reference, row) {
  const rawOccurrenceId = String(row?.occurrenceId || "").trim();
  const occurrence = (selectorRuntime?.occurrences || []).find((occ) => String(occ?.id || "") === rawOccurrenceId) || null;
  const shapes = (selectorRuntime?.shapes || []).filter((shape) => String(shape?.occurrenceId || "") === rawOccurrenceId);
  const occurrenceSelector = String(reference?.occurrenceId || "").trim() || rawOccurrenceId;
  const label = String(occurrence?.name || occurrenceSelector || "Part");

  const fields = [];
  const extents = bboxExtents(occurrence?.bbox);
  if (extents) {
    fields.push(field("size", "Size", `${formatNumber(extents[0])} × ${formatNumber(extents[1])} × ${formatNumber(extents[2])}`, { unit: "mm" }));
  }
  const volume = shapes.reduce((total, shape) => total + (Number(shape?.volume) || 0), 0);
  if (volume > 0) {
    fields.push(field("volume", "Volume", formatNumber(volume), { unit: "mm³" }));
  }
  const origin = translationFromTransform(occurrence?.transform);
  if (origin) {
    fields.push(field("placement", "Placement", formatXyz(origin), { unit: "mm" }));
  }
  const rotation = rotationFromTransform(occurrence?.transform);
  if (rotation) {
    fields.push(field(
      "rotation",
      "Rotation",
      rotation.angleDeg === 0 || !rotation.axis
        ? "none"
        : `${formatNumber(rotation.angleDeg)}° about ${directionText(rotation.axis)}`
    ));
  }

  return {
    kind: "part",
    subtype: "occurrence",
    label,
    refToken: refTokenFor(selectorRuntime, occurrenceSelector),
    occurrence: occurrence ? { id: occurrenceSelector, name: occurrence.name || "" } : null,
    fields
  };
}

function planarFaceFields(row) {
  const extents = bboxExtents(row?.bbox);
  const area = Number(row?.area) || 0;
  const normal = vec(row?.normal) || vec(row?.params?.axis);
  const fields = [];

  let subtype = "planar";
  if (extents) {
    const inPlane = extents
      .map((value, index) => ({ value, index }))
      .filter((entry) => entry.value > PLANAR_THICKNESS_TOLERANCE)
      .sort((a, b) => b.value - a.value);
    const [w, h] = [inPlane[0]?.value || 0, inPlane[1]?.value || 0];
    const rectArea = w * h;
    const discDiameter = (w + h) / 2;
    const discArea = Math.PI * (discDiameter / 2) ** 2;
    const rectMatch = rectArea > 0 && Math.abs(area - rectArea) / area < SHAPE_AREA_TOLERANCE;
    const discMatch = Math.abs(w - h) / Math.max(w, h, 1) < SHAPE_AREA_TOLERANCE
      && discArea > 0 && Math.abs(area - discArea) / area < SHAPE_AREA_TOLERANCE;
    if (discMatch) {
      subtype = "planar-circular";
      fields.push(field("diameter", "Diameter", formatMm(discDiameter), { exact: false }));
    } else if (rectMatch) {
      subtype = "planar-rectangular";
      fields.push(field("size", "Size", `${formatNumber(w)} × ${formatNumber(h)}`, { unit: "mm" }));
    } else {
      subtype = "planar-other";
      fields.push(field("outline", "Outline", `${formatNumber(w)} × ${formatNumber(h)}`, { unit: "mm", exact: false }));
    }
  }
  if (normal) {
    fields.push(field("normal", "Normal", directionText(normal)));
    const named = namedAxis(normal);
    const center = vec(row?.center);
    if (named && center) {
      fields.push(field("plane", "Plane", `${named.axis} = ${formatNumber(center[named.index])}`, { unit: "mm" }));
    }
  }
  return { subtype, fields };
}

function cylindricalFaceFields(row) {
  const params = row?.params || {};
  const radius = Number(params.radius) || 0;
  const axis = vec(params.axis);
  const origin = vec(params.origin);
  const extents = bboxExtents(row?.bbox);
  const fields = [field("diameter", "Diameter", formatMm(radius * 2))];
  if (axis) {
    fields.push(field("axis", "Axis", directionText(axis)));
    if (origin) {
      fields.push(field("axisPoint", "Axis point", formatXyz(origin), { unit: "mm" }));
    }
    const named = namedAxis(axis);
    if (extents && named) {
      fields.push(field("height", "Height", formatMm(extents[named.index]), { exact: false }));
    }
  }
  return { subtype: "cylindrical", fields };
}

function conicalFaceFields(row) {
  const params = row?.params || {};
  const axis = vec(params.axis);
  const origin = vec(params.origin);
  const halfAngleDeg = Number.isFinite(Number(params.semiAngleRad))
    ? (Number(params.semiAngleRad) * 180) / Math.PI
    : null;
  const fields = [];
  if (halfAngleDeg != null) {
    fields.push(field("halfAngle", "Half-angle", `${formatNumber(halfAngleDeg)}°`));
  }
  if (axis) {
    fields.push(field("axis", "Axis", directionText(axis)));
  }
  if (origin) {
    fields.push(field("apex", "Apex", formatXyz(origin), { unit: "mm" }));
  }
  return { subtype: "conical", fields };
}

function sphericalFaceFields(row) {
  const params = row?.params || {};
  const fields = [field("radius", "Radius", formatMm(Number(params.radius) || 0))];
  const center = vec(params.center);
  if (center) {
    fields.push(field("center", "Center", formatXyz(center), { unit: "mm" }));
  }
  return { subtype: "spherical", fields };
}

function toroidalFaceFields(row) {
  const params = row?.params || {};
  const fields = [
    field("majorRadius", "Major radius", formatMm(Number(params.majorRadius) || 0)),
    field("minorRadius", "Minor radius", formatMm(Number(params.minorRadius) || 0))
  ];
  const axis = vec(params.axis);
  if (axis) {
    fields.push(field("axis", "Axis", directionText(axis)));
  }
  const center = vec(params.center);
  if (center) {
    fields.push(field("center", "Center", formatXyz(center), { unit: "mm" }));
  }
  return { subtype: "toroidal", fields };
}

function freeformFaceFields() {
  return { subtype: "freeform", fields: [] };
}

function subtypeFaceFields(row) {
  switch (String(row?.surfaceType || "").toLowerCase()) {
    case "plane": return planarFaceFields(row);
    case "cylinder": return cylindricalFaceFields(row);
    case "cone": return conicalFaceFields(row);
    case "sphere": return sphericalFaceFields(row);
    case "torus": return toroidalFaceFields(row);
    default: return freeformFaceFields(row);
  }
}

function buildFaceEntity(selectorRuntime, reference, row) {
  const fields = [
    field("surface", "Surface", String(row?.surfaceType || "—"))
  ];
  if (Number(row?.area)) {
    fields.push(field("area", "Area", formatNumber(row.area), { unit: "mm²" }));
  }
  const centroid = vec(row?.center);
  if (centroid) {
    fields.push(field("centroid", "Centroid", formatXyz(centroid), { unit: "mm" }));
  }
  const { subtype, fields: subtypeFields } = subtypeFaceFields(row);
  fields.push(...subtypeFields);

  return {
    kind: "face",
    subtype,
    label: String(reference?.label || "Face"),
    refToken: refTokenFor(selectorRuntime, reference?.displaySelector),
    occurrence: occurrenceSummary(selectorRuntime, row),
    fields
  };
}

function lineEdgeFields(row) {
  const params = row?.params || {};
  const direction = vec(params.direction);
  const center = vec(row?.center);
  const length = Number(row?.length) || 0;
  const fields = [];
  if (direction) {
    fields.push(field("direction", "Direction", directionText(direction)));
  }
  if (direction && center && length) {
    const half = scale(direction, length / 2 / (magnitude(direction) || 1));
    fields.push(field("endpoints", "Endpoints", `${formatXyz(sub(center, half))} → ${formatXyz(add(center, half))}`, { unit: "mm" }));
  }
  return { subtype: "line", fields };
}

function circleEdgeFields(row) {
  const params = row?.params || {};
  const radius = Number(params.radius) || 0;
  const length = Number(row?.length) || 0;
  const fullPerimeter = 2 * Math.PI * radius;
  const isFullCircle = radius > 0 && Math.abs(length - fullPerimeter) / fullPerimeter < FULL_CIRCLE_TOLERANCE;
  const fields = [];
  const center = vec(params.center);
  const axis = vec(params.axis);
  if (isFullCircle) {
    fields.push(field("diameter", "Diameter", formatMm(radius * 2)));
  } else {
    fields.push(field("radius", "Radius", formatMm(radius)));
    if (radius > 0) {
      const sweepDeg = (length / radius) * (180 / Math.PI);
      fields.push(field("sweep", "Sweep", `${formatNumber(sweepDeg)}°`, { exact: false }));
    }
  }
  if (center) {
    fields.push(field("center", "Center", formatXyz(center), { unit: "mm" }));
  }
  if (axis) {
    fields.push(field("axis", "Axis", directionText(axis)));
  }
  return { subtype: isFullCircle ? "circle" : "arc", fields };
}

function ellipseEdgeFields(row) {
  const params = row?.params || {};
  const fields = [
    field("majorRadius", "Major radius", formatMm(Number(params.majorRadius) || 0)),
    field("minorRadius", "Minor radius", formatMm(Number(params.minorRadius) || 0))
  ];
  const center = vec(params.center);
  if (center) {
    fields.push(field("center", "Center", formatXyz(center), { unit: "mm" }));
  }
  return { subtype: "ellipse", fields };
}

function subtypeEdgeFields(row) {
  switch (String(row?.curveType || "").toLowerCase()) {
    case "line": return lineEdgeFields(row);
    case "circle": return circleEdgeFields(row);
    case "ellipse": return ellipseEdgeFields(row);
    default: return { subtype: String(row?.curveType || "curve").toLowerCase(), fields: [] };
  }
}

function buildEdgeEntity(selectorRuntime, reference, row) {
  const fields = [
    field("curve", "Curve", String(row?.curveType || "—"))
  ];
  if (Number(row?.length)) {
    fields.push(field("length", "Length", formatMm(row.length)));
  }
  const { subtype, fields: subtypeFields } = subtypeEdgeFields(row);
  fields.push(...subtypeFields);

  const dihedral = row?.dihedralDeg;
  if (dihedral != null && Number.isFinite(Number(dihedral))) {
    fields.push(field("dihedral", "Dihedral", `${formatNumber(dihedral)}°`));
    if (Number(dihedral) < TANGENT_DIHEDRAL_DEG) {
      fields.push(field("blend", "Edge", "tangent (fillet / blend)", { exact: false }));
    }
  }

  return {
    kind: "edge",
    subtype,
    label: String(reference?.label || "Edge"),
    refToken: refTokenFor(selectorRuntime, reference?.displaySelector),
    occurrence: occurrenceSummary(selectorRuntime, row),
    fields
  };
}

function occurrenceSummary(selectorRuntime, row) {
  const rawOccurrenceId = String(row?.occurrenceId || "").trim();
  if (!rawOccurrenceId) {
    return null;
  }
  const occurrence = (selectorRuntime?.occurrences || []).find((occ) => String(occ?.id || "") === rawOccurrenceId);
  return occurrence ? { id: rawOccurrenceId, name: occurrence.name || "" } : { id: rawOccurrenceId, name: "" };
}

export function buildInspectorReadout({ reference, hitPointModelXYZ, selectorRuntime, mode } = {}) {
  const cursor = cursorReadout(hitPointModelXYZ);
  const activeMode = mode === SELECT_MODE.PART ? SELECT_MODE.PART : SELECT_MODE.FEATURE;
  const row = reference ? rowFor(selectorRuntime, reference) : null;

  if (!reference || !row) {
    return { mode: activeMode, cursor, entity: null };
  }

  let entity = null;
  if (activeMode === SELECT_MODE.PART) {
    entity = buildPartEntity(selectorRuntime, reference, row);
  } else if (reference.selectorType === "edge") {
    entity = buildEdgeEntity(selectorRuntime, reference, row);
  } else {
    entity = buildFaceEntity(selectorRuntime, reference, row);
  }

  return { mode: activeMode, cursor, entity };
}

// Whole-model assembly Part readout: built from already-loaded per-part render data
// (selectedMeshData.parts), since face/edge topology is only loaded once a part is inspected.
export function buildPartReadoutFromAssemblyPart({ part, cadPath, cursorXyz } = {}) {
  const cursor = cursorReadout(cursorXyz);
  if (!part) {
    return { mode: SELECT_MODE.PART, cursor, entity: null };
  }
  const selector = String(part.occurrenceId || part.id || "").trim();
  const fields = [];
  const extents = bboxExtents(part.bounds);
  if (extents) {
    fields.push(field(
      "size",
      "Size",
      `${formatNumber(extents[0])} × ${formatNumber(extents[1])} × ${formatNumber(extents[2])}`,
      { unit: "mm", exact: false }
    ));
  }
  const elements = part.matrixWorld?.elements;
  if (Array.isArray(elements) && elements.length >= 16) {
    fields.push(field("placement", "Placement", formatXyz([elements[12], elements[13], elements[14]]), { unit: "mm" }));
  }
  return {
    mode: SELECT_MODE.PART,
    cursor,
    entity: {
      kind: "part",
      subtype: "occurrence",
      label: String(part.name || selector || "Part"),
      refToken: refTokenFor({ cadPath }, selector),
      occurrence: { id: selector, name: String(part.name || "") },
      fields
    }
  };
}

export function inspectorReadoutRefToken(readout) {
  return String(readout?.entity?.refToken || "").trim();
}

export function serializeInspectorReadout(readout) {
  const lines = [];
  const cursorXyz = readout?.cursor?.xyz;
  lines.push(`Cursor: ${cursorXyz ? `${formatXyz(cursorXyz)} mm` : "—"}`);

  const entity = readout?.entity;
  if (entity) {
    const occurrence = entity.occurrence?.name ? ` (${entity.occurrence.name})` : "";
    lines.push(`${entity.label}${occurrence}`);
    if (entity.refToken) {
      lines.push(entity.refToken);
    }
    for (const item of entity.fields || []) {
      const unit = item.unit ? ` ${item.unit}` : "";
      lines.push(`${item.label}: ${item.value}${unit}`);
    }
  }
  return lines.join("\n");
}
