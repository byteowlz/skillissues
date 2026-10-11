---
name: agent-readiness
description: Audit or design a tool's agent-facing contract with reproducible evidence. Use for new apps/templates, before declaring a feature agent-ready, or when state/actions are trapped behind a GUI. Checks semantic access, shared state, safety, schemas, token economy, reproducibility, and human UI accessibility; readiness never grants authority.
---

# Agent readiness

An agent should inspect and operate the tool's real domain without scraping pixels,
and without bypassing the human's authorization. Human UX remains first-class.

## Start with the existing surface

Read repo guidance, domain/contracts, help and tests. Identify authoritative state,
all user-visible operations, existing file formats/CLI/API, and the trust boundary.
Reuse them. Prefer documented files for simple state; semantic operations when
validation, transactions or hardware justify them. Do not require MCP, HTTP, a
second CLI, or embedded model calls just to tick a box.

Separate deterministic mechanism from model/human judgment. Human UI and agent
operations share one substrate. Presentation-only controls (camera orbit, pane
layout) need not become domain operations. Capability differences are acceptable
only as explicit policy or platform limits, not forgotten functionality.

## Evidence gates

For **each gate**, record `pass`, `fail`, `unverified`, or `not_applicable`.
`pass` needs a reproducible command/manual procedure and an observed artifact.
Unknown is not pass; `not_applicable` needs a concrete reason. Do not average away
a missing safety gate with a readiness score.

| Gate | Required evidence |
|---|---|
| `discoverability` | Fast help/docs name state, operations, inputs, side effects, schemas/version and recovery; a fresh agent can complete a fixture task from these alone. |
| `structured_contract` | Documented state and operation schemas; machine-readable failures with stable codes and nonzero exits; valid stdout in machine mode, including invalid input. Files/stdin/stdout compose where meaningful. Exit codes are truthful: health checks fail when unhealthy, and a reader closing stdout early (`\| head`, `\| grep -q`) is a clean exit, not a crash that breaks `pipefail`. |
| `shared_substrate` | Agent edits become visible in an open human UI and UI edits are inspectable through the agent surface. One service/state model; documented reload/conflict behavior. No authoritative content trapped only in browser storage. |
| `authority_and_safety` | Read-only inspection is genuinely read-only. Mutation requires applicable authority and explicit intent, validates target/baseline, previews effects, and has a backup/recovery path. Readiness, discovery, network reachability, `--yes`, or a schema is never a grant. |
| `concurrency_and_recovery` | Stale revisions, concurrent edits, disconnects, timeout/cancellation and partial failure have bounded, truthful outcomes. Idempotent operations/retries are identified; uncertain writes are not blindly retried. |
| `portable_state` | Durable inputs/outputs are documented, inspectable and portable. Export/import roundtrip is tested; artifacts do not depend on the developer's checkout, absolute paths or services. Sensitive runtime data stays out of published proof. |
| `reproducibility` | Deterministic safe fixtures exercise the actual substrate and a project `just agent-check` (or existing equivalent) proves success and denied/error paths. Hardware/platform/live-system claims are separately tested or marked unverified. Wrappers over other tools probe the backend's current contract with a real machine-mode call, not binary presence, and degradation messages name the real cause. |
| `output_economy` | Token cost of representative tasks measured on realistic data with a real tokenizer, before and after. Listings don't repeat derivable data per row (paths, full ids, a subject shown twice); long ids get unique short prefixes the tool resolves, and ambiguity is an error. Filters exist so finding one item doesn't require listing everything. Machine output has no duplicated fields, omits nulls and is compact when piped. Filtered or bounded views never mutate state (e.g. read cursors). |
| `human_accessibility` | Human UI has semantic controls, keyboard access, visible focus, accessible names/status and noncolor feedback. Custom canvases/3D have an equivalent operable 2D/table surface. CLI-only tools may justify not_applicable for GUI checks. |

### Output economy without losing fidelity

Every trim must be lossless, or the full value must stay one command away
(a `read`/detail verb, a `--raw` byte-exact mode). Record in the evidence what a
listing drops (e.g. seconds in timestamps, clipped subjects). Measure, don't
estimate: chars/4 badly underestimates ids and paths (a UUID is ~22 tokens, an
8-character prefix ~3).

```bash
# Token cost of each command's stdout (piped, as an agent receives it):
uv run --script <skill-directory>/scripts/token_cost.py -- "tool list" "tool read ID"
```

Scripted access (pi codemode, any agent that writes code against tools) changes
what matters: the script reads the output and only its return value reaches the
model, so the stable, complete machine contract matters more than text size.
It pays off for multi-step filtering; for a single small read, writing the
script costs more than it saves. Provide both a lean text surface and a full
machine one.

## Workflow

1. Inventory one representative read → plan/edit → validate → apply/export task.
2. State expected outcomes and authority boundary **before** running commands.
3. Run safe fixture/read-only checks first. Never touch a real keyboard, account,
   remote resource or shared state merely to prove readiness. Even reads can have
   effects (mark-as-read, connection side effects): inspect the contract first.
4. Add the smallest missing test/interface seam in the owning repo, not a parallel
   agent-only implementation. For an audit request, report gaps instead of editing.
5. Exercise both human and agent paths, including invalid/stale/denied operations.
6. Record exact source revision, fixture, platform, scope and evidence per gate.
   Keep private transcripts, device IDs, credentials and user data out of reports.
7. Summarize blockers and deliberate exceptions, distinguishing fixture, browser,
   actual native render and live/hardware evidence. Link owning issues for gaps.

Use [report.schema.json](report.schema.json) for an optional portable report.
Each gate is a conservative aggregate: if a required part lacks proof, mark it
`unverified` even when other parts passed. Narrow scope explicitly rather than
quietly claiming all platforms or capabilities. Suggested home:
`docs/agent-readiness.json` (synthetic/public-safe evidence only).

```bash
# Validate a report's structure and declared completeness, not its truth:
uv run --script <skill-directory>/scripts/validate_report.py docs/agent-readiness.json
# '-' reads JSON from stdin. The validator never executes reported commands.
```

The validator returns JSON. Exit `0`: structurally valid, all applicable gates
**claim** pass; `3`: valid report with fail/unverified gates; `2`: invalid report
or usage. Its output always says `evidence_verified: false`: an agent must inspect
and reproduce the cited evidence. Structural validation is not certification.

## Fresh-agent review

The strongest evidence for `discoverability` is a fresh agent actually using
the tool. Give independent reviewers (ideally different models) a read-only
brief: build, drive the WHOLE surface in a throwaway environment (isolated
`XDG_*`/`HOME`, git identity via env, local bare remotes), and return
P0/P1/P2 findings with exact commands and output. Scope matters: reviews
limited to new code miss breakage in older wrappers. Then:

- Reproduce each finding yourself before fixing; reviewers misread things too.
- Re-run against real data, not only fixtures (malformed historical records,
  large stores, other layouts).
- Mutation-check new tests: a test that still passes with the fix removed
  proves nothing, and negative checks (`! ... | grep -q X`) must not pass
  vacuously after an output format change.
- File gaps that belong to another tool in that tool's tracker.

## Boundaries

- File presence, help screenshots, generated IPC types and successful compilation
  alone do not prove semantic parity, safety, accessibility or hardware behavior.
- A mock is not a live adapter. A browser screenshot is not native runtime proof.
- Keep reports proportionate; no universal agent score, auto-approval system,
  inference wrapper, or new transport platform.
- In templates, include one genuine shared-service fixture and negative-path test.
  Consumers replace the example with their own domain proof; they do not inherit
  an 'agent-ready' label from the scaffold.
