# ADR-0001: Scaffold a shared `byteowlz-tui-kit` crate

**Status:** accepted (2026-06-26)
**Deciders:** Tommy (user), via grilling session

## Context

byteowlz ships ~12 `<tool>-tui` crates. Four have grown large (mmry 4.6k, trx 3.6k,
based 3.2k, hstry 2.5k LOC); the rest are ~290-LOC template stubs awaiting build-out.
Survey shows:

- **No shared helper crate exists.** Every TUI independently re-implements modes,
  the WhichKey bar, a command palette, a status bar, popups, selection state, and the
  crossterm enter/leave dance.
- **`ratatui` versions are drifting** across repos (trx pins 0.29, tmz pins 0.30) with
  no shared baseline.
- The stated pain is cross-tool **inconsistency** (visual + interaction) plus
  **ugly/dated** output from freshly-built TUIs.

The old `templates-repo/rust-workspace/TUI.md` is descriptive mechanics — it documents
*what mmry does*, not a contract. Consistency cannot be achieved by prose an agent must
re-read and re-interpret on each build.

## Decision

Scaffold **`byteowlz-tui-kit`** in `templates-repo/rust-workspace` (replacing the stale
`TUI.md` as the source of truth). The kit is the **mechanism** layer; the `tui-design`
skill is the **judgment** layer that says when to reach for each piece.

The kit provides, as data-on-disk:

1. A workspace-pinned `ratatui` + `crossterm` baseline (kills version drift).
2. The **Theme** (token → ANSI color; see ADR-0002) applied via a `Theme` type and a
   `Style` helper so widgets never take a raw color.
3. **Reusable widgets** that embody the patterns: `StatusBar`, `CommandPalette`,
   `SelectionList`, `HelpOverlay`, `ConfirmOverlay`, centered-popup layout helper.
4. **Action dispatch**: an `Action` registry + a tiny reducer so adding a command never
   adds a Mode (the core lever against mode explosion).
5. An **event loop + terminal lifecycle** helper (enter/leave raw mode, restore on panic).

## Consequences

- **Positive:** consistency becomes "depend on the kit," not "read and emulate."
  New TUIs start modern on day one. A redesign happens in one place. Stops version drift.
- **Positive:** keeps judgment out of the kit (the kit renders; the skill decides),
  consistent with `bitter-lesson-proof-project` rules 4 (every surface over one substrate)
  and 8 (disposable satellites, never colonization — the kit never extends a tool's core).
- **Negative:** introduces a cross-repo dependency. A breaking change in the kit ripples.
  Mitigation: treat the kit's public API as versioned; semver from day one; the Theme and
  `Action` trait are the stable contracts.
- **Negative:** the 4 large existing TUIs do not migrate automatically. Migration is
  opt-in, per tool, when it is next substantially edited. We do not rewrite working apps
  for purity.

## Alternatives considered

- **(i) Prescribe-only** — skill documents the contract, each tool re-implements.
  Rejected: does not solve consistency; prose is the thing that already failed (the old
  `TUI.md`).
- **A shared "TUI framework" that also owns app logic.** Rejected: that would colonize
  each tool's core (rule 8). The kit is widgets + theme + dispatch primitives, not a
  framework that owns state or domain logic.
