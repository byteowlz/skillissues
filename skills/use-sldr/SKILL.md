---
name: use-sldr
description: Create, build, and share presentations with the sldr CLI — modular markdown slides, swappable layouts and flavors, self-contained HTML output. Use when making slides, building a talk or deck, working with sldr playlists/flavors/layouts, or asked to create a presentation.
---

# Using sldr effectively

## Quick start

```bash
sldr init                                                 # once: creates ~/sldr/{slides,playlists,flavors,layouts}
# write slide files in ~/sldr/slides/ (frontmatter + markdown body)
echo '{"name":"talk","title":"My Talk","slides":["intro","point","end"]}' | sldr playlist create
sldr build talk --flavor fjord                            # → ~/sldr/presentations/talk/ (self-contained)
sldr open talk
```

A slide file (`~/sldr/slides/point.md`):

```markdown
---
title: The one idea
subtitle: why it matters
layout: statement
---
This is **the** point.
```

## The mental model — the leverage

sldr factors a deck into four orthogonal things; that separation *is* the power:

- **Slide** — one markdown file (content). Choose its structure with `layout:` in frontmatter.
- **Layout** — structure (cover, two-cols, image-right, framed, …). Data files you can author yourself.
- **Flavor** — style (colors, fonts, background, logos). Swap the whole deck's look with one `--flavor`.
- **Playlist** — which slides, in what order: the deck definition.

Author a slide once; reuse it in any deck, restyle with any flavor, rebuild byte-identically.

## Effective use

- **Pick the layout to the content's shape**, not the reverse. One big claim → `statement`/`hero-stat`; a comparison → `versus`/`two-cols`; image + caption → `image-right`/`feature-image`; a wall of images → `image-grid`; a process → `timeline`/`agenda`. Branded decks (persistent header/footer/logos/background) → the `framed-*` family. Full catalog with "use when" in [REFERENCE.md](REFERENCE.md).
- **Frontmatter carries the chrome; markers carry structure.** `title`/`subtitle`/`source`/`source_url`/`footer` populate framed-layout slots. `::left::`/`::right::` and `::content::`/`::image::` split the body. `::lang:en::`/`::lang:de::` keep multilingual slides in one file.
- **Restyle, don't rewrite.** `sldr build deck --flavor X` re-skins everything. Embed several (`--flavor a,b,c`) for a runtime `T`-key switcher.
- **Flavors are editable files on disk — edit them freely.** The bundled flavors install to `~/.config/sldr/flavors/<name>/` on `sldr init`; your own live in `~/sldr/flavors/<name>/` (override the bundled ones by name). They are *seeds, not sacred*: edit, rename, copy, or delete any of them. To fork, copy a flavor dir (or `sldr show flavor X` into a new `flavor.toml`) and edit. Lost or want the originals back / refreshed after an sldr upgrade? `sldr init --force` re-installs the bundled set, overwriting in place. (Layouts work the other way: built-in, read with `sldr show layout X`; drop an HTML file in `~/sldr/layouts/` to add or override one.)
- **Make decks portable.** Outputs are self-contained (media embedded). Ship fonts *in the flavor* (local `font_imports`) so they render on any machine. Default output is a directory (media streams natively); `--single-file` inlines everything into one mailable HTML; `sldr bundle` packs the editable sources as a `.sldr`.
- **Read the error.** A missing slide/flavor/layout fails loud and lists what's available — the message *is* the fix. sldr never silently substitutes.
- **Verify visually.** Open or screenshot the deck before declaring done; structure passing ≠ looks right.

## Layout cheat sheet

- Title/section: `cover` `section` `intro` `statement` `hero-stat` `contact` `end`
- Body: `default` `two-cols` `two-cols-header` `pillars` `agenda` `timeline` `versus` `quote` `terminal` `split-accent`
- Image: `image` `image-left` `image-right` `feature-image` `image-grid` `image-row` `image-portraits` `image-stack`
- Branded (persistent chrome): `framed` `framed-cols` `framed-image` `framed-gallery` `framed-scatter` `framed-cover` `framed-section` `framed-full`

## Build & share

```bash
sldr ls slides|playlists|flavors|layouts     # discover what exists (names)
sldr show flavor aurora                      # read a flavor's/layout's actual source
sldr show layout framed > ~/sldr/layouts/mine.html  # …or fork it as a starting point
sldr build talk --flavor aurora --lang de    # build with a flavor + language
sldr build talk --single-file                # one portable HTML file
sldr watch talk --host 0.0.0.0               # live-reload preview, reachable on the LAN
sldr bundle talk                             # → talk.sldr (editable source bundle; open with `sldr open talk.sldr`)
sldr export talk --format pdf                # PDF/PPTX exit doors
```

## See also

- [REFERENCE.md](REFERENCE.md) — full CLI, frontmatter fields, the layout catalog with when-to-use, flavor authoring, output tiers, bundles, languages, fonts.
- [EXAMPLES.md](EXAMPLES.md) — complete worked decks (simple, branded/framed, multilingual, web-clipping).
