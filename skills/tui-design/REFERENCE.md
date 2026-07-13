# tui-design reference

Full mechanism behind [SKILL.md](SKILL.md). Everything here targets the byteowlz stack:
**Rust (edition 2024) + ratatui 0.30 + crossterm 0.29 + tokio + clap**, under the maximum
`rust-magic-linter` preset (deny `unwrap_used`/`expect_used`/`panic`, `missing_docs`,
`missing_const_for_fn`, cognitive complexity ≤ 15). The kit and reference demo are written
to compile under that.

## Where things live

The templates repo: <https://github.com/byteowlz/templates> — local clone at
`~/byteowlz/templates`.

- `byteowlz-tui-kit` — `~/byteowlz/templates/rust-workspace/crates/byteowlz-tui-kit`. The
  mechanism crate. Depend on it; do not fork it.
- `rust-tui` (reference demo) — `~/byteowlz/templates/rust-workspace/crates/rust-tui`. A
  running modern TUI built on the kit; copy its shape.
- Workspace pins: `ratatui = "0.30"`, `crossterm = "0.29"` in the workspace
  `[workspace.dependencies]`. **Use the workspace pins** — this is what stops the version
  drift (trx was on 0.29, tmz on 0.30).

## Workspace wiring

In the workspace `Cargo.toml`, the kit is already a member and a dependency:

```toml
[workspace.dependencies]
ratatui = "0.30"
crossterm = "0.29"
byteowlz-tui-kit = { path = "crates/byteowlz-tui-kit" }
```

In a `<tool>-tui/Cargo.toml`:

```toml
[dependencies]
<tool>-core.workspace = true
byteowlz-tui-kit.workspace = true
ratatui.workspace = true
crossterm.workspace = true
anyhow.workspace = true
clap.workspace = true
```

## The kit, by module

All examples assume `use byteowlz_tui_kit::prelude::*;`.

### theme — tokens to ANSI colors (two surface shades)

`Theme::ansi_default()` maps every [`Token`](CONTEXT.md) to a named ANSI color. The
load-bearing detail: **there are two surface shades**, and using them correctly is what
creates visual structure:

- `Surface` → `Color::Reset` (the terminal's content bg). **Content floats on this.
  Never use it for bars/panels** or you get the flat void.
- `Bar` → `Color::Black` (a real dark fill the terminal maps to a surface). Used for
  header/status **bars** and panel structure.
- `Muted` → `DarkGray` (text + thin borders); `Accent` → Blue (one accent, focus +
  primary).

Each token works as a foreground (`.fg()`) **or** a background fill (`.bg()` / `.on_bar()`):

```rust
let theme = Theme::ansi_default();
let title    = theme.fg_bold(Token::Primary);   // main text, bold
let meta     = theme.fg(Token::Muted);          // secondary + borders
let cursor   = theme.focus();                    // accent + bold, for the active row
let danger   = theme.fg(Token::Danger);          // state: destructive
let header   = theme.on_bar_bold(Token::Accent); // bold accent text on a filled bar
let bar_fill = theme.bg(Token::Bar);             // the dark surface fill for strips
```

Never pass a raw `Color::Rgb`/hex unless you have a stated reason; use
`.with_token(token, color)` for the rare override.

### action — Actions are data; the prefix router kills modes

Define actions as data. Direct keys, **key progressions** (`s d`), and palette-only actions
are all just different Key Paths:

```rust
use byteowlz_tui_kit::action::{Action, ActionId, Key};

fn actions() -> Vec<Action> {
    vec![
        Action::new(ActionId::new("item.delete"), "Delete").key(Key::char('d')),
        Action::new(ActionId::new("sort.date"), "Sort by date")
            .keys(&[Key::char('s'), Key::char('d')]),
        Action::new(ActionId::new("sort.importance"), "Sort by importance")
            .keys(&[Key::char('s'), Key::char('i')]),
        Action::new(ActionId::new("export.json"), "Export as JSON"), // palette-only: no key
    ]
}
```

The router is a prefix-state machine. Feed it keys in Normal mode:

```rust
use byteowlz_tui_kit::action::{KeyRouter, Route};
let mut router = KeyRouter::new(&actions);
match router.feed(Key::char('s')) {
    Route::Action(id) => { /* run it */ router.reset(); }
    Route::Prefix(options) => {
        // options: [(next key, label), ...]  -> show as a transient WhichKey hint
    }
    Route::Miss => { /* prefix cleared; ignore */ }
}
```

> **This is how `dd`/`gg`/`s d` work without a mode.** The transient prefix shows a
> WhichKey hint (next module) — the user never memorizes the second key. Adding an action
> never touches a mode enum.

### whichkey — the on-demand hint (not a permanent bar)

```rust
use byteowlz_tui_kit::whichkey;
if let Some((prefix, options)) = &app.pending_hint {
    whichkey::draw_hint(frame, hint_area, theme, prefix, options);
}
```

Drawn only while a prefix is in progress. There is no always-on hint bar — that was the old
smell.

### palette — the type-to-discover path

```rust
use byteowlz_tui_kit::palette::{CommandPalette, PaletteOutcome};
// open on `:` or Ctrl-P:
app.palette = Some(CommandPalette::new(actions.clone()));
// per key while open:
match app.palette.as_mut().unwrap().handle(key) {  // (demo only; real code avoids unwrap)
    PaletteOutcome::Open    => {}
    PaletteOutcome::Closed  => app.palette = None,
    PaletteOutcome::Run(id) => { app.palette = None; run(id); }
}
// render:
if let Some(p) = app.palette.as_mut() { p.draw(frame, theme); }
```

Filter is fuzzy, matches are highlighted in the accent, the Key Path is shown beside each
label. The palette and the key router share **one** action substrate — two discovery paths.

### widgets — panels, bars, and the rest

The structure primitives (`panel`, `bar`, `draw_status_bar`) are where the visual
structure comes from. Use them:

```rust
use byteowlz_tui_kit::widgets::{panel, bar};
// a titled rounded panel; active = accent border, inactive = muted
let block = panel("items", theme, /* active */ true);
frame.render_stateful_widget(list.block(block), area, &mut state);

// a filled header/status strip
let line = Line::from(vec![Span::styled(" memory ", theme.on_bar_bold(Token::Accent))]);
frame.render_widget(bar(line, theme), header_area);
```

- `Selection` — first-class, cursor-orthogonal multi-select. `.next/.previous/.top/.bottom`,
  `.toggle/.select_all/.deselect_all`, `.is_selected`, `.state()` for ratatui's `List`.
- `draw_status_bar(frame, area, theme, left, &[(key, label)])` — the single status line,
  filled with `Bar`, hints right-aligned.
- `draw_empty_state(frame, area, theme, prompt)` — never show a blank pane (IA4).
- `centered_rect(px, py, area)` — the popup primitive for every overlay.
- `poll_event(tick) -> io::Result<Option<AppEvent>>` — synchronous loop; `AppEvent::Key` is
  already normalized to a `Key` (press only). Wrap in `spawn_blocking` for async apps.
- `TerminalGuard::enter()` — RAII; enter raw mode + alt screen, **restore on drop even on
  panic**. This is the single cleanup path: there is no way to leave the terminal broken.

```rust
use byteowlz_tui_kit::terminal::TerminalGuard;
let mut guard = TerminalGuard::enter()?;
loop {
    guard.draw(|f| draw(f, &mut app))?;
    match poll_event(Duration::from_millis(120))? {
        Some(AppEvent::Key(k)) => { if handle(k, &mut app) == Flow::Quit { break; } }
        Some(AppEvent::Resize(_, _)) | Some(AppEvent::Tick) | None => {}
    }
}
```

## Mouse (rule I10)

Policy: **supported, never required.** Scroll-wheel scrolls the hovered list; click
focuses a pane; click selects a row; double-click acts like `Enter`. Every mouse action
must have a keyboard path.

Kit state: `TerminalGuard::enter()` already enables `EnableMouseCapture`, but
`poll_event` currently *drops* mouse events (normalizes them to `Tick`). Until the kit
grows `AppEvent::Mouse(MouseEvent)`, handle crossterm's `Event::Mouse` yourself if the
tool needs it — hit-test against the pane `Rect`s you computed in `layout()` (keep them
on the app state). Match on `MouseEventKind::ScrollUp/ScrollDown` and
`MouseEventKind::Down(MouseButton::Left)`; ignore drag/move noise.

## Runtime & async

The kit loop is synchronous on purpose — most tools need nothing more. When a tool does
background work (network, indexing, long ops):

- **One event channel.** `tokio::sync::mpsc::Sender<Msg>` cloned into tasks; the main
  loop `select!`s (or drains after `spawn_blocking(poll_event)`) and treats a `Msg` like
  any other event: mutate state, redraw. UI state is mutated **only** on the main loop —
  tasks send messages, they never touch the app struct.
- **Never block the loop.** Anything > ~50ms goes to a task; show progress via I7 (status
  line spinner/percent updated on `Tick`), a blocking overlay only if the user truly
  cannot proceed.
- **Redraw on change, not every tick.** Set a `dirty` flag on state mutation; skip
  `draw()` when clean. Spinners are the exception (they dirty on tick while active).
- **Shelling out to `$EDITOR`:** leave the alt screen + raw mode, run the editor
  inherited-stdio, re-enter, force a full redraw (`guard.clear()`). Do this through the
  guard so the panic path stays intact — never raw `disable_raw_mode` calls scattered in
  handlers.

## Text input

Text entry is where TUIs quietly break. Rules:

- **Reuse, don't hand-roll.** Single-line → `tui-input`; multi-line → `tui-textarea`.
  Hand-rolled cursor math gets unicode width wrong (CJK, emoji, combining marks).
- **Bracketed paste.** Enable it and handle `Event::Paste` as one string insert —
  otherwise a paste replays as individual keys and can trigger keybindings mid-paste.
- **Cursor:** show the real terminal cursor in text-entry (set `frame.set_cursor_position`),
  don't fake one with a styled cell.
- Single-line one-shot input = an Overlay; a persistent filter/search input = the one
  legitimate Sustained Mode (see CONTEXT.md).

## Responsive layout

Design for 80×24 as the floor; verify there.

- **Min widths per pane.** Below a pane's minimum, collapse it — a detail pane becomes an
  on-`Enter` Overlay, a sidebar becomes a picker. Collapsing beats squeezing.
- **Truncation order is a decision** (V6): drop decorations first, then meta, then
  ellipsize the title. Status-bar hints drop from the left; counts survive longest.
- Recompute layout on `AppEvent::Resize` only; keep the computed `Rect`s on state (they
  double as mouse hit-boxes).
- Height matters too: at < ~15 rows, merge header into the status line.

## Testing (snapshot the screens)

Eyeballing (workflow step 7) is the acceptance test; snapshots make it a regression test.

```rust
use ratatui::{backend::TestBackend, Terminal};

#[test]
fn list_screen_normal() -> std::io::Result<()> {
    let mut term = Terminal::new(TestBackend::new(100, 30))?;
    let mut app = App::fixture();
    term.draw(|f| draw(f, &mut app))?;
    insta::assert_snapshot!(term.backend());
    Ok(())
}
```

`TestBackend` renders text + styles; `insta` snapshots diff readably in review. Required
matrix per screen: **normal · focused/active-pane · overlay open · empty state (IA4) ·
narrow (80×24)**. Add one per bug thereafter. Run under `cargo test` in CI; review
snapshot diffs like code — a changed frame is a changed UI.

What snapshots do **not** catch: color rendering on a real terminal (light themes,
`NO_COLOR`) — that stays a manual check (V8).

## Module layout (copy from `rust-tui`)

A modern `<tool>-tui` stays small by delegating to the kit:

```
src/
  main.rs      # clap, TerminalGuard::enter, the loop, handle() dispatch
```

Grow it only when a screen earns its own file:

```
src/
  main.rs      # loop + top-level draw/handle
  actions.rs   # the action table (data)
  state.rs     # domain state + Selection
  ui/
    list.rs    # one render fn, references tokens
    detail.rs
```

Keep each `draw_*` and `handle_*` under 100 lines / cognitive complexity 15 (the workspace
clippy threshold). The reference demo already splits `layout`/`body`/`draw_list`/
`draw_detail`/`draw_status_row` precisely for this.

## Gotchas (real, from building the kit + demo)

- **`Color::Reset`, not `Color::Black`, for the *content* `Surface`.** `Reset` = terminal
  default bg, so content floats on the operator's theme. But **`Bar` must be `Black`
 (a real fill)**, not `Reset` — that's the whole point of having two surface shades.
  Using `Reset` for bars produces the flat void. (The kit's `Bar` token is `Black`.)
- **You cannot `render_widget` a bare `Style`.** To fill a region's background, render a
  `Paragraph::new("").style(theme.bg(Token::Bar))` or a `Block` with `.style(...)`. The
  kit's `draw_status_bar`/`bar` do this for you.
- **No `KeyCode::Space`.** Use `KeyCode::Char(' ')`. (The kit's `Key::space()` does this.)
- **`key.kind == KeyEventKind::Press`.** Filter to press only; crossterm also reports
  Release/Repeat on some terminals and you'll double-fire otherwise. `poll_event` does this.
- **`Terminal::draw` returns `io::Result<CompletedFrame>`, not `io::Result<()>`.** The
  guard's `draw` matches.
- **Max-lint clippy wants `const fn` everywhere it can.** The kit's simple
  `next/previous/top/bottom/has_prefix` are `const fn`; match that in your widgets.
- **`needless_pass_by_ref_mut`.** A `draw_*(frame: &mut Frame, app: &App, area)` that
  doesn't mutate `app` must take `&App`. The demo hit this — render fns take `&App`.
- **Leak the action table for a `'static` router** (demo does this) *only* because the app
  is one short-lived process. In a library, give the router a non-`'static` lifetime tied to
  a borrowed table.
- **Restore the terminal on panic.** `TerminalGuard`'s `Drop` does this; never bypass it
  with raw `enable_raw_mode` without a matching disable.

## Per-tool build checklist

- [ ] Actions modeled as data; the mode enum has ≤ 2 sustained modes (Normal + maybe
      Search/Insert). No action-modes.
- [ ] Every action reachable by palette **and** (where bound) by key; key progressions show
      a WhichKey hint.
- [ ] Layout derived from the task (IA1); primary content gets the most space (IA2).
- [ ] Theme is `Theme::ansi_default()`; no raw RGB; **two surface shades used correctly**
      (content on `Reset`, bars/panels filled with `Bar`); weight carries hierarchy.
- [ ] Regions are titled **panels** (thin rounded borders, active = accent); header/status
      are filled **bars**. No heavy double-boxes, no borderless void (V1).
- [ ] Empty states wired (IA4); `Esc` converges to Normal (I8).
- [ ] Every TUI action is also a CLI subcommand over the Core (IA5).
- [ ] `cargo clippy --workspace` clean under the max preset; `cargo test` green.
- [ ] Snapshot tests exist (TestBackend + insta) for normal · focus · overlay · empty ·
      80×24 states of each screen.
- [ ] Usable at 80×24; panes collapse instead of squeezing; checked on a light terminal
      theme and with `NO_COLOR` (V8).
- [ ] Mouse: scroll + click-focus + click-select work; nothing is mouse-only (I10).
- [ ] Errors surfaced per I11 (status line `Danger` / blocking overlay); no panics.
- [ ] Captured a frame, **rendered and eyeballed it** (distinct shades, visible panels,
      one accent) before declaring done. Not just the bytes — the picture.
