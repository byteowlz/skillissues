---
name: sttmchn
description: Model interconnected state machines in TOML for system design and test case generation. Use when the user wants to define, validate, visualize, or test state machines — for example modeling component lifecycles, protocol states, connection flows, or any system with discrete states and event-driven transitions. Triggers on requests to create state machine definitions, generate state diagrams, produce test skeletons from state machines, or validate cross-component interactions.
---

# sttmchn — State Machine Modeling

Define state machines in TOML, validate them, generate Mermaid diagrams, and emit Rust test skeletons.

## Directory Structure

Place machine files in a `machines/` directory at the project root:

```
machines/
  session.toml      # One machine per file
  runner.toml
  websocket.toml
  wiring.toml       # Cross-machine links (optional)
```

The CLI auto-discovers `machines/` by walking up from cwd to the git root.

## CLI Commands

```bash
sttmchn list                    # List machines with state/transition counts
sttmchn check                   # Validate all machines + wiring
sttmchn show <machine>          # Pretty-print states and transitions
sttmchn diagram <machine>       # Mermaid diagram for one machine
sttmchn diagram                 # System-wide diagram with wiring
sttmchn tests <machine>         # Rust test skeleton for one machine
sttmchn tests                   # All skeletons + wiring tests
sttmchn diagram -o out.md       # Write to file
```

Override directory: `sttmchn -d path/to/machines list`

## Writing Machine Definitions

Each `.toml` file defines one state machine. For the full schema, see [references/toml-schema.md](references/toml-schema.md).

Minimal example:

```toml
machine = "connection"
initial = "disconnected"

[states.disconnected.on]
CONNECT = "connecting"

[states.connecting.on]
SUCCESS = "connected"
FAILURE = "disconnected"

[states.connected.on]
DISCONNECT = "disconnected"
ERROR = "disconnected"

[states.connected]
desc = "Active connection"

invariants = ["connected implies socket is open"]
```

### Rich Transitions

Use table syntax for transitions with guards, actions, or spawn:

```toml
[states.idle.on.FORK]
target = "pending"
spawn = true
action = "create_fork"
guard = "has_capacity"
```

### Terminal States

Mark states that accept no further events:

```toml
[states.closed]
terminal = true
desc = "Session terminated"
```

## Cross-Machine Wiring

Define how machines interact in `wiring.toml`:

```toml
[[links]]
from = "runner.spawning"
event = "PROCESS_READY"
to = "session.active"
note = "Agent ready activates session"

[[constraints]]
expr = "runner.stopped implies all session.closed"
severity = "error"
```

Wildcards (`machine.*`) and dynamic refs (`machine.{current}`) are supported in link targets.

## Workflow

1. **Define** machines as `.toml` files in `machines/`
2. **Validate** with `sttmchn check` — catches broken refs, unreachable states, dead ends
3. **Visualize** with `sttmchn diagram` — paste output into any Mermaid renderer
4. **Generate tests** with `sttmchn tests` — one `#[test]` per transition and invariant
5. **Iterate** — edit TOML, re-validate, regenerate

## Design Guidelines

- One machine per file, named after the component it models
- Use SCREAMING_CASE for events, lowercase for state names
- Mark all final states as `terminal = true`
- Add `desc` to states for self-documenting diagrams
- Use `invariants` to capture rules that span multiple states
- Use `edges_to_test` to highlight critical paths (happy path, error recovery, edge cases)
- Keep wiring links focused on observable cross-machine effects
