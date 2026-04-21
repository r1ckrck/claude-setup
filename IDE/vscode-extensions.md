# VS Code Extensions — Curated List

A curated, opinionated list of VS Code extensions for a TypeScript / React / Next.js workflow. Not a dump — only extensions that earn their slot.

## Tier 1 — install these today

| Extension | What it does |
|---|---|
| **GitLens** | Inline blame, file history, branch comparison. Hover any line to see who/when/why. |
| **Error Lens** | Pulls error/warning messages out of squiggly underlines and shows them inline next to the offending code. |
| **Prettier** | Format on save. The de facto formatter. |
| **ESLint** | Lint on save. Catches bugs and enforces patterns. |
| **Pretty TypeScript Errors** | Reformats cryptic TS errors with syntax highlighting and structure. Huge for Next.js. |

## Tier 2 — recommended for TS/JS/React stack

| Extension | What it does |
|---|---|
| **ES7+ React/Redux/React-Native snippets** | `rfc` → full functional component skeleton. |
| **Tailwind CSS IntelliSense** | Class autocomplete with color previews. Skip if you don't use Tailwind. |
| **Path Intellisense** | Autocompletes file paths in imports and `<a href>`. |
| **Auto Rename Tag** | Edit an opening JSX/HTML tag, the closing tag updates automatically. |
| **Playwright Test for VSCode** (Microsoft) | Run/debug Playwright tests from a side panel, see traces inline. |

## Tier 3 — quality of life

| Extension | What it does |
|---|---|
| **Markdown All in One** | Keyboard shortcuts, TOC generation, list continuation. |
| **Code Spell Checker** | Catches typos in code, comments, strings. Configurable. |
| **TODO Tree** | Aggregates `TODO:` `FIXME:` `HACK:` comments into a sidebar tree. |
| **Thunder Client** | Lightweight Postman alternative inside VS Code. |
| **Image preview** | Hover image imports for a thumbnail. |
| **Indent Rainbow** | Color-codes indentation levels. Helps with deeply nested JSX/JSON. |

## Skip these (commonly recommended but redundant)

| Extension | Why skip |
|---|---|
| **Bracket Pair Colorizer** | Built into VS Code — enable `editor.bracketPairColorization.enabled`. |
| **Live Server** | Use your framework's dev server instead (Next.js, Vite, etc.). |
| **Material Icon Theme** | Pick one icon theme (e.g. `vscode-icons`) and stick with it. |
| **Settings Sync extensions** | VS Code has built-in Settings Sync — sign in with GitHub. |

## Install all of Tier 1 via CLI

```bash
code --install-extension eamodio.gitlens \
     --install-extension usernamehw.errorlens \
     --install-extension esbenp.prettier-vscode \
     --install-extension dbaeumer.vscode-eslint \
     --install-extension yoavbls.pretty-ts-errors
```

## Install all of Tier 2 via CLI

```bash
code --install-extension dsznajder.es7-react-js-snippets \
     --install-extension bradlc.vscode-tailwindcss \
     --install-extension christian-kohler.path-intellisense \
     --install-extension formulahendry.auto-rename-tag \
     --install-extension ms-playwright.playwright
```

## Install all of Tier 3 via CLI

```bash
code --install-extension yzhang.markdown-all-in-one \
     --install-extension streetsidesoftware.code-spell-checker \
     --install-extension Gruntfuggly.todo-tree \
     --install-extension rangav.vscode-thunder-client \
     --install-extension kisstkondoros.vscode-gutter-preview \
     --install-extension oderwat.indent-rainbow
```

## Notes on philosophy

- **Quality over quantity.** Most productive devs use 10–20 extensions. Too many slows VS Code and creates conflicts.
- **Add extensions when you hit a specific pain.** Don't install speculatively.
- **Periodically prune.** `Cmd+Shift+P` → "Show Installed Extensions" → disable anything you don't actively use.
