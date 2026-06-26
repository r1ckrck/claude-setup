# Animations & Transitions

`python-pptx` and `pptxgenjs` have **no animation API**. Slide animations and transitions are
hand-authored OOXML `<p:timing>` inside each `slide{N}.xml`. Author them through the normal
unpack → edit XML → **validate** → pack workflow (see editing.md).

## Golden rule: validate, never eyeball
LibreOffice and python-pptx happily open malformed animation XML; **PowerPoint silently "repairs"
it** on open, stripping the offending animations. A clean LibreOffice render proves nothing. After
ANY animation / raw-XML edit, run the bundled XSD validator — the same schema PowerPoint checks at
open:

```bash
python scripts/office/validate.py output.pptx --original source.pptx
```

`--original` reports only NEW errors (filters pre-existing noise). **Focus on `ppt/slides/*` errors.**
Benign noise to ignore: `authors.xml`, `revisionInfo.xml`, `modernComment_*` (Microsoft-extension
parts not in the ISO schema). If slides validate clean, PowerPoint won't show the repair prompt.
`pack.py` runs this automatically — if you bypass it (e.g. you edited with python-pptx and saved),
run `validate.py` explicitly.

## Four structural rules that cause "PowerPoint repair" (XSD-invalid, but LO/python-pptx tolerate)
These four bit us repeatedly; each is invisible until PowerPoint opens the file.
1. **`<p:timing>` placement.** Within `<p:sld>` the child order is fixed:
   `cSld, clrMapOvr, transition, timing, extLst`. `timing` must come **before** any slide-level
   `<p:extLst>`. Appending it as the last child lands it *after* extLst on slides that have one → repair.
2. **Shapes come after group props.** `<p:spTree>` (and every `<p:grpSp>`) must start with
   `<p:nvGrpSpPr>` then `<p:grpSpPr>`; all shapes follow. Inserting a shape/group at index 0 (before
   those) → repair. Insert after `grpSpPr`.
3. **`<p:cTn id>` monotonic + unique.** Timing-node ids must strictly increase in document order.
   Allocate wrapper/parent ids **before** their child ids.
4. **`style.visibility` set needs a stCondLst.** A `<p:set>` animating `style.visibility` needs an
   inner `<p:cTn dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>`.
   (A `style.opacity` emphasis set does **not** — required children differ by effect type.)

## Best source of correct XML: PowerPoint itself
The surest way to match the schema is to apply the effect once in PowerPoint, unpack, and copy the
exact `<p:timing>` XML. Proven patterns:
- **Emphasis dim/undim:** `<p:set>` on `style.opacity` + paired
  `<p:animEffect filter="image" prLst="opacity: X">`, both targeting the same `spid`.
- **Move + scale (zoom to center):** `<p:anim calcmode="lin" valueType="num"><p:cBhvr additive="base">`
  on `ppt_x`/`ppt_y` (shape **center**, as a slide fraction — `0.5` = centre) and `ppt_w`/`ppt_h`
  (size, as a slide fraction). `<p:tav tm="0">` = from, `tm="100000">` = to; value is a `<p:strVal>`
  literal or formula (`#ppt_w*1.2`, `#ppt_x`). Microsoft-documented; reverse by animating back to
  `#ppt_x`/`#ppt_y`/`#ppt_w`/`#ppt_h`.
  **Editability caveat:** raw `<p:anim>` on `ppt_*` has no `presetClass`, so PowerPoint shows it as a
  **locked, non-editable custom motion** (and a position move reads as a "fly in/out" in the pane). If
  the deck must stay editable in PowerPoint's animation ribbon, use the native `<p:animScale>`
  (Grow/Shrink) + `<p:animMotion>` (motion path) effects, which map to gallery presets. Raw `ppt_*` is
  fine when the animation is playback-only.
- **Video play/stop:** `<p:cmd type="call" cmd="playFrom(0.0)">` (afterEffect) and `cmd="stop"`
  (clickEffect), `presetClass="mediacall"`. Each video needs a `<p:video><p:cMediaNode>` registration
  at the end of `<p:timing>`.
- **Show/hide on schedule:** `style.visibility` set to `visible`/`hidden`, `presetClass` entr/exit,
  `delay` in ms.
- **Click-step skeleton:** `mainSeq` → one `<p:par>` per click (outer `<p:cTn>` with
  `<p:cond delay="indefinite"/>` = wait-for-click → inner `<p:cTn delay="0">` → effects). First effect
  in a step = `nodeType="clickEffect"`, simultaneous = `withEffect`, auto-after = `afterEffect`. Close
  the `<p:seq>` with `<p:prevCondLst>`/`<p:nextCondLst>` (`onPrev`/`onNext` → `<p:sldTgt/>`) so the last
  click advances the slide.

## Gotchas (each cost a debug cycle)
- **Don't animate a group's transform to move its children.** Animating `ppt_w`/`ppt_x` on a
  `<p:grpSp>` distorts children unreliably across renderers. To move a media + its callouts as a rigid
  set, animate **each shape** with a shared pivot: scale ×k about the group's centre `C` and translate
  `C` to the target → per shape `ppt_x = 0.5 + k·(centre_x − C_x)`, `ppt_w = w·k` (fractions).
- **Zero-dimension shapes (connectors/lines) vanish if box-scaled.** A horizontal connector has
  height 0; animating `ppt_h → 0` collapses/drops it (a vertical one, `ppt_w → 0`). When per-shape
  scaling, **skip the degenerate dimension** (omit `ppt_w` if width ≈ 0, `ppt_h` if height ≈ 0) and
  animate only position + the non-zero dimension.
- **Make a callout APPEAR at a moved position without a "fly-in".** Two traps: (a) animating a shape's
  position at click-0 while its entrance is later **un-hides it early**; (b) deferring an *animated*
  move to the appear time makes the Appear read as a **Fly In** (PowerPoint merges entrance + motion
  into one fly). Fix: at the appear time, pair the visibility entrance with an **instant** position set
  — a `ppt_*` anim whose `from == to == target` (no interpolation) — so it pops in already at the
  target. Never animate position *into* an appearing shape.
- **Media bytes are safe** through python-pptx save and unpack/pack — copied verbatim (verify with
  md5 of `ppt/media/*`). The "image cannot be displayed" corruption seen on OneDrive came from
  PowerPoint re-saving + incremental cloud sync of a machine-generated file, not from generation.
  Mitigation: after editing, do a local **Save As** before re-uploading to OneDrive; make sure cloud
  files are fully downloaded (not 0-byte placeholders) before copying.
- **You can't verify playback locally.** LibreOffice PDF export renders a static/initial state, not
  the click sequence. Verify structure with `validate.py` + targeted asserts (ids monotonic, expected
  effect counts, every `spid` exists, `timing` before `extLst`); a human confirms feel in PowerPoint.
