# Gotchas: Text and Typography

> Part of the [use_figma skill](../SKILL.md). Load when creating text nodes, loading fonts, or setting typography.
> Covers: lineHeight/letterSpacing format, font style name probing.

## `lineHeight` and `letterSpacing` must be objects, not bare numbers

```js
// WRONG — throws or silently does nothing
style.lineHeight = 1.5
style.lineHeight = 24
style.letterSpacing = 0

// CORRECT
style.lineHeight = { unit: "AUTO" }                    // auto/intrinsic
style.lineHeight = { value: 24, unit: "PIXELS" }       // fixed pixel height
style.lineHeight = { value: 150, unit: "PERCENT" }     // percentage of font size

style.letterSpacing = { value: 0, unit: "PIXELS" }     // no tracking
style.letterSpacing = { value: -0.5, unit: "PIXELS" }  // tight
style.letterSpacing = { value: 5, unit: "PERCENT" }    // percent-based
```

This applies to both `TextStyle` and `TextNode` properties. The same rule applies inside `use_figma`, interactive plugins, and any other plugin API context.

## Font style names are file-dependent — probe before assuming

Font style names vary per provider and per Figma file. `"SemiBold"` and `"Semi Bold"` are different strings. Loading a font with the wrong style string **throws silently or errors** — there is no canonical list.

```js
// WRONG — guessing style names
await figma.loadFontAsync({ family: "Inter", style: "SemiBold" }) // may throw

// CORRECT — probe which style names are available
const candidates = ["SemiBold", "Semi Bold", "Semibold"]
for (const style of candidates) {
  try {
    await figma.loadFontAsync({ family: "Inter", style })
    // capture the one that works
    break
  } catch (_) {}
}
```

When building a type ramp script, always verify font styles against the target file before hardcoding them.
