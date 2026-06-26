# tui-design examples

Worked designs that exercise the rules. Each one names the smell, the rules that fix it,
and the concrete shape — so you can pattern-match a new tool to the closest case.

## Example 1 — A list + detail tool (the canonical shape)

**Task:** a memory/task store with a list of items and a detail pane.

**Smell avoided:** cargo-culting a 3-pane layout when there's no third role (rules IA1, IA2).

**Decisions:**
- **2 panes**, not 3. Primary object = the list; what you scan = the list; what you act on
  = a selected item's detail. There is no third role, so no third pane.
- Layout: list (45%) `|` detail (55%). The detail is what you read, so it gets more space.
- Air over borders (V1): `Block::default().padding(Padding::new(1,1,1,0))`, no `Borders`.
- Hierarchy (V3): item title bold-`Primary`, meta `Muted`; active row `theme.focus()`.

**Actions** (data — note the key progressions, no modes):

```text
item.open       Enter     (direct)
item.delete     d         (direct → Confirm overlay)
item.add        a         (direct → Input overlay)
sort.date       s d       (progression)
sort.imp        s i       (progression)
sort.category   s c       (progression)
palette.open    :         (direct → CommandPalette overlay)
help            ?         (direct → Help overlay)
quit            C-c       (direct)
nav.down        j         (direct)
nav.up          k         (direct)
```

**Mode enum:** `Normal` only. Sort/delete/add/help/palette are **Overlays**; `s` is a
**Key Progression** with a WhichKey hint. One mode, eleven actions. (Contrast: the old
mmry shape used ~6 modes for fewer actions.)

**Result:** this is exactly the reference `rust-tui` in `templates-repo/rust-workspace`.
Copy it.

## Example 2 — Migrating mmry's 13 modes down to ~2

**Smell:** mmry-tui today has 13 modes — `Sort`, `WhichKey`, `StoreSelect`, `StoreCreate`,
`MoveToStore`, `Export`, `CategoryInput`, `CategorySelect`, `Delete`, `DeleteMultiple`,
`Help`, `Search`, `Normal`. Most are **action-modes** (rule I2 smell).

**The refactor — map each mode to its correct unit:**

| Old mode (action-mode) | Becomes | Why |
|---|---|---|
| `Sort` | Key Path `s d`/`s i`/`s c` + WhichKey hint | one action, not a dwelling state |
| `WhichKey` | the on-demand hint, not a mode | it was always transient |
| `StoreSelect` | Overlay picker | one-shot selection |
| `StoreCreate` | Overlay input | one-shot text entry |
| `MoveToStore` | Overlay picker | one-shot selection |
| `Export` | Overlay menu | one-shot selection |
| `CategoryInput` | Overlay input | one-shot text entry |
| `CategorySelect` | Overlay picker | one-shot selection |
| `Delete` / `DeleteMultiple` | Confirm Overlay | one-shot yes/no |
| `Help` | Help Overlay | transient |
| `Search` | **kept** as sustained Sustained Mode | text-entry surface (legitimate) |
| `Normal` | **kept** | the home state |

**After:** `Normal` + `Search` (2 sustained modes) + a stack of transient Overlays + Key
Progressions. Escape semantics become unambiguous (I8): Esc peels one overlay. Every action
is palette-reachable (I1). The 13-way `match self.mode` collapses to a router + an overlay
stack.

**Migration rule (do not rewrite for purity):** migrate *when the tool is next
substantially edited* (ADR-0001). Port one action-mode at a time to an Overlay/Key Path;
keep the old path working until each lands.

## Example 3 — Authoring a key-progression set

**Goal:** fast keyboard chords (`s d`, `g a`, …) without memorizing the second key.

**Rule I9 in action.** Progressions are transient prefix states; the WhichKey hint reveals
the next key. Design them as a small, consistent namespace:

```text
s   sort…       →  d date · i importance · c category
g   go…         →  g top · G bottom · t tab · e editor
m   mark…       →  i important · c category · t tag
S   store…      →  s switch · n new · m move-to
```

**Authoring checklist:**
1. Every progression shares a one-key namespace (`s`, `g`, `m`, `S`).
2. The second key is a mnemonic for the sub-action (`d` = date).
3. The WhichKey hint lists them the instant the prefix is hit — discoverability for free.
4. Direct single-keys (`d` delete, `e` edit) stay available; only reserve namespace prefixes
   that don't collide (`s`/`g`/`m`/`S` don't collide with `d`/`e`/`a`/`q`).
5. The **same** actions appear in the palette (`:`) with their Key Path shown — the two
   discovery paths never diverge.

**This is the nvim muscle-memory you wanted, and it costs zero modes.**

## Example 4 — An empty state (IA4)

Never show a blank pane. A filter/result list with zero matches:

```text
                      No memories match "ports"

                  Press Esc to clear the filter, or
                  press a to add a new memory.
```

Rendered with `draw_empty_state(frame, area, theme, prompt)`, centered, `Muted`/dim.
The prompt is a concrete call to action naming the keys — never just "no results."

## Example 5 — Progressive disclosure (IA3)

A detail pane that does not dump 7 fields:

- **At rest:** caption (`MEMORY · 3d · debugging`), title (bold), one-line meta, a 2-line
  body excerpt, and a single `⏎ open full editor` action.
- **On `Enter`:** the full editor (or an expanded Overlay) reveals the rest — key, tags,
  created date, raw.

The rule: show the summary by default; reveal the rest on an explicit action. The detail
pane in the reference `rust-tui` is this shape.

## Anti-example — what not to ship

A pane rendered as `Block::default().borders(Borders::ALL)` around every region, a title
bar + a permanent WhichKey bar + a status bar (three rows of chrome), every label at equal
weight, color (red/yellow/cyan/magenta) used as decoration, a `SORTMODE` enum variant to
gate one action, and a search box that overflowed its bounds. **Every one of these is a
named rule above.** If the captured frame looks like this, you skipped step 3
(visualize before you build).
