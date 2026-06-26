---
name: tui-design
description: Design and build modern, ergonomic, consistent TUIs for byteowlz tools (Rust + ratatui). Use when creating or overhauling a TUI - layout/IA, the Mode-vs-Key-Progression-vs-Overlay interaction model, the ANSI-token theme, command palette + chords, or reaching for the byteowlz-tui-kit crate.
---

# Designing byteowlz TUIs

## When to use this skill

Use when designing or implementing any **Rust + ratatui** TUI for a byteowlz tool — a new
`<tool>-tui` crate, a new screen in an existing one, or an overhaul of an ugly/cluttered
one. The goal is a family of TUIs that are **modern** (yazi ergonomics + Helix/opencode
looks), **ergonomic**, and **consistent** with each other.

This skill is the **judgment** layer. The **mechanism** lives in the `byteowlz-tui-kit`
crate (in `templates-repo/rust-workspace`) — reach for it instead of re-implementing
widgets/theme/dispatch.

> Read [CONTEXT.md](CONTEXT.md) first — it defines the vocabulary. The single most
> important term is **Mode vs Key Progression vs Overlay**, all ways to reach an
> **Action**. Confusing them is the root cause of mode explosion.

## The mental model — the leverage

The whole skill rests on one cut (your own `bitter-lesson-proof-project` rule):

- **Judgment → delegate it.** Layout choice, information hierarchy, "is this a mode or a
  command?" — these are taste. Capture them as *rules here*, don't hard-code them as
  per-tool heuristics.
- **Mechanism → build/normalize it once.** The theme tokens, the command palette, the
  prefix router, the terminal lifecycle — these live in `byteowlz-tui-kit` and are
  reused across every tool.

So: **an Action is data, not a mode. The kit renders; this skill decides.** The patterns
below are the decisions; `byteowlz-tui-kit` is the deterministic substrate that makes them
cheap.

## Workflow (do this order)

1. **Model the actions, not the modes.** List every thing the user can do as an `Action`
   with a label and a Key Path. *Then* ask, for each: is this reached by a direct key, a
   key progression (`s d`), the palette only, or does it genuinely need a sustained mode
   (text entry)? See [CONTEXT.md](CONTEXT.md) → "Derived rule". If you are about to add a
   Mode for an action, you want a Key Path or an Overlay, not a Mode.
2. **Decide the layout from the task, not a template.** What is the primary object? What
   does the user scan? What do they act on? That's your pane count. Three-pane is one
   answer, not the answer (rule IA1).
3. **Visualize before you build.** Render the proposed design as a before/after mock (HTML
   via the `visual-explainer` skill, or ANSI captured from a prototype) and confirm the
   hierarchy reads. Calibrate against yazi/Helix. **Do not start writing widget code
   before the layout passes the squint test.**
4. **Reach for the kit.** Depend on `byteowlz-tui-kit`; wire the `Theme`, register
   `Action`s, drive a `KeyRouter`, and render with the kit widgets. Add tool-specific
   widgets *as data over the kit*, not by forking it. See [REFERENCE.md](REFERENCE.md).
5. **Keep the TUI one surface over the Core.** Every TUI action is also a CLI subcommand
   over the same Core. The TUI is a view, never the only path (rule IA5).
6. **Verify it renders modern.** Run it, capture the frame, check it against the rules
   below. Structure compiling ≠ looks right.

## The pattern set

These are *derived defaults*, not laws. Each exists to kill a specific smell. Deviate on
purpose, with a stated reason — never by neglect.

### Visual (why they look ugly/dated)

- **V1 — Air over borders.** Separate regions with whitespace + padding, not boxes. A
  `bordered` block must earn its place. Default: no border, `Padding` inside. Border only
  the *focused* region, or a single hairline. *(kills: boxy, cramped, dated)*
- **V2 — One accent, muted base.** Palette = 3–4 grays + **one** accent + semantic state
  colors. Color carries *state*, never decoration. *(kills: ugly, clashing)*
- **V3 — Weight is hierarchy; color is state.** Bold = primary, `Muted`/dim = secondary.
  Most "ugly" is equal weight + color noise. *(kills: bad visual hierarchy)*
- **V4 — Padding inside, gaps between.** 1-space cell padding; spacer `Constraint`s between
  regions. *(kills: cramped, old)*
- **V5 — Hide the chrome.** One quiet status line for hints + counts. No busy toolbars.
  *(kills: cluttered)*
- **V6 — Graceful truncation.** `…` ellipsis, never mid-glyph cuts or chaotic wrap.
  *(kills: broken layout)*
- **V7 — One Theme as tokens, shared across every tool.** Code references tokens, never raw
  colors. *This is the consistency layer.* *(kills: cross-tool inconsistency)*

### Interaction (why ergonomics are bad / modes are a smell)

- **I1 — Command Palette is the type-to-discover path.** `:` / `Ctrl-P`, fuzzy, lists every
  Action with its Key Path. *(kills: broken palettes, undiscoverable actions)*
- **I2 — Sustained Modes only.** A Mode exists iff the whole keyboard becomes text entry
  (Search/Filter/Insert) or a mutually-exclusive tool (Visual). *"Sort/Select/Delete/Export
  mode" → smell → Action + Overlay or Key Path.* *(kills: mode explosion)*
- **I3 — Overlays, not Modes, for one-shots.** Confirm/pick/menu/form = transient overlay;
  own key handler; returns on Esc. Overlays stack. *(kills: mode explosion, ambiguous Esc)*
- **I4 — One verb = one key, everywhere.** `Enter` act · `Space` toggle-select · `d` delete
  · `e` edit · `/` filter · `?` help · `q`/`Ctrl-C` quit · `Tab` next pane. *(kills: inconsistency)*
- **I5 — Vim and arrows both.** `j/k/h/l gg G Ctrl-d/u` for believers; arrows/PgUp/Dn/Home/
  End for everyone else. Never force one. *(kills: bad ergonomics)*
- **I6 — Selection is first-class & orthogonal.** `Space` toggle, `V` range, `Ctrl-A` all —
  works in every list, independent of cursor. *(kills: bad ergonomics)*
- **I7 — Immediate, ephemeral feedback.** Status message ("3 deleted"), fades after a tick.
  Never a modal for success. *(kills: bad ergonomics)*
- **I8 — Escape always converges to Normal.** Esc peels one overlay/mode. Never trap the
  user. *(kills: bad ergonomics)*
- **I9 — Key Progressions are a feature, not a mode.** `dd`/`gg`/`s d`/space-leader are
  *transient* prefix states with an on-demand WhichKey hint — the keyboard-fast discovery
  path that coexists with the palette. This is the nvim muscle-memory you want, and it is
  *not* the mode-explosion smell. *(adds: power-user speed without mode cost)*

### Information architecture (why layout is bad)

- **IA1 — Layout follows the task, not a template.** Decide panes from the primary object,
  what you scan, what you act on. *Hard-coding 3-pane is the bug.* *(kills: bad layout,
  cargo-cult layouts)*
- **IA2 — Primary content gets the most space.** The thing you read = biggest region.
  *(kills: bad layout)*
- **IA3 — Progressive disclosure.** Show essentials; reveal detail on demand. *(kills: cluttered)*
- **IA4 — Empty states are a feature.** Never blank: "No items — press `a` to add."
  *(kills: bad UX)*
- **IA5 — TUI is one surface over a shared Core.** Every TUI action is also a CLI subcommand.
  *(kills: TUI-as-only-path, divergence)*

## The theme rule (load-bearing)

Tokens map to **named ANSI colors**, never raw RGB by default. The terminal (and its theme
manager — tinty, etc.) owns rendering, so every byteowlz tool matches the operator's
light/dark palette with zero per-tool config. An RGB override is a *stated exception* for a
deliberately branded tool. *Designing with raw hex is the smell.* See
[ADR-0002](docs/adr/0002-ansi-default-theme.md).

## See also

- [CONTEXT.md](CONTEXT.md) — the ubiquitous language (Mode / Key Progression / Overlay /
  Action / Token / …). Read first.
- [REFERENCE.md](REFERENCE.md) — the ratatui mechanism: `byteowlz-tui-kit` API, the
  reference `rust-tui` demo, gotchas, and a per-tool build checklist.
- [EXAMPLES.md](EXAMPLES.md) — worked designs: a list+detail tool, migrating mmry's 13
  modes down to ~2, and authoring a key-progression set.
- `templates-repo/rust-workspace/crates/rust-tui/` — a running reference built on the kit.
