---
name: drftr
description: Use this skill whenever a design folder (a directory containing design.toml) is involved, when the user mentions drftr, frames, blocks, sketching or blocking out a UI, wireframes, mockups, or wants to agree on a screen with you. drftr is a multi-frame design canvas built for human–agent agreement: the human points, comments, drags and approves in the studio; you read and write plain files (design.toml, review.toml, frames/*.blocks.json, frames/*.tsx, parts/, library/) through the `drftr` CLI and the folder. Never ask the human to describe a layout in prose when a blocks frame or a snapshot would be more precise.
license: MIT
---

# drftr — designing UI with a human, through files

A **design** is a folder. Everything in it is yours to read and edit; the
studio (a web app the human has open) live-reloads on every write and shows
you what the human did through the same files. The CLI is the fast path.

```
designs/<name>/
  design.toml            frames (id, src, size, canvas position, variants), flows, presets
  review.toml            comments (the human's queue for you), nudges, approvals — machine-written
  decisions.md           why an alternative won; append-only history
  notes.md               intent; read this first
  frames/<id>.blocks.json   a blocks frame: the sketch layer (default kind)
  frames/<id>.tsx           a TSX frame: real code on the design system
  parts/<name>.tsx       reusable components you write, placeable as part:<name>
  snapshots/             PNGs of frames — your eyes
```

Shared across designs, under the served root: `library/parts/<name>.tsx`
(+ `<name>.block.json`) and `library/templates/<name>.blocks.json`.

## The loop

```bash
drftr show <DESIGN> --json      # the whole picture: frames, approval, open comments, lint, snapshots
drftr review <DESIGN>           # open comments with anchors like home#workspace-list — your work queue
# … edit frames/*.blocks.json, frames/*.tsx, parts/ …
drftr lint <DESIGN>             # must be clean; --fix assigns missing block ids
drftr snapshot <DESIGN> [FRAME] # renders through the open studio into snapshots/; then LOOK at the PNGs
drftr comment reply <DESIGN> c3 "loosened the rows" --as agent:<you>
drftr comment status <DESIGN> c3 addressed
drftr context <DESIGN>          # who is looking at what right now (selection/presence)
```

Approval is the contract: `approved` frames are locked by source hash —
`drftr lint` fails if you change one. To propose a change to an approved
frame, add an alternative (`drftr frame add <DESIGN> home@b --rationale "…"`)
and let the human pick. Never edit `review.toml` by hand; use the CLI.

## Blocks frames (sketch layer) — prefer these for layout work

`frames/<id>.blocks.json` is a tree. Position is order in the parent plus
layout tokens; there are no pixel coordinates.

```json
{
  "schema": 1,
  "root": { "id": "root", "type": "stack", "props": { "gap": 6, "padding": 8 }, "children": [
    { "id": "header", "type": "stack", "props": { "direction": "row", "justify": "between", "align": "center" }, "children": [
      { "id": "title", "type": "heading", "props": { "text": "Workspaces", "level": 1 } },
      { "id": "new", "type": "button", "props": { "label": "New workspace", "icon": "plus" } }
    ]},
    { "id": "list", "type": "list", "props": { "items": ["oqto_refactor · 2h ago", "drftr · just now"] } },
    { "id": "cols", "type": "grid", "props": { "cols": 3 }, "children": [
      { "id": "stat-1", "type": "card", "props": { "title": "Sessions" }, "layout": { "span": 2 }, "children": [] },
      { "id": "stat-2", "type": "card", "props": { "title": "Errors" }, "children": [] }
    ]}
  ]}
}
```

- `id`: unique, `[a-z0-9-]+`; it is the `data-id` the human's comments point
  at, so keep ids stable when you restructure.
- `type`: a catalog type or `part:<name>`. Get the catalog with its prop specs
  from `schemas/blocks-catalog.json` in the drftr repo or
  `GET http://<server>/api/catalog`. Types: `stack grid card spacer separator
  heading text link button input textarea select checkbox switch badge list
  table tabs nav icon image avatar`. Unknown types and props are lint errors.
- `layout`: `w` (`auto|full|1/2|1/3|2/3|1/4|3/4|<n>px`), `h`
  (`auto|full|<n>px`), `span` (1–12, inside a grid), `grow` (bool).
- Containers: `stack` (`direction row|column`, `gap`, `padding`, `align`,
  `justify`, `wrap`, `surface none|card|muted`, `border`), `grid` (`cols`,
  `gap`), `card` (`title`, `padding`, `gap`). Only containers have `children`.
- Icons are lucide names in kebab-case (`arrow-right`).

When the human drags, resizes or retypes in the studio, this file changes;
read it again rather than assuming your last version.

## Parts and templates — how you extend the vocabulary

- A **part** is a TSX component: `parts/<name>.tsx` (this design) or
  `library/parts/<name>.tsx` (every design). Default-export a component;
  import only `react`, `lucide-react`, `@/components/ui/*`, `@/lib/utils`,
  `../parts/*`; put `data-id` on pointable elements; no inline styles, no
  `absolute`/`fixed`. Add `<name>.block.json` next to it so the studio shows
  a props form:
  `{"description": "Hero with title", "props": [{"name": "title", "kind": "text", "default": "Hi"}]}`
  (`kind`: `text|longtext|number|bool|enum|icon|items`, plus `min/max` or `values`).
  Place it with `{"id": "hero-1", "type": "part:hero", "props": {"title": "…"}}`.
- A **template** is a reusable subtree: `library/templates/<name>.blocks.json`
  = `{"name": "Login form", "description": "…", "root": {…}}`. Ids are
  regenerated on insert. Build these when you notice the same structure twice.

## TSX frames — the implementation layer

`drftr eject <DESIGN> <FRAME>` turns a blocks frame into `frames/<id>.tsx`
deterministically (same classes, same `data-id`s). From then on edit the
TSX directly; the same import rules as parts apply. Frames must stay under
~300 lines; split into `parts/`.

## Do / don't

- Do run `drftr lint` before telling the human you are done.
- Do look at `snapshots/*.png` after `drftr snapshot` — you cannot judge
  layout from JSON.
- Do propose 2–3 alternatives (`home@a`, `home@b`) with one-line rationales
  when the direction is open; the human picks in one click.
- Don't reconcile frames or comments by text or order — only by id.
- Don't hand-edit `review.toml`, `studio/vendor`, or approved frames.
- Don't write pixel positions; if a layout needs something blocks cannot
  express, eject to TSX and continue there.
