---
name: tui-design
description: Design and build modern, ergonomic, consistent TUIs. Stack-agnostic judgment layer (layout/IA, the Mode-vs-Key-Progression-vs-Overlay interaction model, ANSI-token theming, palette + chords) with a Rust + ratatui binding via the byteowlz-tui-kit crate. Use when creating or overhauling any TUI, in any language.
---

# Designing modern TUIs

## When to use this skill

Use when designing or implementing **any TUI** — a new `<tool>-tui`, a new screen in an
existing one, or an overhaul of an ugly/cluttered one. The goal is TUIs that are
**modern** (yazi ergonomics + Helix/opencode looks), **ergonomic**, and **consistent**
with each other.

The judgment layer (this file + [CONTEXT.md](CONTEXT.md)) is **stack-agnostic** — the
rules apply equally to ratatui, Textual, bubbletea, or Ink. The **mechanism binding**
for the default byteowlz stack (Rust + ratatui) is the `byteowlz-tui-kit` crate in the
templates repo — <https://github.com/byteowlz/templates>, local clone
`~/byteowlz/templates` (`rust-workspace/crates/byteowlz-tui-kit`). In Rust, reach for it
instead of re-implementing widgets/theme/dispatch. On another stack, apply the same
rules with that stack's native equivalents.

> Read [CONTEXT.md](CONTEXT.md) first — it defines the vocabulary. The single most
> important term is **Mode vs Key Progression vs Overlay**, all ways to reach an
> **Action**. Confusing them is the root cause of mode explosion.

> **Judgment belongs in reusable rules; mechanism belongs in a shared library. An Action
> is data, not a mode.** This skill decides; the stack-native kit renders.

## Workflow (do this order)

1. **Model the actions, not the modes.** List every thing the user can do as an `Action`
   with a label and a Key Path. *Then* ask, for each: is this reached by a direct key, a
   key progression (`s d`), the palette only, or does it genuinely need a sustained mode
   (text entry)? See [CONTEXT.md](CONTEXT.md) → "Derived rule". If you are about to add a
   Mode for an action, you want a Key Path or an Overlay, not a Mode.
2. **Decide the layout from the task, not a template.** What is the primary object? What
   does the user scan? What do they act on? That's your pane count. Three-pane is one
   answer, not the answer (rule IA1).
3. **Visualize before you build — and verify the structure, not just the text.** Render
   the proposed design as a before/after mock (HTML via `visual-explainer`, or ANSI
   captured from a prototype) and confirm: distinct surface shades for bars vs content,
   titled panels with visible borders, and one accent on focus. Calibrate against
   yazi/Helix. **Do not start writing widget code until the layout has real visual
   structure** — a frame that is just text on one background has failed, even if the
   text is correctly colored.
4. **Reach for the kit.** Depend on `byteowlz-tui-kit`; wire the `Theme`, register
   `Action`s, drive a `KeyRouter`, and render with the kit widgets. Add tool-specific
   widgets *as data over the kit*, not by forking it. See [REFERENCE.md](REFERENCE.md).
5. **Keep the TUI one surface over the Core.** Every TUI action is also a CLI subcommand
   over the same Core. The TUI is a view, never the only path (rule IA5).
6. **Snapshot the screens.** Add backend-level snapshot tests (ratatui `TestBackend` +
   `insta`, or the stack's equivalent) for normal, focused, overlay, empty, and 80×24
   states. See [REFERENCE.md](REFERENCE.md) → Testing.
7. **Verify it renders modern — actually look at the frame.** Run it, capture the frame,
   and check it against the rules: are there distinct surface shades (bar fills vs
   content)? titled panels with borders? one accent on the active panel/focus row?
   **Capturing the bytes is not enough** — render and eyeball it. The reference demo was
   once shipped with a flat void of white-on-black text because structure was claimed but
   never verified; don't repeat that. Structure compiling ≠ looks right.

## The pattern set

These are *derived defaults*, not laws. Each exists to kill a specific smell. Deviate on
purpose, with a stated reason — never by neglect.

### Visual (why they look ugly/dated)

- **V1 — Thin styled borders + subtle fills, not boxes and not a void.** Draw each region
  inside a titled, rounded-border panel; fill header/status **bars** with a dark surface
  token distinct from the content bg. The contrast between the content surface and the
  bar fill *is* the structure. Avoid the two failure modes equally: heavy double-boxes
  (old mmry) **and** a borderless sea of floating text (the void). *(kills: boxy/dated,
  AND the flat/unstructured look)*
- **V2 — One accent, muted base.** Palette = 3–4 grays + **one** accent + semantic state
  colors. Color carries *state*, never decoration. *(kills: ugly, clashing)*
- **V3 — Weight is hierarchy; color is state.** Bold = primary, `Muted`/dim = secondary.
  Most "ugly" is equal weight + color noise. *(kills: bad visual hierarchy)*
- **V4 — Padding inside, gaps between.** 1-space cell padding inside panels; a spacer
  column between side-by-side panels. Tight edges = dated. *(kills: cramped, old)*
- **V5 — Hide the chrome.** One quiet status line for hints + counts. No busy toolbars.
  *(kills: cluttered)*
- **V6 — Graceful truncation.** `…` ellipsis, never mid-glyph cuts or chaotic wrap.
  *(kills: broken layout)*
- **V7 — One Theme as tokens, shared across every tool.** Code references tokens, never raw
  colors. *This is the consistency layer.* *(kills: cross-tool inconsistency)*
- **V8 — Degrade gracefully.** Respect `NO_COLOR` (weight/spacing must carry the hierarchy
  alone); look right on light *and* dark terminal themes (ANSI tokens give you this for
  free — verify it); glyphs beyond ASCII need a plain fallback (no nerd-font requirement);
  no tty → the CLI surface is the answer (IA5), never a broken TUI. *(kills: works-on-my-
  terminal)*

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
- **I10 — Mouse is supported, never required.** Scroll-wheel scrolls the hovered list,
  click focuses a pane, click selects a row, double-click = `Enter`. Every mouse action
  has a keyboard path; no mouse-only affordances. *(adds: casual-user ergonomics without
  keyboard cost)*
- **I11 — Errors have one home each.** Recoverable/background errors → status line in the
  `Danger` token (ephemeral, like I7); blocking errors that need a decision → a Confirm/
  message Overlay; never a panic, never a corrupted frame, never silence. *(kills:
  invisible failures, terminal-wrecking crashes)*

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
- `rust-tui` — a running reference built on the kit:
  <https://github.com/byteowlz/templates> → `rust-workspace/crates/rust-tui`
  (local: `~/byteowlz/templates/rust-workspace/crates/rust-tui`).
