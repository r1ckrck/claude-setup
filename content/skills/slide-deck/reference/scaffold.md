# Scaffold a new deck

Step-by-step playbook for creating a new deck inside `assistant/slides/`.

## Naming

- Kebab-case folder name: `slides/<deck-slug>/`
- No date prefix (unlike social posts — decks are topic-named, not time-stamped)
- Examples: `slides/bfl-automation/`, `slides/claude-visual-showcase/`, `slides/wcag-figma-plugin/`

## Steps

### 1. Create the folder

```bash
mkdir assistant/slides/<deck-slug>
```

### 2. Write `index.html`

Boilerplate — drop into `slides/<deck-slug>/index.html`. **The three `deck-*` meta tags are required** — the hosted landing page at `slides.nesh.studio` reads them to build the archive. Don't ship without them.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><deck title> — Arnesh Mandal</title>
<meta name="deck-title" content="<plain-language title for the index>">
<meta name="deck-date"  content="YYYY-MM-DD">
<meta name="deck-blurb" content="<one sentence, plain prose, ≤140 chars>">
<link rel="stylesheet" href="../shared/design-system.css">
<link rel="stylesheet" href="slides.css">
</head>
<body>
<div class="stage">
  <div class="deck">

    <section class="slide slide--dark">
      <!-- slide 1 content -->
    </section>

    <section class="slide slide--light">
      <!-- slide 2 content -->
    </section>

  </div>
</div>
<script src="../shared/core.js"></script>
</body>
</html>
```

Notes:

- `.stage > .deck > .slide` — no wrappers between `.deck` and `.slide`. `core.js` requires it.
- `core.js` sets `.active` on slide 0 at boot and toggles it on nav — don't hand-add it.
- Alternate `.slide--light` and `.slide--dark` for rhythm; both pull token-driven palettes.
- Title convention: `<deck title> — Arnesh Mandal` (matches existing decks). `deck-title` is the cleaner version that appears on the landing page.
- The three `deck-*` meta tags must sit immediately after `<title>`. The landing-page script reads them by regex; don't reorder.

### 3. Write `slides.css`

Starter — drop into `slides/<deck-slug>/slides.css`:

```css
/* <deck-slug> — deck-specific layouts only.
   Shared primitives (cards, flowchart, chrome) live in shared/design-system.css.
   Tokens (color, type, spacing) live in shared/tokens.css. */

/* Example: a deck-specific grid for slide 03 */
/*
.slide-03 .grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--s-32);
}
*/
```

Keep this file lean. If you find yourself writing chrome, cards, or flowchart styles here — they probably belong in `shared/design-system.css` instead (only if a second deck would use them).

### 4. Optional — write `CLAUDE.md`

Add only if the deck has content constraints worth pinning (slide list, things to never mention, author byline, etc.). Skip otherwise.

Template:

```markdown
# <deck-slug> — content rules

<one-line description of the deck>. Architecture, runtime, and styling contracts live in `/slides/CLAUDE.md`. **This file is content-only.**

## Slides
1. Title
2. ...

## Content constraints

- <hard rules about wording, naming, claims>
```

### 5. Verify

```bash
cd assistant/slides
python3 -m http.server 8765
# Open http://localhost:8765/<deck-slug>/ — slide 1 should render
```

Then optionally:

```bash
node qa/qa.js <deck-slug>
# Inspect qa/shots/<deck-slug>/ visually
```

## Checklist

- [ ] Folder created at `slides/<deck-slug>/`
- [ ] `index.html` links `../shared/design-system.css` + local `slides.css` + `../shared/core.js`
- [ ] Three meta tags present: `deck-title`, `deck-date`, `deck-blurb` — immediately after `<title>`
- [ ] DOM is `.stage > .deck > .slide` with no wrappers between
- [ ] `slides.css` exists (even if empty) so the link doesn't 404
- [ ] Deck loads in browser; `core.js` scales the viewport; keyboard nav works
- [ ] No console errors

## Common pitfalls

- **Forgot `core.js`** — slides render at raw 1920×1080 in the corner of the viewport instead of scaling.
- **Extra wrapper inside `.deck`** — `core.js` queries `.deck > .slide`; wrappers break it.
- **Loaded a raw font / hex** — go through `var(--font-*)` and `var(--text-*)` tokens.
- **SVG marker collision across slides** — every `<marker id="arr-…">` must be unique across the whole document (not just per SVG).
