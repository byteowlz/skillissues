# tui-design reference

Full mechanism behind [SKILL.md](SKILL.md). Everything here targets the byteowlz stack:
**Rust (edition 2024) + ratatui 0.30 + crossterm 0.29 + tokio + clap**, under the maximum
`rust-magic-linter` preset (deny `unwrap_used`/`expect_used`/`panic`, `missing_docs`,
`missing_const_for_fn`, cognitive complexity ≤ 15). The kit and reference demo are written
to compile under that.

## Where things live

- `byteowlz-tui-kit` — `templates-repo/rust-workspace/crates/byteowlz-tui-kit`. The
  mechanism crate. Depend on it; do not fork it.
- `rust-tui` (reference demo) — `templates-repo/rust-workspace/crates/rust-tui`. A running
  modern TUI built on the kit; copy its shape.
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

`Theme::ansi_default()` maps every [`Token`](../CONTEXT.md) to a named ANSI color. The
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
- [ ] Captured a frame, **rendered and eyeballed it** (distinct shades, visible panels,
      one accent) before declaring done. Not just the bytes — the picture.
