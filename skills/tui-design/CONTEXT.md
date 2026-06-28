# TUI design — ubiquitous language

This glossary defines the vocabulary the skill uses. It is **design language, not implementation detail** — no crate names, no struct fields, no ratatui calls. Those live in `REFERENCE.md`.

The single most important distinction: **Mode vs Key Progression vs Overlay**, all of them ways to reach an **Action**. Confusing these is the root cause of mode explosion.

## Core interaction units

**Action** — one named thing the user can do (`delete`, `edit`, `sort-by-date`, `switch-store`, `toggle-important`). An Action is *data*: a label plus a **Key Path**. Actions are registered once and surfaced by **two discovery paths over one substrate**: the **Command Palette** (type-to-discover) and **Key Progressions** (chord-to-discover). **Adding an Action never adds a Mode.** This is the lever that kills mode explosion.

**Key Path** — the sequence of key presses that invokes an Action from the keyboard. `[]` = unbound (palette-only). `[d]` = direct. `[s, d]` = a *progression*: `s` is a prefix, then `d`. A Key Path is data on the Action, not a Mode of the app.

**Key Progression / Prefix** — a *transient* state, active only in Normal, where the app waits for the next key(s) to complete a Key Path (`dd`, `gg`, `s d`, a space-leader menu). It returns to Normal the instant the path completes or mismatches. **This is what nvim's `dd`/`gg`/`gca` and yazi's `space`-menus are — and it is NOT a Mode in the smell sense.** It is the keyboard-fast discovery path; it coexists with the Palette. Wherever a progression is possible, the app shows a transient **WhichKey hint**.

**Command Palette** — one of the two discovery primitives: a fuzzy-filterable overlay listing every Action available in the current context, each with its Key Path shown. Triggered by `:` (vim idiom) and/or `Ctrl-P`. It is the *type-to-discover* path and replaces the static, unsearchable WhichKey **bar**. It is *not* a filter for list items — that is a **Filter**.

**WhichKey hint** — a *transient* overlay shown only during a Key Progression, revealing the key(s) that complete the in-progress path. It is **not** a permanent bottom bar. This is the bridge between chord muscle-memory (Key Progressions) and discoverability: the user never has to memorize the second key. The old static WhichKey bar was this idea done wrong (always-on, unsearchable); the hint is the modern, on-demand form.

**Filter** — narrows a list of *items* by query (`/` or inline input). Distinct from the Palette, which lists *actions*. A broken "command palette" usually conflates these two. A Filter is a sustained Mode (text-entry); the Palette is an Overlay.

**Mode** — a state in which the *whole keyboard means something different*. A Mode is justified **only** when the keyboard becomes a text-entry surface (Filter/Search input, inline rename, vim-like Insert) or a mutually-exclusive tool (vim-like Visual). Modes are rare and sustained — the user *dwells* in them. nvim's Normal/Insert/Visual are the canonical **legitimate** sustained Modes; this skill does not fight the modal nature of editors — it fights **action-modes**.

- **Sustained Mode** — legitimate, and the right pattern when the keyboard becomes a text-entry or tool surface. Named by the verb (Insert, Search, Visual). Keep them rare.
- **Action Mode** — **the smell.** `SortMode`, `StoreSelectMode`, `DeleteMode`, `ExportMode` exist only to gate *one* action. They inflate the mode enum, make Escape semantics ambiguous, hide Actions from the Palette, and duplicate what a Key Path expresses cleanly. Refactor: Action → transient Overlay or Key Path.

A Key Progression is sometimes mistaken for a Mode because it briefly reinterprets the next key. It is not: it is transient (no dwelling), scoped to completing one Action, and returns to Normal immediately. If you are about to add a Mode for an action, you want a Key Path or an Overlay, not a Mode.

**Overlay** — a transient UI layer (dialog, picker, menu, form, the Palette itself) drawn on top of the base view. Has its own key handling, returns to Normal on `Esc`/completion/failure. Overlays **stack**; they are not first-class persistent modes. Confirmation, selection, and one-shot input are Overlays.

**Normal** — the default, no-overlay, no-sustained-input state. The home state. `Esc` always converges toward Normal (peeling one Overlay/mode at a time).

## Layout units

**Region** — a rectangular area of the screen devoted to one role (list, detail, status, filters). A region is usually drawn inside a **Panel** (a titled, thin, rounded border) so the structure is visible. The modern byteowlz look uses thin styled borders + subtle background fills (header/status **bars**), not heavy double-boxes and not a borderless void.

**Panel** — a titled container for one region: a thin border (rounded), a title in the top edge, and padding inside. Exactly one panel is **active** at a time — its border is the accent color; the rest are muted. This is the yazi/Helix/lazygit panel, not the old mmry heavy box.

**Bar** — a full-width strip (header or status) with a subtle **background fill** (a dark surface token, distinct from the content background). Bars carry the app's chrome: name/context (header), counts + key hints (status). The fill is what makes them read as distinct regions.

**Pane** — a Region that can receive focus and input. A three-pane layout is *one* arrangement, not the arrangement.

**Focus** — the single Pane/Overlay currently receiving keyboard input. Exactly one at a time. The focused element is visually distinguished (accent edge, highlight, or cursor); everything else is muted.

**Status Line** — the single bottom line carrying: ephemeral feedback ("3 items deleted"), keybinding hints, and counts. One line. Never a busy toolbar.

## Visual language

**Theme** — the set of token → color/weight mappings, applied identically across every screen and every tool. The Theme is the primary consistency mechanism: one family of tools shares one Theme.

**Token** — a named semantic slot (`primary`, `muted`, `accent`, `bar`, `surface`, `success`, `danger`) that code references instead of raw colors. A token serves double duty: usable as a foreground (`.fg()`) or a background fill (`.bg()`). Tokens let 12 tools look like one family and let a redesign happen in one place.

**ANSI-default (the resolution rule)** — a Token resolves to a **named ANSI color** (the terminal's 16-color palette: `Red`, `Green`, `Blue`, `Cyan`, `Yellow`, `Magenta`, `Black`, `White`, `DarkGray`, `Gray`, + light variants) — **never to a hardcoded RGB/hex value by default**. The *terminal* (and its theme manager — tinty, etc.) owns the actual color rendering. Consequence: the TUI automatically matches the user's light/dark theme and palette with zero plugin or config in the tool. An opt-in **override layer** may pin a Token to an RGB for a deliberately-branded tool, but that is a stated exception, not the default. *Designing with raw hex is the smell.* This is the modern default — it is why yazi/helix/lazygit look right in any terminal.

**The two surface shades (load-bearing)** — content floats on `Surface` (`Reset` = the terminal's bg); chrome strips and panel structure use a distinct dark fill, `Bar` (`Black`, which the terminal maps to a dark surface). **`Reset` is reserved for the content background only.** Using it for bars/panels produces a flat, structureless void. The contrast between `Surface` and `Bar` *is* the visual structure — modern TUIs get their depth from this, not from raw RGB gradients.

**Weight** — bold vs dim/muted. The *primary* hierarchy mechanism. Use bold for what matters, dim for secondary. Weight and spacing carry hierarchy; color carries *state*.

**Accent** — the single saturated ANSI color (typically `Blue` or `Magenta`) reserved for focus and primary actions. There is one Accent. The rest of the palette is muted grays plus semantic state colors.

## Cross-surface contract

**Surface** — a way to operate the tool: CLI, TUI, (later) GUI/API. Every byteowlz tool has at least two surfaces (CLI + TUI).

**Core / Substrate** — the shared logic and data model beneath all surfaces. Every Action reachable in the TUI is *also* reachable as a CLI subcommand over the same Core. The TUI is a view over the Core, never the only path. (See: every surface over one substrate.)

---

## Derived rule (the payoff)

> **Sustained Modes are rare and named by a verb; they exist only for text-entry or mutually-exclusive tools. Actions are data, each with a Key Path. One-shot interactions are Overlays. The Command Palette and Key Progressions are the two discovery paths over one Action substrate; the WhichKey hint is shown on demand during a progression. If you are adding a Mode, you are almost certainly wrong — it should be an Action (with a Key Path), a Key Progression, or an Overlay.**
