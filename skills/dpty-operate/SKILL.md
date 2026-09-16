---
name: dpty-operate
description: Operate a dpty machine unit — introspect capability, match and run recipes, place and supervise Work Requests/Instances, handle unload policy, and report to gvnr over the mesh. Use when running dpty on a machine, placing work on the fleet, writing or debugging recipe matching, reading the ledger, or handshaking with gvnr. Not for authoring the dpty Rust codebase (that is AGENTS.md/DESIGN.md).
---

# dpty operate

`dpty` (deputy) is the byteowlz per-machine compute unit. It reads **recipes**
from `wismut/dpty-recipes`, runs + supervises **Instances**, keeps a
**Work-Request/Instance ledger**, and reports **facts/events** to **gvnr** over
HTTPS+token on the overlay mesh. Read `README.md`/`DESIGN.md` before using.

## Non-negotiable boundaries

- **LEDGER, not scheduler.** The queue is a ledger of intent + capacity check.
  dpty never presents as a centralized priority scheduler (no fair-share /
  preemption / auto-placement). Never add one.
- **gvnr never dispatches.** gvnr resolves + lists only. Consumers place work;
  dpty picks + executes. Reachability ≠ authority.
- **Transport:** gvnr ↔ dpty is HTTPS + Bearer token (or mTLS) over the overlay
  mesh (`100.64.0.x`). Never SSH on the registry bus. SSH is ops-only.
- **Unload is explicit + logged.** A `never` / `block_until` unload requires the
  Governor (`dpty-core::model::Instance::transition`).
- **Ansible = provisioning; dpty = workload supervision.** dpty introspects
  read-only; it never installs drivers/CUDA/OS packages.

## The three-layer model

1. **Recipe** — how-to-run TOML manifest. Source of truth `wismut/dpty-recipes`.
   Grammar owned by dpty (`dpty-recipe.schema.json`). Fields: `definition`
   (id/rev/desc/owner/status), `requirements.accel` (backends, `min_mem_gb`,
   `gpu_count`, `arch`), `source`/`source.artifact` (typed origin), `runtime`
   (engine/api/base_url/args/env/health), `lifecycle`, `record`.
2. **Work Request** — intent + policy: priority `0`(critical)–`3`(low), unload
   policy (`unloadable-at-will`/`block_until`/`never`), purpose, owner.
3. **Instance** — the living thing: recipe + placement + who/why/priority/unload
   + started + expected.

## Capability introspection

On start (and on a refresh interval) dptyd acquires the machine capability
manifest via `dpty-core::capability::Introspector`:

```
Introspector::with_options(IntrospectionOptions { machine_id, mesh_ip,
  declared_file, probe_engines })
  .acquire()?                       -> CapabilityManifest
```

- **Backend-agnostic, cross-platform.** `Backend` enum covers `cuda`, `rocm`,
  `level-zero`, `metal-mps`, `vulkan`, `opencl`, `directml`. No NVIDIA/
  CUDA hardcoding.
- **Uniform `mem_gb`** across dedicated VRAM AND Apple unified memory;
  `arch` uses per-backend nomenclature (`sm_120a` / `gfx90a` / `m3`).
- **`declared` (Ansible/install intent) vs `observed` (introspection).**
  `manifest.drift()` returns a `DriftReport`; if `has_drift()`, surface the
  drifts before placement (e.g. declared CUDA 13.3 vs observed 12.9).
- Persist with `read_json_file`/`write_json_file(manifest, path)`.

## Recipe matching

Match a recipe's `requirements.accel` against the **observed** manifest, never
`declared` alone:

- `Device.meets_mem(min_mem_gb)` — uniform mem check.
- `Device.meets_arch(accepted)` — arch pin. A `cuda`+`sm_120a` recipe matches
  ONLY a CUDA/Blackwell box; an `arch=[]` recipe matches any acceptable backend.
- On drift that would violate the constraints, do **not** match and report.
- Assets fold into placement: static capability ∪ dynamic asset cache
  (`Assets { models, workflows }`), so a recipe whose model/workflow is already
  cached is preferred.

## Placing work

Consumers place work; dpty picks + executes.

```
dpty request --recipe <id> [--priority N]
```

- Stamp provenance from the enqueuing agent's `AGENT_CTX` (owner←`USER_ID`,
  purpose←`SESSION_NAME`, agent←`AGENT_ID`, address←`AGENT_ADDRESS`,
  machine←`MACHINE_ID`, model←`MODEL`). Phone-initiated (xlatch) uses the grant/
  device id; protected mode clears env so AGENT_CTX does not flow (by design).
- `dpty status` — local ledger + capability snapshot (drift surfaced).
- `dpty --fleet` — fleet view **resolved from gvnr** (never local inference).

## Running + supervisison

`dptyd` runs one unit per machine: acquires the manifest, maintains the ledger,
runs + supervises Instances (recipe loader, instance supervisor, `ledger.jsonl`),
and reports to gvnr:

- `RegisterReq` (runner_id + capability snapshot + token nonce) — POST `/register`
- `HeartbeatReq` (runner_id, ts, `free_vram_gb`, `free_disk_gb`,
  `assets_changed`) — POST `/heartbeat`
- `EventMessage` (ts, type, runner_id, payload) — POST `/events` (best-effort
  audit log — **never creates facts**)

Wire client: `dpty_wire::WireClient` (`HeartbeatReq`, `now_ts`). Messages
conform to `gvnr-dpty-wire.schema.json` (canonical home `byteowlz/gvnr`).

## Unload

Explicit + logged. `unloadable-at-will` unloads freely (logged); `never` /
`block_until` requires the Governor via `Instance::transition`. Never unload
silently.

## Fleet resolution (via gvnr)

- `GET /list_runners?cap=<recipe-or-caps>` — ranked capable runners (filter on
  capability snapshot).
- `GET /resolve/{id}` — resolve a runner address. **Address = routing hint,
  never authorization.**

## Recipes on disk

`wismut/dpty-recipes` holds the catalog; dpty reads it. Example in this repo:
`recipes/dsv4-flash-vision.toml` (DeepSeek-V4-Flash-Vision on 2× RTX PRO 6000,
backend `cuda`, `min_mem_gb=80`, `arch=["sm_120a"]`, SGLang SM120 fork, DSpark
spec decode) and `recipes/sdxl-turbo.toml` (backend `["metal-mps","cuda"]`,
`min_mem_gb=16`, engine `dwarfstar`, api `comfyui`).

## Checks

- `cargo build`, `cargo test`, `cargo clippy --workspace`, `cargo fmt --check`.
- After any manifest/matcher change, add or update the capability-model tests
  (multi-platform, drift, arch-pin matching).