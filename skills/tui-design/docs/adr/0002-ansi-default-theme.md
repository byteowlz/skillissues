# ADR-0002: ANSI-default theme (defer to the terminal palette)

**Status:** accepted (2026-06-26)
**Deciders:** Tommy (user), via grilling session

## Context

The naive way to theme a TUI is to pick hex/RGB colors ("accent = `#3b82f6`", "surface =
`#1e1e2e`") and bake them in. That fights the user: it ignores their terminal theme, breaks
light/dark switching, and produces a tool that looks "off" in any terminal whose palette
differs from the author's. It is also the *dated* look — modern TUIs (yazi, helix, lazygit,
bottom) instead defer to the terminal's palette.

Tommy runs a terminal theme manager (tinty). The requirement: the TUI should match the
terminal's theme **with zero per-tool plugin or config**.

## Decision

`byteowlz-tui-kit`'s **Theme maps each token to a named ANSI color** (the terminal's
16-color palette: `Red`, `Green`, `Yellow`, `Blue`, `Magenta`, `Cyan`, `Black`, `White`,
`DarkGray`, `Gray`, and light variants) and `Reset` for surfaces — **never to a hardcoded
RGB/hex value by default**.

The terminal (and its theme manager) owns the actual color rendering. Consequences the
design gets for free: automatic light/dark adherence, automatic palette matching, no
config surface in the tool, and a guaranteed-coherent look across the whole family because
they all draw from the same semantic slots.

Token → ANSI mapping (defaults, all overridable by a tool *stating* a reason):

| Token        | ANSI default | Role                                |
|--------------|--------------|-------------------------------------|
| `surface`    | `Reset`      | background; the terminal's bg       |
| `primary`    | `White`/fg   | main text                           |
| `muted`      | `DarkGray`   | metadata, hints, secondary          |
| `accent`     | `Blue`       | focus + primary action (the ONE)    |
| `success`    | `Green`      | state: ok                           |
| `danger`     | `Red`        | state: destructive/error            |
| `warning`    | `Yellow`     | state: caution                      |
| `info`       | `Cyan`       | state: neutral info                 |

An opt-in **override layer** may pin a token to an RGB — but only for a deliberately
branded tool, stated as an exception. Designing fresh UIs with raw hex is the smell.

## Consequences

- **Positive:** a byteowlz TUI matches the user's terminal instantly; light/dark "just
  works"; the family is coherent because the token contract is shared.
- **Positive:** it is the *modern* default — this is precisely why yazi/helix/lazygit look
  right in any terminal.
- **Negative:** no exact brand color by default. A byteowlz marketing screenshot won't
  show a fixed brand hue unless the tool opts into the RGB override. Accepted: respecting
  the user's environment beats brand consistency in a terminal.
- **Negative:** designers lose pixel-control. Mitigation: the override layer exists for the
  rare case it's warranted; the token contract stays stable either way.

## Alternatives considered

- **Hardcoded hex palette per tool.** Rejected: fights the terminal, the dated look, and
  guarantees inconsistency across the family.
- **A fixed RGB palette shared across tools (a "brand theme").** Rejected for the same
  reason; deferring to the terminal is the explicit goal.
