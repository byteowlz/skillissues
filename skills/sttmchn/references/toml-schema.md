# sttmchn TOML Schema Reference

## Machine File (`<name>.toml`)

```toml
# Required: machine identifier and initial state
machine = "session"
initial = "pending"

# States: each state has optional description, terminal flag, and event handlers
[states.<name>]
desc = "Human-readable description"    # optional
terminal = true                         # optional, marks final state (no outbound expected)

# Simple transitions: EVENT = "target_state"
[states.<name>.on]
EVENT_NAME = "target_state"

# Rich transitions: EVENT with metadata
[states.<name>.on.EVENT_NAME]
target = "target_state"    # required
guard = "condition"        # optional: when this transition is valid
action = "do_something"    # optional: side effect to execute
spawn = true               # optional: creates new machine instance

# Invariants: human-readable constraints that must hold
invariants = [
    "working implies agent process alive",
    "closed is terminal",
]

# Priority test edges: transitions to emphasize in test generation
[[edges_to_test]]
from = "source_state"
event = "EVENT_NAME"
to = "target_state"
desc = "Why this edge matters"    # optional
```

## Wiring File (`wiring.toml`)

Cross-machine event routing and global constraints:

```toml
# Links: how events flow between machines
[[links]]
from = "machine.state"     # source (or "machine.*" for wildcard)
event = "EVENT_NAME"       # triggering event
to = "machine.state"       # target (or "machine.{current}" for dynamic)
note = "Description"       # optional

# Constraints: global invariants across machines
[[constraints]]
expr = "human-readable constraint expression"
severity = "error"         # "error" (default) or "warning"
```

## Validation Rules

sttmchn validates:
- Initial state exists in states map
- All transition targets reference existing states
- Terminal states have no outbound transitions (warning)
- No unreachable states (warning)
- No dead-end non-terminal states (warning)
- edges_to_test reference valid states, events, and targets
- Wiring links reference valid machine.state pairs
- No unknown machines in wiring references
