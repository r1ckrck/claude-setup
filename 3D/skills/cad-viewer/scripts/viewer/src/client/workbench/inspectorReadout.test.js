import assert from "node:assert/strict";
import { test } from "node:test";

import {
  availableSelectModesFor,
  buildInspectorReadout,
  buildPartReadoutFromAssemblyPart,
  inspectorReadoutRefToken,
  serializeInspectorReadout
} from "./inspectorReadout.js";
import { SELECT_MODE } from "./constants.js";

const CAD_PATH = "models/caster.step";

function runtime({ faces = [], edges = [], occurrences = [], shapes = [] } = {}) {
  return { cadPath: CAD_PATH, faces, edges, occurrences, shapes };
}

function fieldValue(readout, key) {
  return (readout.entity?.fields || []).find((item) => item.key === key);
}

test("cursor XYZ is always present; entity null without a reference", () => {
  const readout = buildInspectorReadout({
    reference: null,
    hitPointModelXYZ: [1, 2, 3],
    selectorRuntime: runtime(),
    mode: SELECT_MODE.FEATURE
  });
  assert.deepEqual(readout.cursor.xyz, [1, 2, 3]);
  assert.equal(readout.cursor.onSurface, true);
  assert.equal(readout.entity, null);
});

test("off-model: null hit point → onSurface false, entity null", () => {
  const readout = buildInspectorReadout({
    reference: null,
    hitPointModelXYZ: null,
    selectorRuntime: runtime(),
    mode: SELECT_MODE.FEATURE
  });
  assert.equal(readout.cursor.xyz, null);
  assert.equal(readout.cursor.onSurface, false);
  assert.equal(readout.entity, null);
});

test("Part mode: size, volume, placement, rotation, @cad[o#] token", () => {
  const faces = [{ occurrenceId: "o1.1", surfaceType: "plane" }];
  const occurrences = [{
    id: "o1.1",
    name: "wheel",
    transform: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 25, 0, 0, 0, 1],
    bbox: { min: [-25, -12.5, 0], max: [25, 12.5, 50] }
  }];
  const shapes = [{ occurrenceId: "o1.1", volume: 16812.78 }];
  const reference = { selectorType: "face", rowIndex: 0, occurrenceId: "o1.1", displaySelector: "o1.1.f1", label: "Face o1.1.f1" };

  const readout = buildInspectorReadout({
    reference,
    hitPointModelXYZ: [0, 0, 25],
    selectorRuntime: runtime({ faces, occurrences, shapes }),
    mode: SELECT_MODE.PART
  });

  assert.equal(readout.entity.kind, "part");
  assert.equal(readout.entity.label, "wheel");
  assert.equal(fieldValue(readout, "size").value, "50 × 25 × 50");
  assert.equal(fieldValue(readout, "volume").value, "16812.78");
  assert.equal(fieldValue(readout, "placement").value, "(0, 0, 25)");
  assert.equal(fieldValue(readout, "rotation").value, "none");
  assert.equal(readout.entity.refToken, "@cad[models/caster.step#o1.1]");
});

test("Feature face: planar rectangular vs circular", () => {
  const rect = {
    surfaceType: "plane", area: 300, center: [-30, 0, 72.5], normal: [-1, 0, 0],
    bbox: { min: [-30, -30, 70], max: [-30, 30, 75] }, params: { axis: [1, 0, 0] }
  };
  const rectReadout = buildInspectorReadout({
    reference: { selectorType: "face", rowIndex: 0, displaySelector: "o1.1.f1", label: "Face o1.1.f1" },
    hitPointModelXYZ: [-30, 0, 72.5],
    selectorRuntime: runtime({ faces: [rect] }),
    mode: SELECT_MODE.FEATURE
  });
  assert.equal(rectReadout.entity.subtype, "planar-rectangular");
  assert.equal(fieldValue(rectReadout, "size").value, "60 × 5");
  assert.equal(fieldValue(rectReadout, "plane").value, "X = -30");

  const disc = {
    surfaceType: "plane", area: Math.PI * 25, center: [0, 0, 10], normal: [0, 0, 1],
    bbox: { min: [-5, -5, 10], max: [5, 5, 10] }, params: { axis: [0, 0, 1] }
  };
  const discReadout = buildInspectorReadout({
    reference: { selectorType: "face", rowIndex: 0, displaySelector: "o1.1.f2", label: "Face o1.1.f2" },
    hitPointModelXYZ: [0, 0, 10],
    selectorRuntime: runtime({ faces: [disc] }),
    mode: SELECT_MODE.FEATURE
  });
  assert.equal(discReadout.entity.subtype, "planar-circular");
  assert.equal(fieldValue(discReadout, "diameter").value, "10 mm");
});

test("Feature face: cylindrical Ø=2r (exact) + height (approx)", () => {
  const cyl = {
    surfaceType: "cylinder", area: 86.36, center: [-22, -22, 72.5], normal: null,
    bbox: { min: [-24.75, -24.75, 70], max: [-19.25, -19.25, 75] },
    params: { origin: [-22, -22, 69], axis: [0, 0, 1], radius: 2.75 }
  };
  const readout = buildInspectorReadout({
    reference: { selectorType: "face", rowIndex: 0, displaySelector: "o1.1.f7", label: "Face o1.1.f7" },
    hitPointModelXYZ: [-22, -24.7, 72.5],
    selectorRuntime: runtime({ faces: [cyl] }),
    mode: SELECT_MODE.FEATURE
  });
  assert.equal(readout.entity.subtype, "cylindrical");
  const diameter = fieldValue(readout, "diameter");
  assert.equal(diameter.value, "5.5 mm");
  assert.equal(diameter.exact, true);
  const height = fieldValue(readout, "height");
  assert.equal(height.value, "5 mm");
  assert.equal(height.exact, false);
});

test("Feature edge: line endpoints = center ± half·direction (exact)", () => {
  const line = {
    curveType: "line", length: 5, center: [-30, -30, 72.5],
    bbox: { min: [-30, -30, 70], max: [-30, -30, 75] },
    params: { origin: [-30, -30, 70], direction: [0, 0, 1] }, dihedralDeg: 90
  };
  const readout = buildInspectorReadout({
    reference: { selectorType: "edge", rowIndex: 0, displaySelector: "o1.1.e1", label: "Edge o1.1.e1" },
    hitPointModelXYZ: [-30, -30, 72.5],
    selectorRuntime: runtime({ edges: [line] }),
    mode: SELECT_MODE.FEATURE
  });
  assert.equal(readout.entity.subtype, "line");
  assert.equal(fieldValue(readout, "endpoints").value, "(-30, -30, 70) → (-30, -30, 75)");
  assert.equal(fieldValue(readout, "endpoints").exact, true);
});

test("Feature edge: full circle vs arc by perimeter", () => {
  const circle = {
    curveType: "circle", length: 2 * Math.PI * 2.75,
    params: { center: [-22, -22, 75], axis: [0, 0, 1], radius: 2.75 }, dihedralDeg: null
  };
  const circleReadout = buildInspectorReadout({
    reference: { selectorType: "edge", rowIndex: 0, displaySelector: "o1.1.e10", label: "Edge o1.1.e10" },
    hitPointModelXYZ: [-19.25, -22, 75],
    selectorRuntime: runtime({ edges: [circle] }),
    mode: SELECT_MODE.FEATURE
  });
  assert.equal(circleReadout.entity.subtype, "circle");
  assert.equal(fieldValue(circleReadout, "diameter").value, "5.5 mm");

  const arc = {
    curveType: "circle", length: Math.PI * 2.75, // half turn
    params: { center: [0, 0, 0], axis: [0, 0, 1], radius: 2.75 }, dihedralDeg: null
  };
  const arcReadout = buildInspectorReadout({
    reference: { selectorType: "edge", rowIndex: 0, displaySelector: "o1.1.e11", label: "Edge o1.1.e11" },
    hitPointModelXYZ: [2.75, 0, 0],
    selectorRuntime: runtime({ edges: [arc] }),
    mode: SELECT_MODE.FEATURE
  });
  assert.equal(arcReadout.entity.subtype, "arc");
  assert.equal(fieldValue(arcReadout, "sweep").value, "180°");
});

test("Feature edge: dihedral angle always shown; tangent hint only below threshold", () => {
  const sharp = { curveType: "line", length: 5, center: [0, 0, 0], params: { direction: [1, 0, 0] }, dihedralDeg: 90 };
  const sharpReadout = buildInspectorReadout({
    reference: { selectorType: "edge", rowIndex: 0, displaySelector: "o1.1.e1", label: "Edge o1.1.e1" },
    hitPointModelXYZ: [0, 0, 0],
    selectorRuntime: runtime({ edges: [sharp] }),
    mode: SELECT_MODE.FEATURE
  });
  assert.equal(fieldValue(sharpReadout, "dihedral").value, "90°");
  assert.equal(fieldValue(sharpReadout, "blend"), undefined);

  const tangent = { ...sharp, dihedralDeg: 0 };
  const tangentReadout = buildInspectorReadout({
    reference: { selectorType: "edge", rowIndex: 0, displaySelector: "o1.1.e2", label: "Edge o1.1.e2" },
    hitPointModelXYZ: [0, 0, 0],
    selectorRuntime: runtime({ edges: [tangent] }),
    mode: SELECT_MODE.FEATURE
  });
  assert.equal(fieldValue(tangentReadout, "dihedral").value, "0°");
  assert.equal(fieldValue(tangentReadout, "blend").value, "tangent (fillet / blend)");
});

test("serializer produces stable, paste-ready text", () => {
  const line = {
    curveType: "line", length: 5, center: [-30, -30, 72.5],
    params: { direction: [0, 0, 1] }, dihedralDeg: 90
  };
  const readout = buildInspectorReadout({
    reference: { selectorType: "edge", rowIndex: 0, displaySelector: "o1.1.e1", label: "Edge o1.1.e1" },
    hitPointModelXYZ: [-30, -30, 72.5],
    selectorRuntime: runtime({ edges: [line] }),
    mode: SELECT_MODE.FEATURE
  });
  assert.equal(serializeInspectorReadout(readout), [
    "Cursor: (-30, -30, 72.5) mm",
    "Edge o1.1.e1",
    "@cad[models/caster.step#o1.1.e1]",
    "Curve: line",
    "Length: 5 mm",
    "Direction: +Z",
    "Endpoints: (-30, -30, 70) → (-30, -30, 75) mm",
    "Dihedral: 90°"
  ].join("\n"));
});

test("refToken is the clean @cad token (no summary suffix)", () => {
  const readout = buildInspectorReadout({
    reference: { selectorType: "face", rowIndex: 0, displaySelector: "o1.1.f7", label: "Face o1.1.f7" },
    hitPointModelXYZ: [0, 0, 0],
    selectorRuntime: runtime({ faces: [{ surfaceType: "plane", area: 1, center: [0, 0, 0] }] }),
    mode: SELECT_MODE.FEATURE
  });
  assert.equal(inspectorReadoutRefToken(readout), "@cad[models/caster.step#o1.1.f7]");
});

test("whole-model Part readout: from assembly part render data", () => {
  const part = {
    id: "o1.3",
    occurrenceId: "o1.3",
    name: "fork",
    bounds: { min: [-20, -10, 0], max: [20, 10, 60] },
    matrixWorld: { elements: [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 5, 0, 25, 1] }
  };
  const readout = buildPartReadoutFromAssemblyPart({ part, cadPath: CAD_PATH, cursorXyz: [1, 2, 3] });
  assert.equal(readout.entity.kind, "part");
  assert.equal(readout.entity.label, "fork");
  assert.equal(readout.entity.refToken, "@cad[models/caster.step#o1.3]");
  assert.equal(fieldValue(readout, "size").value, "40 × 20 × 60");
  assert.equal(fieldValue(readout, "placement").value, "(5, 0, 25)");
  assert.deepEqual(readout.cursor.xyz, [1, 2, 3]);
});

test("whole-model Part readout: null part → entity null, cursor preserved", () => {
  const readout = buildPartReadoutFromAssemblyPart({ part: null, cadPath: CAD_PATH, cursorXyz: null });
  assert.equal(readout.entity, null);
  assert.equal(readout.cursor.onSurface, false);
});

test("availableSelectModesFor drops Part inside a part", () => {
  assert.deepEqual(availableSelectModesFor({ insidePart: false }), [SELECT_MODE.PART, SELECT_MODE.FEATURE]);
  assert.deepEqual(availableSelectModesFor({ insidePart: true }), [SELECT_MODE.FEATURE]);
});
