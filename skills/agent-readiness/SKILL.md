---
name: agent-readiness
description: Audit or design a tool's agent-facing contract with reproducible evidence. Use for new apps/templates, before declaring a feature agent-ready, or when state/actions are trapped behind a GUI. Checks semantic access, shared state, safety, schemas, reproducibility, and human UI accessibility; readiness never grants authority.
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
| `structured_contract` | Documented state and operation schemas; machine-readable failures with stable codes and nonzero exits; valid stdout in machine mode, including invalid input. Files/stdin/stdout compose where meaningful. |
| `shared_substrate` | Agent edits become visible in an open human UI and UI edits are inspectable through the agent surface. One service/state model; documented reload/conflict behavior. No authoritative content trapped only in browser storage. |
| `authority_and_safety` | Read-only inspection is genuinely read-only. Mutation requires applicable authority and explicit intent, validates target/baseline, previews effects, and has a backup/recovery path. Readiness, discovery, network reachability, `--yes`, or a schema is never a grant. |
| `concurrency_and_recovery` | Stale revisions, concurrent edits, disconnects, timeout/cancellation and partial failure have bounded, truthful outcomes. Idempotent operations/retries are identified; uncertain writes are not blindly retried. |
| `portable_state` | Durable inputs/outputs are documented, inspectable and portable. Export/import roundtrip is tested; artifacts do not depend on the developer's checkout, absolute paths or services. Sensitive runtime data stays out of published proof. |
| `reproducibility` | Deterministic safe fixtures exercise the actual substrate and a project `just agent-check` (or existing equivalent) proves success and denied/error paths. Hardware/platform/live-system claims are separately tested or marked unverified. |
| `human_accessibility` | Human UI has semantic controls, keyboard access, visible focus, accessible names/status and noncolor feedback. Custom canvases/3D have an equivalent operable 2D/table surface. CLI-only tools may justify not_applicable for GUI checks. |

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

## Boundaries

- File presence, help screenshots, generated IPC types and successful compilation
  alone do not prove semantic parity, safety, accessibility or hardware behavior.
- A mock is not a live adapter. A browser screenshot is not native runtime proof.
- Keep reports proportionate; no universal agent score, auto-approval system,
  inference wrapper, or new transport platform.
- In templates, include one genuine shared-service fixture and negative-path test.
  Consumers replace the example with their own domain proof; they do not inherit
  an 'agent-ready' label from the scaffold.
