---
name: dpty-operate
description: Operate a dpty machine unit — introspect capability, match recipes to observed capacity, place and supervise Work Requests, reserve capacity, manage loadouts, read the ledger, and report to gvnr. Use when running dpty on a machine, authoring or validating recipes, placing fleet work, reserving capacity for a job, changing a machine's loadout, or debugging recipe/capability matching.
---

# dpty operate

`dpty` (deputy) is the byteowlz per-machine compute unit. It reads **recipes** from
`wismut/dpty-recipes`, runs + supervises **Instances**, keeps the
Work-Request/Instance **ledger**, and reports facts/events to **gvnr** over
HTTPS + token on the overlay mesh.

The boundaries — **per-machine desired-state, not a fleet scheduler; facts
published, agent reasons; HTTPS+token not SSH on the registry bus;
explicit-and-logged unload; Ansible=provisioning / dpty=supervision** — are
defined in this repo's `AGENTS.md`/`DESIGN.md` and `govnr` ADR-0009 (project
nvridl). Read them; **this skill never relaxes them.** When a line here seems to
conflict, the repo docs win. The symbol-level API reference is disclosed to
[`details.md`](details.md); reach it when you need exact type/method/endpoint
names.

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

## Operating rules (project nvridl)

The operator-side behaviours that differ from default — **apply every one, every run**:

- **Match `observed`, never `declared`.** A recipe's accel constraint binds
  against what introspection found, not what a manifest intended. An arch pin
  (`arch=["sm_120a"]`) matches ONLY a box of that arch; empty `arch` matches any
  acceptable backend. On `declared` ≠ `observed` **drift**, do not match and report.
- **Read the ledger for truth.** `dpty status` shows the local ledger + capability
  snapshot (drift surfaced). The queue is a machine-owned backlog, not a fleet scheduler.
- **Desired-state, not a scheduler.** A machine's dpty reconciles Running instances
  to a **loadout** chosen by **rules** (role / time schedule / trigger / idle
  fallback). It may accept a **remote loadout directive** (authz + provenance);
  it never fair-shares/preempts across the fleet.
- **Reserve capacity explicitly.** `reserve` claims capacity on a machine for a
  lease; the machine validates against reality and accepts or rejects (telling
  *when free*). On lease end it auto-releases and **reverts to desired state**.
  The machine refuses double-booking. No queueing, no preemption for a reservation.
- **Facts published, agent reasons.** dpty/gvnr report honest, reservation-adjusted
  capacity (`total`, `available_after_current`, `available_if_reserved` + loadout +
  reservations + queue). **The agent sizes/places** — there is no auto-sizing or
  auto-placement layer.
- **Place explicitly, stamp provenance.** `dpty request --recipe <id> [--priority N]`
  — an agent enqueues work; the machine's dpty executes. Enqueue stamps AGENT_CTX
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

## Authoring a recipe (the how-to)

Use `dpty recipe validate` to check a recipe against the schema + this machine's
observed capability before committing to the catalog.

1. **Start from `_template.toml`** in `wismut/dpty-recipes`. Copy it, fill in
   the id/rev/desc/owner/status under `[definition]`.
2. **Set `[requirements]`** to match what the job actually needs:
   `accel.backends` (empty `[]` = no accelerator, match on ram/disk),
   `min_mem_gb`, `gpu_count`, `arch` (empty = any acceptable backend). These bind
   against **observed** capability.
3. **`[source]`** is a reproducible descriptor: `kind = git|binary|image|local`,
   with `url`/`ref` (git) or `sha256` (binary). Never an unverifiable "trust me".
4. **`[runtime]`** is how to launch: `engine`, `api`, `base_url`, `args` (`args[0]`
   is the EXECUTABLE dptyd spawns directly — a venv python, a binary, or a wrapper
   script), `env` (with `$VAR` substitution), and `health = {path, port, expect}`.
   For a Docker workload, `args[0]` is a wrapper script that runs `docker run`.
5. **`[lifecycle]`** sets `resume` (`restart-manifest` to relaunch after reboot;
   the persistent ledger IS that record) and `restart` (`on-failure` self-heals).
6. **`[record]`** adds `group`/`tags` for discovery. Set `status` to `prototype`
   until validated, `validated` once it runs clean, `graduated` when stable.
7. **Validate**: `dpty recipe validate <id-or-path>` — prints OK + a MATCH/RANK
   (or REJECT + reasons + drift) against the machine's observed capability.
   Iterate until it MATCHes.
8. **Commit + push** to `wismut/dpty-recipes` (rev bumps on change). The merged
   commit *is* the recipe registered — no server-side register step.

## Demand bar

Operating dpty is **done** only when: no placement proceeds against `declared`
alone, no unload goes unlogged, no fact is created by an `event`, every
reservation is validated against reality and auto-releases, and every operating
rule above is applied.