---
name: dpty-operate
description: Operate a dpty machine unit — introspect capability, match recipes to observed capacity, place and supervise Work Requests, read the ledger, and report to gvnr. Use when running dpty on a machine, placing fleet work, or debugging recipe/capability matching.
---

# dpty operate

`dpty` (deputy) is the byteowlz per-machine compute unit. It reads **recipes** from
`wismut/dpty-recipes`, runs + supervises **Instances**, keeps the
Work-Request/Instance **ledger**, and reports facts/events to **gvnr** over
HTTPS + token on the overlay mesh.

The non-negotiable boundaries — **LEDGER not scheduler**, gvnr never dispatches,
HTTPS+token not SSH on the registry bus, explicit-and-logged unload,
Ansible=provisioning / dpty=supervision — are defined in this repo's
`AGENTS.md` and `DESIGN.md`. Read them; **this skill never relaxes them.** When a
line here seems to conflict, the repo docs win. The symbol-level API reference
is disclosed to [`details.md`](details.md); reach it when you need exact
type/method/endpoint names.

## The three-layer model

1. **Recipe** — how-to-run TOML manifest. Grammar owned by dpty
   (`dpty-recipe.schema.json`): `definition` (id/rev/desc/owner/status),
   `requirements.accel` (backends, `min_mem_gb`, `gpu_count`, `arch`),
   `source`/`source.artifact`, `runtime` (engine/api/base_url/args/env/health),
   `lifecycle`, `record`. Source of truth for documents: `wismut/dpty-recipes`.
2. **Work Request** — intent + policy: priority `0`(critical)–`3`(low), unload
   policy (`unloadable-at-will`/`block_until`/`never`), purpose, owner.
3. **Instance** — the living thing: recipe + placement + who/why/priority/unload
   + started + expected.

## Operating rules

The operator-side behaviours that differ from default — **apply every one, every run**:

- **Match `observed`, never `declared`.** A recipe's accel constraint binds
  against what introspection found, not what Ansible intended. An arch pin
  (`arch=["sm_120a"]`) matches ONLY a box of that arch; empty `arch` matches any
  acceptable backend. On `declared` ≠ `observed` **drift**, do not match and report.
- **Read the ledger for truth.** `dpty status` shows the local ledger + capability
  snapshot (drift surfaced). The queue is a ledger of intent + capacity check,
  never a scheduler.
- **Place explicitly, stamp provenance.** `dpty request --recipe <id> [--priority N]`
  — consumers place work; dpty picks + executes. Enqueue stamps AGENT_CTX
  provenance (owner/purpose/agent/address/machine/model). Phone (xlatch) uses the
  grant/device id; protected mode clears AGENT_CTX by design.
- **Unload explicitly + logged.** `unloadable-at-will` unloads freely; a
  `never`/`block_until` unload requires the Governor. Never unload silently.
- **Report to gvnr, facts only.** `register` (capability snapshot) and
  `heartbeat` (liveness + free vram/disk + `assets_changed`) are the only
  registry facts; `events` is best-effort audit and **never creates facts**.
  Address = routing hint, never authorization. HTTPS + token; never SSH.
- **Fleet view via gvnr, not local inference.** `dpty --fleet`,
  `list_runners?cap=`, `resolve/{id}`.

## Demand bar

Operating dpty is **done** only when: no placement proceeds against `declared`
alone, no unload goes unlogged, no fact is created by an `event`, and every
operating rule above is applied.