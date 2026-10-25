---
name: memr
description: "Render deterministic caption memes with memr: classic top/bottom shouting (Anton capitals + black outline) and modern formats (Inter sans, preserved case, no outline, slot layouts for 2-panel/4-panel/three-line templates). Use for meme requests, template fetch/caching, style or config precedence, or machine-readable --json render reports."
---

# memr (repo-shipped skill)

`memr` renders classic and modern caption memes locally: it owns caption
typography and template caching, and does not call a third-party renderer.
Source repo: `~/byteowlz/memr`, hosted on forgejo `wismut/memr`
(ssh://git@forgejo/wismut/memr.git); CLI `src/memr.py`, catalog `templates.json`,
layout classes `layouts.json`, fonts Anton/Inter both OFL.

## Setup

```bash
# if the repo is not on this machine (other machines share the forgejo remote):
# git clone ssh://git@forgejo/wismut/memr.git ~/byteowlz/memr
cd ~/byteowlz/memr && just install   # symlink to ~/.local/bin/memr
memr doctor                          # font, catalog, cache, Pillow preflight
```

## Commands

| command | intent |
| --- | --- |
| `memr render TEMPLATE` | primary verb: captions onto a template |
| `memr templates` | catalog ids, cached/fetch state (`--ids` for scripts) |
| `memr fetch TEMPLATE` | cache a catalog id or blank-template URL |
| `memr layouts` | caption layout classes and per-template assignments |
| `memr config` | resolved settings plus the layer that supplied each value |
| `memr doctor` | preflight checks |
| `memr schema config\|output` | JSON schema for validation |
| `memr completions bash\|zsh\|fish` | shell completion code |
| `memr version` | version and resolved paths |

## Formats

Ink families (`--style`, config `[style] preset`):

| style | font | case | outline | type size |
| --- | --- | --- | --- | --- |
| classic (default) | Anton | capitals | black 0.083 of pointsize | 0.10 of width |
| modern | Inter | preserved | none | 0.075 of width |
| quiet | Inter | preserved | none | 0.055 of width |

Layout classes (`memr layouts`): `single-bottom`, `stack-2` (classic top/bottom
bands), `stack-3`, `panel-2-row` (Drake's two stacked rows), `panel-2-col`,
`grid-4` (2x2 Anakin-Padme panels). Assignment order: curated id → template
`lines` → supplied caption count → `stack-2` fallback.

Line advance = pointsize × style line ratio: classic 1.20, modern 1.06, quiet
1.10. Stacked caption lines keep a readable vertical gap rather than touching.

Edge inset = pointsize × margin_ratio: classic 0.25 hugs the frame (~4% of
height); structured panel classes center captions in their region. Fill + outline
stay wholly inside the canvas; never clip ascenders, descenders or ellipsis.
These classic values (line 1.20, margin 0.25) are user-approved: do not drift
them without an explicit request.

## Caption placement

- `-t/--top` targets slot 0; `-b/--bottom` targets the final slot (classic pair)
- repeated `-l/--line TEXT` fills slots 0..n in order for multi-line/panel
  templates; `--line` never mixes with `-t/-b` (`caption_conflict`, exit 2)
- a caption string of `-` reads stdin (one only)
- captions beyond the layout slot count exit 2 (`captions_exceed_layout`);
  two captions on one slot exit 2 (`slot_conflict`)
- `--pointsize` is a *starting* size; auto-fit still shrinks to fit the slot

## Recipes

```bash
# classic meme
memr render interesting -t "i don't always do satire..." \
  -b "but when i do, it's good natured, clothed satire."

# modern, preserved-case sans with an outline-free panel layout
memr render drake --style modern -l "left on unread" -l "left on read"

# three-line structured template
memr render pigeon --style modern -l engineer -l powerpoint -l "is this photoshop?"

# custom template image + machine report
memr render ~/Pictures/photo.jpg -t "top" -b "bottom" -o out.png --json

# caption from a pipe
echo "you had one job" | memr render pigeon -t - -b "signed off"
```

## Config precedence

flags > `--config PATH` > `MEMR_*` env > `./.memr.toml` > `~/.config/memr
/config.toml` (created with defaults on first run). `memr config --json` reports
`values` and per-key `sources` (`flag`, `env:MEMR_SCALE`, `--config`, `local`,
`global`, `style`, `default`) so precedence is auditable, not assumed.

Supported env: `MEMR_SCALE`, `MEMR_POINTSIZE_RATIO`, `MEMR_STROKE_RATIO`,
`MEMR_LINE_RATIO`, `MEMR_MARGIN_RATIO`, `MEMR_BLOCK_RATIO`,
`MEMR_MIN_POINTSIZE`, `MEMR_UPPERCASE`, `MEMR_JPEG_QUALITY`, `MEMR_FONT`,
`MEMR_STYLE`, `MEMR_CACHE_DIR`.

## Contract and safety

- exit codes: 0 ok, 1 runtime, 2 usage, 3 refused overwrite (use `--force`)
- `--json` stdout is one parseable document on success **and** failure,
  with `ok`, `command`, `version`, and `error.code/message` on failure
- success report has `layout.class`, `settings.style`, `text.lines`, and
  `captions.slots[]` with `lines`, `pointsize`, `stroke`, `advance`, `block`,
  `region`, `ink_y` — audit wraps and placement instead of guessing
- default output is `./meme-<template>-<hash8>.jpg`, deterministic per input

## Templates and licensing

Template photos are mostly third-party copyrighted works. They stay only in
`~/.cache/memr/templates` and must never be committed to a repo or published.
`templates.json` is metadata only (regenerate with `scripts/update-catalog.py`).
Anton and Inter ship with their OFL license files; any added font must too.

## Proof discipline

Any rendering/typography/layout change needs evidence:

```bash
just test     # offline, synthetic fixture; 52 contract checks
just smoke    # real catalog template (network on first cache miss)
```

Tests cover geometry, ink presence, config/style precedence, case, auto-fit,
overwrite guard, JSON-on-failure, stdin, catalog, completions, schemas, modern
and quiet styles, and layout slot separation. Visual quality claims need
inspectable render evidence (human eyeball or vision model), never a blind
assertion. Record tuning facts (stroke ordering, 2x supersampling) in the repo's
`docs/DESIGN.md` rather than repeating them per session.

## Boundaries

memr renders captions onto supplied templates; it does not choose wording,
judge humor, write credits/watermarks, or mutate external/shared state.
