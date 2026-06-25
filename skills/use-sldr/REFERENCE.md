# sldr reference

Full detail behind `SKILL.md`. Names are fuzzy-matched and file extensions are optional everywhere — `sldr build talk`, `sldr open intro`, etc. Ambiguity or a miss fails loud with the candidates listed.

## Directories

- `~/sldr/slides/` — slide markdown files (subdirectories allowed; reference as `ai/intro`).
- `~/sldr/playlists/` — playlist TOML files (the deck definitions).
- `~/sldr/presentations/` — build output.
- `~/sldr/flavors/`, `~/sldr/layouts/` — your library's flavors and layouts (override the built-ins by name).
- `~/.config/sldr/` — `config.toml` plus extra flavor/layout/scaffold dirs. Resolution order is library → config dirs → built-ins.

## Commands

- `sldr init` — create the library tree, install bundled flavors/scaffolds and the reference deck (`sldr build reference` to see every layout).
- `sldr new <name> --scaffold <s> --dir <subdir>` — create a slide from a scaffold (a pre-filled starter); `{{title}}`/`{{name}}` are substituted from the slide name. `sldr ls scaffolds` for the list — e.g. `translated-figure` scaffolds a bilingual content+image slide done right (shared image, per-language `::content::`, `translations` chrome).
- `sldr slides create` — batch-create slide files from JSON on stdin (or `--file`). The **agent-native authoring path** — no hand-written markers. Per slide: `{"name","title","layout","content"}` plus optional chrome (`subtitle`, `source`, `source_url`, `footer`) and a `translations` map. The map `{"de":{"title":…,"subtitle":…,"source":…,"content":…}}` emits both the `translations.<lang>` chrome frontmatter **and** the `::lang:<lang>::` body blocks for you, and auto-pairs per-language text with `::content::` when the shared `content` carries an `::image::`. Flags: `--dry-run`, `--json`, `--force`.
- `sldr playlist create` — make a playlist from JSON on stdin (or `--file`, or `--from-dir <dir> --name <n>`). Minimal JSON: `{"name":"talk","title":"My Talk","slides":["intro","point","end"]}`. Optional: `"flavor"`, `"description"`.
- `sldr add <playlist> <slides>` / `sldr rm <playlist> <slides>` — edit a playlist's slide list.
- `sldr build <playlist>` — flags: `--flavor <a,b,c>` (first active, rest embed for the `T` switcher), `--lang <a,b>` (embed languages, `L` switcher), `--single-file`, `--output <dir>`, `--pdf`, `--pptx`.
- `sldr watch <playlist>` — live-reload dev server. Flags: `--flavor`, `--port`, `--host 0.0.0.0` (expose on the LAN — prints reachable URLs).
- `sldr open <playlist|.sldr>` — open a built deck in the browser; a `.sldr` bundle is extracted, rebuilt, and presented.
- `sldr bundle <playlist>` — pack the editable sources into a portable `.sldr` (a plain zip). Flags mirror build (`--flavor`, `--lang`, `--output`).
- `sldr export <playlist> --format pdf|pptx` — exit doors. **PDF** is print-to-PDF. **PPTX** is *native, editable* OOXML by default — each slide's chrome + body become real PowerPoint placeholders/pictures (square bullets, bold/italic, per-language `--lang` all preserved). `--flatten` falls back to the lossy screenshot-per-slide path; `--template --flavor X` emits just theme + masters (no slides) to author new branded slides in PowerPoint. Native PPTX covers the layouts that declare export zones (today: `framed`, `two-cols`, `image-left`/`image-right`); others are named in a fail-loud message pointing to `--flatten`.
- `sldr import <file.pptx>` — round-trip a sldr-generated `.pptx` back into slide markdown (the inverse of native export; layout, chrome, bulleted body, and images reconstructed). Refuses decks sldr didn't generate.
- `sldr preview <slide>` / `sldr sample [--flavor]` — quick single-slide / sample-deck preview.
- `sldr ls slides|playlists|flavors|layouts|scaffolds` — list names. `sldr show layout <name>` / `sldr show flavor <name>` — print the *source* a name resolves to (the authored `.html`/`.toml`, built-in or user override; honors the build's resolution order; source to stdout, origin to stderr, `--json` for both). Use it to learn the format, copy a starting point, or see what a name really resolves to.
- `sldr search <query>` · `sldr config` · `sldr serve`.

## Slide frontmatter

```markdown
---
title: Headline               # chrome headline (framed layouts) + ls/search label
subtitle: smaller line        # chrome subheadline (framed layouts)
layout: framed                # which layout (default: "default")
source: "Article title | Site"   # web-clipping attribution line (framed layouts)
source_url: https://…            # makes the source line a link
footer: "© My Org"               # per-slide footer; overrides the flavor's default
align: left|center|right         # horizontal override
valign: top|center|bottom        # vertical override
tags: [topic, demo]              # for ls/search
translations:                    # optional: per-language chrome (see below)
  de:
    title: Überschrift
    subtitle: kleinere Zeile
    source: "Artikel | Seite"
---
body markdown…
```

`title`/`subtitle`/`source`/`footer` are read by the **framed** layouts as chrome slots; plain layouts render the markdown body and ignore them (use a markdown `#`/`##` heading there instead).

**Translating chrome.** `--lang` swaps the body (`::lang:xx::`) *and* the chrome. Top-level `title`/`subtitle`/`source`/`source_url`/`footer` are the default language; an optional `translations.<lang>` block overrides them per language, and any omitted field falls back to the top-level value. Building a non-default language for a slide that has chrome but no `translations` block warns loudly and falls back — never a silent wrong-language headline. (It's the frontmatter analog of the body's `::lang:xx::`.)

## Body markers

Split a slide's body for column/image layouts. A marker must stand alone on its own line, outside code fences:

- `::left::` / `::right::` → two-column layouts (`two-cols`, `framed-cols`, `versus`, …).
- `::content::` / `::image::` → content + image layouts (`image-left`, `image-right`, `framed-image`).
- `::left::` / `::right::` also drive `framed-scatter` (article left, image collage right) and `versus`.
- `::lang:xx::` → per-language **body** sections in one file (e.g. `::lang:en::`, `::lang:de::`). Content before the first marker is shared by every language. Build a language with `--lang xx`; a missing language warns and falls back to the deck default. (Framed **chrome** translates via the frontmatter `translations:` block — see *Slide frontmatter*.)

**Marker/layout match is checked.** If a layout has an image or column slot but the body lacks the matching markers (e.g. `framed-image`/`image-left` with no `::content::`/`::image::`, or a two-column layout with no `::left::`/`::right::`), the build warns loudly — naming the slide, layout, and expected markers — instead of silently dropping the image into the text column. (Letting a split body fall into a *plain* layout is intentional graceful degradation and does not warn.) A **stray** marker that doesn't form a pair (a lone `::content::`, a marker on a single-block layout) is **stripped from the output and reported** — so it never renders as literal `::content::` text. Only the four split markers above are special; anything else is plain text.

## Images, diagrams & graphics

- **Images:** `![alt](media/x.png)` relative to the slide file. Embedded at build (no runtime dependency). PNG/JPG/GIF/WebP and **SVG** all work; SVG is inlined as vector.
- **Diagrams:** a ` ```mermaid ` code fence **renders as a diagram** (flowchart, sequence, state, xychart, …). Mermaid runs client-side from a bundled copy — fully offline, and inlined only into decks that actually use it. Don't expect a mermaid fence to show as code; it becomes the rendered diagram (a syntax error shows mermaid's error diagram, not raw text).
- **Vector / custom graphics:** the reliable path is an SVG **file** — `![](chart.svg)` — embedded at build. You can also drop raw `<svg>…</svg>` inline, or use a ` ```svg ` / ` ```html ` fence (passed through and rendered, not syntax-highlighted). Prefer the file reference for anything complex.
- **Charts from data:** author them as a mermaid `xychart-beta`, or generate an SVG and reference it. There's no "paste a Chart.js snippet" path — it's static HTML output.

## Layout catalog (use when)

These are the four `sldr ls layouts` categories. Each layout also carries a *register* tag — `classic` (predictable placement) or `expressive` (dramatic), plus `branded` for the framed family — author-declared in the layout file (`<!-- sldr:category … -->` / `<!-- sldr:tags … -->`). Pick by content shape; register is the taste filter. See them grouped with `sldr ls layouts`.

- `cover` — title slide, centered hero. · `section` — big centered divider. · `intro` — orientation paragraph. · `statement` — one oversized declaration (accent on bold/italic words). · `hero-stat` — one huge number + caption. · `contact` — closing slide, contact lines as chips. · `end` — minimal closer.
- `default` — heading + body, top-anchored. · `two-cols` / `two-cols-header` — two columns (`::left::`/`::right::`). · `pillars` — list items as editorial columns. · `agenda` — numbered run-of-show. · `timeline` — list items as milestones on a line. · `versus` — head-to-head columns with a VS badge. · `quote` — dramatic centered quote. · `terminal` — code framed as a terminal window. · `split-accent` — content + diagonal accent panel.
- `image` — full-bleed image (fills, may crop). · `image-center` — one image shown whole (uncropped), centered, no text. · `image-left`/`image-right` — image + content (`::content::`/`::image::`). · `feature-image` — image-dominant with a caption rail. · `image-grid`/`image-row`/`image-portraits`/`image-stack` — collages (one `![]()` per line; alt text becomes captions where shown).
- **Framed family** (persistent chrome — headline/subheadline/footer/source zones + flavor logos + flavor background, with a readability scrim on content): `framed` (body) · `framed-cols` (two-col body) · `framed-image` (content + image) · `framed-figure` (a single whole/centered image, chrome + logos) · `framed-gallery` (image grid) · `framed-scatter` (content/article on the left, a semi-chaotic overlapping image collage on the right) · `framed-cover` (title) · `framed-section` (divider) · `framed-full` (edge-to-edge media, optional source). Use these for branded decks; pair with a flavor that sets logos/background/footer.

Author your own layout: an HTML file with `{{slot}}` placeholders (`{{content}}`, `{{left}}`, `{{right}}`, `{{image}}`, `{{heading}}`, plus framed chrome slots `{{headline}}`/`{{subheadline}}`/`{{footer}}`/`{{source}}`) and an optional scoped `<style>` binding only to flavor tokens (`var(--sldr-*)`). Drop it in `~/sldr/layouts/<name>.html`; reference it as `layout: <name>`. Start from a built-in: `sldr show layout framed > ~/sldr/layouts/my-layout.html` gives you the real source to edit.

## Flavors

A flavor is `flavor.toml` (+ optional `flavor.css` escape hatch + an `assets/` dir) under `~/sldr/flavors/<name>/`. Key sections: `[colors]` (+ `[dark_colors]`), `[typography]`, `[background]` (`background_type = "color"|"gradient"|"image"|"svg"`, `value = …`; image/svg files in `assets/` are embedded), `[shape]`/`[shadow]`/`[motion]`/`[spacing]`, `[decoration]` (`effect = "stardust"|"aurora"|"grain"|"spotlight"|"bokeh"|"grid-pan"`), `[code] syntax_theme`, a top-level `footer = "…"`, and `[[logos]]` blocks (`file`, `x`/`y`/`width` as `%`, `layouts = [...]`). Restyle a whole deck by swapping the flavor; tokens are the contract, `flavor.css` is the unbounded escape hatch (promote recurring patterns into tokens, don't add speculatively).

The bundled flavors are installed to disk (`~/.config/sldr/flavors/`) on `sldr init` and are **editable seeds** — edit, rename, copy, or delete any of them; your library flavors in `~/sldr/flavors/` override the bundled ones by name. They are not sacred: `sldr init --force` re-installs/overwrites the bundled set, so it is always safe to hack on a copy and restore later. Read any flavor's resolved source with `sldr show flavor <name>` (origin reported on stderr).

Shipped flavors: `aurora` `blueprint` `neon-noir` `terracotta` `sakura` `midnight-gold` `acid-lab` `fjord` `kraft` `letterpress` `editorial-serif` `minimal-light` `monochrome` `signal` `swiss-grid` `technical-dark` `vellum` `coral` `brutalist-mono` `neo-grid-bold` `raw-grid`. (`sldr ls flavors` for the live list.)

## Fonts — ship them in the flavor

To render identically on any machine, the flavor should carry its own fonts. Put a `font_imports = ["assets/fonts.css"]` pointing at a local stylesheet whose `@font-face` rules reference local font files (or already-base64 data URIs) in `assets/`; sldr inlines them into the deck — no network at build or presentation, no reliance on installed fonts. A remote `font_imports = ["https://fonts.googleapis.com/…"]` also works (fetched and embedded at build, cached), but a local font is the robust choice.

## Output tiers & guarantees

- **Directory** (default) — `index.html` + media siblings in `assets/`. Browser-native; video streams; no size ceiling. Zip it to send.
- **`--single-file`** — everything inlined into one HTML. Universal handoff; warns past the data-URI media ceiling (~tens of MB).
- **`.sldr` bundle** (`sldr bundle`) — a plain zip of the *sources* (playlist, slides, flavors, layouts, media) + a manifest pinning the build axes. The exchange format for the editable work; `sldr open talk.sldr` rebuilds and presents it. Restylable on arrival.

Determinism: same inputs → byte-identical output (diff decks like code). Self-contained: a built deck needs no network at presentation time. Fail-loud: missing references error with searched paths and available names.

## Presenter keys

Arrows/Space/Enter navigate · `O` overview · `S` speaker notes · `F` fullscreen · `D` dark mode · `T` flavor switch (multi-flavor) · `L` language switch (multi-language) · `M` toggle decoration motion (overrides OS reduced-motion) · `E` edit mode · `Home`/`End`.
