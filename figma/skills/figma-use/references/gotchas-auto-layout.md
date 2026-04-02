# Gotchas: Auto Layout and Sizing

> Part of the [use_figma skill](../SKILL.md). Load when working with auto-layout, sizing modes, or nested frames.
> Covers: FILL/HUG ordering, resize() behavior, layoutGrow, grid layout, sections.

## `layoutSizingVertical`/`layoutSizingHorizontal` = `'FILL'` requires auto-layout parent FIRST

```js
// WRONG — setting FILL before the node is a child of an auto-layout frame
const child = figma.createFrame()
child.layoutSizingVertical = 'FILL'  // ERROR: "FILL can only be set on children of auto-layout frames"
parent.appendChild(child)

// CORRECT — append to auto-layout parent FIRST, then set FILL
const child = figma.createFrame()
parent.appendChild(child)            // parent must have layoutMode set
child.layoutSizingVertical = 'FILL'  // Works!
```

## HUG parents collapse FILL children

A `HUG` parent cannot give `FILL` children meaningful size. If children have `layoutSizingHorizontal = "FILL"` but the parent is `"HUG"`, the children collapse to minimum size. The parent must be `"FILL"` or `"FIXED"` for FILL children to expand. This is a common cause of truncated text in select fields, inputs, and action rows.

```js
// WRONG — parent hugs, so FILL children get zero extra space
const parent = figma.createFrame()
parent.layoutMode = 'HORIZONTAL'
parent.layoutSizingHorizontal = 'HUG'
const child = figma.createFrame()
parent.appendChild(child)
child.layoutSizingHorizontal = 'FILL'  // collapses to min size!

// CORRECT — parent must be FIXED or FILL for FILL children to expand
const parent = figma.createFrame()
parent.layoutMode = 'HORIZONTAL'
parent.resize(400, 50)
parent.layoutSizingHorizontal = 'FIXED'  // or 'FILL' if inside another auto-layout
const child = figma.createFrame()
parent.appendChild(child)
child.layoutSizingHorizontal = 'FILL'  // expands to fill remaining 400px
```

## `layoutGrow` with a hugging parent causes content compression

```js
// WRONG — layoutGrow on a child when parent has primaryAxisSizingMode='AUTO' (hug)
// causes the child to SHRINK below its natural size instead of expanding
const parent = figma.createComponent()
parent.layoutMode = 'VERTICAL'
parent.primaryAxisSizingMode = 'AUTO'  // hug contents
const content = figma.createFrame()
content.layoutMode = 'VERTICAL'
content.primaryAxisSizingMode = 'AUTO'
parent.appendChild(content)
content.layoutGrow = 1  // BUG: content compresses, children hidden!

// CORRECT — only use layoutGrow when parent has FIXED sizing with extra space
content.layoutGrow = 0  // let content take its natural size
// OR: set parent to FIXED sizing first
parent.primaryAxisSizingMode = 'FIXED'
parent.resizeWithoutConstraints(300, 500)
content.layoutGrow = 1  // NOW it correctly fills remaining space
```

## `resize()` resets `primaryAxisSizingMode` and `counterAxisSizingMode` to FIXED

`resize(w, h)` silently resets **both** sizing modes to `FIXED`. If you call it after setting `HUG`, the frame locks to the exact pixel value you passed — even a throwaway like `1`.

```js
// WRONG — resize() after setting sizing mode overwrites it back to FIXED
const frame = figma.createComponent()
frame.layoutMode = 'VERTICAL'
frame.primaryAxisSizingMode = 'AUTO'  // hug height
frame.counterAxisSizingMode = 'FIXED'
frame.resize(300, 10)  // BUG: resets BOTH axes to 'FIXED'! Height stays at 10px forever.

// ESPECIALLY DANGEROUS — throwaway values when you only care about one axis
const comp = figma.createComponent()
comp.layoutMode = 'VERTICAL'
comp.layoutSizingHorizontal = 'FIXED'
comp.layoutSizingVertical = 'HUG'
comp.resize(280, 1)  // BUG: "I only want width=280" but this locks height to 1px!
// HUG was reset to FIXED by resize(), frame is now permanently 280×1

// CORRECT — call resize() FIRST, then set sizing modes
const frame = figma.createComponent()
frame.layoutMode = 'VERTICAL'
frame.resize(300, 40)  // use a reasonable default, never 0 or 1
frame.counterAxisSizingMode = 'FIXED'  // keep width fixed at 300
frame.primaryAxisSizingMode = 'AUTO'   // NOW set height to hug — this sticks!
// Or use the modern shorthand (equivalent):
// frame.layoutSizingHorizontal = 'FIXED'
// frame.layoutSizingVertical = 'HUG'
```

**Rule of thumb**: Never pass a throwaway/garbage value (like `1` or `0`) to `resize()` for an axis you intend to be `HUG`. Either call `resize()` before setting sizing modes, or use a reasonable default that won't cause visual bugs if the mode reset goes unnoticed.

## Grid layout with mixed-width rows causes overlaps

```js
// WRONG — using a single column offset for rows with different-width items
// e.g. vertical cards (320px) and horizontal cards (500px) in a 2-row grid
for (let i = 0; i < allCards.length; i++) {
  allCards[i].x = (i % 4) * 370  // 370 works for 320px cards but NOT 500px cards!
}

// CORRECT — compute each row's spacing independently based on actual child widths
const gap = 50
let x = 0
for (const card of horizontalCards) {
  card.x = x
  x += card.width + gap  // use actual width, not a fixed column size
}
```

## Sections don't auto-resize to fit content

```js
// WRONG — section stays at default size, content overflows
const section = figma.createSection()
section.name = "My Section"
section.appendChild(someNode) // node may be outside section bounds

// CORRECT — explicitly resize after adding content
const section = figma.createSection()
section.name = "My Section"
section.appendChild(someNode)
section.resizeWithoutConstraints(
  Math.max(someNode.width + 100, 800),
  Math.max(someNode.height + 100, 600)
)
```

## `counterAxisAlignItems` does NOT support `'STRETCH'`

```js
// WRONG — 'STRETCH' is not a valid enum value
comp.counterAxisAlignItems = 'STRETCH'
// Error: Invalid enum value. Expected 'MIN' | 'MAX' | 'CENTER' | 'BASELINE', received 'STRETCH'

// CORRECT — use 'MIN' on the parent, then set children to FILL on the cross axis
comp.counterAxisAlignItems = 'MIN'
comp.appendChild(child)
// For vertical layout, stretch width:
child.layoutSizingHorizontal = 'FILL'
// For horizontal layout, stretch height:
child.layoutSizingVertical = 'FILL'
```
