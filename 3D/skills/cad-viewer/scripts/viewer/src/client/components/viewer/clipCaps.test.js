import assert from "node:assert/strict";
import test from "node:test";

import {
  buildClipCapPlaneMaterial,
  buildClipCapStencilMaterials,
  clipCapColorForRecord,
  resolveClipCapColor,
  shouldRenderClipCaps,
  syncClipCapStyle
} from "cadjs/common/cadScene.js";

// Fake THREE.Color: only getHexString is needed by clipCapColorForRecord.
const color = (hex) => ({ getHexString: () => hex });

// Fake THREE: records MeshBasicMaterial options + supplies stencil-constant sentinels.
const THREE = {
  BackSide: "BackSide",
  FrontSide: "FrontSide",
  DoubleSide: "DoubleSide",
  AlwaysStencilFunc: "AlwaysStencilFunc",
  NotEqualStencilFunc: "NotEqualStencilFunc",
  IncrementWrapStencilOp: "IncrementWrapStencilOp",
  DecrementWrapStencilOp: "DecrementWrapStencilOp",
  ReplaceStencilOp: "ReplaceStencilOp",
  MeshBasicMaterial: class {
    constructor(opts = {}) {
      Object.assign(this, opts);
    }
  }
};

test("stencil mask materials: back increments, front decrements, no color/depth, clipped", () => {
  const plane = { id: "plane" };
  const { back, front } = buildClipCapStencilMaterials(THREE, plane);
  for (const m of [back, front]) {
    assert.equal(m.colorWrite, false);
    assert.equal(m.depthWrite, false);
    assert.equal(m.depthTest, false);
    assert.equal(m.transparent, true); // shares the transparent queue with the caps
    assert.equal(m.clipping, true);
    assert.deepEqual(m.clippingPlanes, [plane]);
    assert.equal(m.stencilWrite, true);
    assert.equal(m.stencilFunc, THREE.AlwaysStencilFunc);
  }
  assert.equal(back.side, THREE.BackSide);
  assert.equal(back.stencilZPass, THREE.IncrementWrapStencilOp);
  assert.equal(back.stencilFail, THREE.IncrementWrapStencilOp);
  assert.equal(back.stencilZFail, THREE.IncrementWrapStencilOp);
  assert.equal(front.side, THREE.FrontSide);
  assert.equal(front.stencilZPass, THREE.DecrementWrapStencilOp);
});

test("stencil mask materials: empty clippingPlanes when no plane", () => {
  const { back } = buildClipCapStencilMaterials(THREE, null);
  assert.deepEqual(back.clippingPlanes, []);
});

test("cap plane material: draws where stencil != 0, not clipped, double-sided", () => {
  const m = buildClipCapPlaneMaterial(THREE, "#abcdef");
  assert.equal(m.color, "#abcdef");
  assert.equal(m.side, THREE.DoubleSide);
  assert.equal(m.clipping, false);
  assert.equal(m.clippingPlanes, null);
  assert.equal(m.stencilWrite, true);
  assert.equal(m.stencilRef, 0);
  assert.equal(m.stencilFunc, THREE.NotEqualStencilFunc);
  assert.equal(m.stencilFail, THREE.ReplaceStencilOp);
  assert.equal(m.stencilZFail, THREE.ReplaceStencilOp);
  assert.equal(m.stencilZPass, THREE.ReplaceStencilOp);
  assert.equal(m.polygonOffset, true);
});

test("cap plane material: opacity drives transparency + depthWrite", () => {
  const full = buildClipCapPlaneMaterial(THREE, "#abcdef");
  assert.equal(full.transparent, true);
  assert.equal(full.opacity, 1);
  assert.equal(full.depthWrite, true); // opaque-looking cap occludes
  const dim = buildClipCapPlaneMaterial(THREE, "#abcdef", 0.035);
  assert.equal(dim.opacity, 0.035);
  assert.equal(dim.depthWrite, false); // dimmed cap does not occlude
});

test("syncClipCapStyle mirrors each part's opacity + visibility onto its cap", () => {
  const focused = { mesh: { visible: true }, material: { opacity: 1 } };
  const dimmed = { mesh: { visible: true }, material: { opacity: 0.035 } };
  const hidden = { mesh: { visible: false }, material: { opacity: 1 } };
  const cap = (record) => ({ visible: true, material: { opacity: 1, depthWrite: true }, userData: { cadClipCapRecord: record } });
  const caps = [cap(focused), cap(dimmed), cap(hidden)];
  const mask = (record) => ({ visible: true, userData: { cadClipCapRecord: record } });
  const masks = [mask(focused), mask(dimmed), mask(hidden)];
  const runtime = { capsGroup: { visible: true, children: caps }, clipCapStencilMeshes: masks };

  syncClipCapStyle(runtime);

  assert.equal(caps[0].material.opacity, 1);
  assert.equal(caps[0].material.depthWrite, true);
  assert.equal(caps[1].material.opacity, 0.035);
  assert.equal(caps[1].material.depthWrite, false);
  assert.equal(caps[1].visible, true); // dimmed but still shown
  assert.equal(caps[2].visible, false); // hidden part → cap off
  assert.equal(masks[2].visible, false); // hidden part → no stencil
});

test("syncClipCapStyle is a no-op when caps are inactive", () => {
  assert.doesNotThrow(() => syncClipCapStyle({ capsGroup: { visible: false, children: [] } }));
  assert.doesNotThrow(() => syncClipCapStyle({}));
});

test("shouldRenderClipCaps gate matrix", () => {
  const base = { enabled: true, displayMode: "solid", hasRecords: true, hasPlane: true };
  assert.equal(shouldRenderClipCaps(base), true);
  assert.equal(shouldRenderClipCaps({ ...base, enabled: false }), false);
  assert.equal(shouldRenderClipCaps({ ...base, displayMode: "wireframe" }), false);
  assert.equal(shouldRenderClipCaps({ ...base, hasRecords: false }), false);
  assert.equal(shouldRenderClipCaps({ ...base, hasPlane: false }), false);
  assert.equal(shouldRenderClipCaps(), false);
});

test("resolveClipCapColor darkens the theme surface, neutral fallback otherwise", () => {
  assert.equal(resolveClipCapColor({ baseTheme: { surface: "#ffffff" } }, 0.85), "#d9d9d9");
  assert.equal(resolveClipCapColor({ baseTheme: { surface: "#f4f4f5" } }, 0.85), "#cfcfd0");
  assert.equal(resolveClipCapColor({}), "#9ca3af");
  assert.equal(resolveClipCapColor({ baseTheme: { surface: "rgb(1,2,3)" } }), "#9ca3af");
});

test("clipCapColorForRecord reads the part's baseColor and darkens it", () => {
  assert.equal(clipCapColorForRecord({}, { baseColor: color("ffffff") }, 0.82), "#d1d1d1");
});

test("clipCapColorForRecord prefers baseColor over material.color (no hover flicker)", () => {
  const record = { baseColor: color("204060"), material: { color: color("ffffff") } };
  assert.equal(clipCapColorForRecord({}, record, 1), "#204060");
});

test("clipCapColorForRecord falls back to material.color when baseColor absent", () => {
  assert.equal(clipCapColorForRecord({}, { material: { color: color("112233") } }, 1), "#112233");
});

test("clipCapColorForRecord uses theme neutral for vertex-color parts (not white)", () => {
  const runtime = { baseTheme: { surface: "#ffffff" } };
  const record = { useVertexColors: true, baseColor: color("ffffff") };
  assert.equal(clipCapColorForRecord(runtime, record, 0.82), resolveClipCapColor(runtime, 0.82));
});

test("clipCapColorForRecord falls back to neutral when no color at all", () => {
  assert.equal(clipCapColorForRecord({}, {}), "#9ca3af");
});

test("clipCapColorForRecord clamps at the extremes", () => {
  assert.equal(clipCapColorForRecord({}, { baseColor: color("ffffff") }, 1), "#ffffff");
  assert.equal(clipCapColorForRecord({}, { baseColor: color("ffffff") }, 0), "#000000");
});
