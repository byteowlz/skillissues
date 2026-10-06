# dpty-operate — symbol reference

Reached from [`SKILL.md`](SKILL.md) when you need exact type/method/endpoint
names. Read `AGENTS.md`/`DESIGN.md` for the authoritative boundaries.

## crates

Workspace members: `dpty-core` (domain lib), `dpty-wire` (wire client),
`dptyd` (daemon), `dpty-cli` (CLI `dpty`). Also `dpty-api`/`dpty-tui`/`dpty-mcp`
and `byteowlz-tui-kit`.

## Capability introspection (`dpty-core::capability`)

- `Introspector` / `Introspector::with_options(IntrospectionOptions)` /
  `.acquire()? -> CapabilityManifest` — auto-acquire from the running host.
- `IntrospectionOptions { machine_id, mesh_ip, declared_file, probe_engines }`.
- `CapabilityManifest` — `devices_for(Backend)`, `has_no_accel()`, `drift() ->
  DriftReport`, `to_json()`.
- `Backend` enum: `cuda`, `rocm`, `level-zero`, `metal-mps`, `vulkan`,
  `opencl`, `directml` — backend-agnostic, no NVIDIA/CUDA hardcoding.
- `Device { backend, name, mem_gb, arch, capabilities }`:
  `meets_mem(min_mem_gb)`, `meets_arch(&[String])`. `mem_gb` is uniform across
  dedicated VRAM AND Apple unified memory; `arch` uses per-backend nomenclature
  (`sm_120a`/`gfx90a`/`m3`).
- `write_json_file(manifest, path)` / `read_json_file(path)` — persist.
- `declared` (Ansible/install intent) vs `observed` (introspection); drift
  surfaced before placement.
- `Assets { models, workflows }` — dynamic cache folded into placement.

## Recipes on disk

- `recipes/dsv4-flash-vision.toml` — DeepSeek-V4-Flash-Vision on 2× RTX PRO 6000
  (backend `cuda`, `min_mem_gb=80`, `arch=["sm_120a"]`, engine `sglang`, SGLang
  SM120 fork + DSpark). Plus pinned `dsv4-flash-vision.setup.sh`.
- `recipes/sdxl-turbo.toml` — SDXL-turbo (backend `["metal-mps","cuda"]`,
  `min_mem_gb=16`, engine `dwarfstar`, api `comfyui`).
- `llm/qwen3.6-35b-a3b-nvfp4-fast.toml` — Qwen3.6 35B-A3B on a single DGX Spark
  (backend `cuda`, `min_mem_gb=36`, `arch=["sm_120a"]/GB10`, engine `vllm`,
  host-run via a pinned venv). See `scripts/qwen36-nvfp4-fast.setup.sh`.
- `llm/qwen3.8-flash-next.toml` — Qwen3.8-Flash-Next on a DGX Spark
  (containerized via a wrapper; engine `vllm`).
- Catalog home: `wismut/dpty-recipes`.

### DGX Spark / GB10 unified-memory gotcha

`nvidia-smi` reports `[N/A]`/`Not Supported` for `memory.total` on unified-memory
boxes (DGX Spark, GB10, GB300-class), so dpty previously introspected `mem_gb=0`
and any `min_mem_gb`-pinned recipe never matched. The CUDA adapter falls back to
the system unified RAM when every GPU parses to zero. When authoring a recipe
for such a box, pin `min_mem_gb` to what the model's resident working set
actually needs (e.g. ~36 GiB for qwen3.6-nvfp4-fast at 262K ctx), not the box's
total — `dpty recipe validate` will tell you if it matches.

## CLI (`dpty`)

- `dpty status` — local ledger + capability snapshot (drift surfaced).
- `dpty request --recipe <id> [--priority N]` — enqueue a Work Request
  (AGENT_CTX provenance stamped).
- `dpty recipe validate <id-or-path>` — validate a recipe against the schema +
  report placement against THIS machine's observed capability (MATCH/RANK or
  REJECT + reasons + drift). Accepts a recipe id (under `recipes_dir`) or a
  direct `.toml` path.
- `dpty recipe match <id-or-path>` — placement-only form (no schema re-check).
- `dpty --fleet` — fleet view resolved from gvnr (not local inference).
- `dpty service enable|disable|start|stop|status|run [--user]` — install/manage
  the dptyd daemon under the platform init (Linux systemd unit; macOS launchd
  agent; Windows fails loud).

## dptyd daemon

Runs one unit per machine: introspects capability, maintains the ledger
(`ledger.jsonl`), runs + supervises Instances, reports to gvnr.

## Wire messages (`dpty_wire::WireClient`, `now_ts`)

Conform to `gvnr-dpty-wire.schema.json` (canonical home `byteowlz/gvnr`):

- `HeartbeatReq` — runner_id, ts, `free_vram_gb`, `free_disk_gb`, `assets_changed`
  → POST `/heartbeat`
- `RegisterReq` — runner_id + capability snapshot + token nonce → POST `/register`
- `EventMessage` — ts, type, runner_id, payload → POST `/events`
- GET `/list_runners?cap=`, GET `/resolve/{id}` — fleet resolution.

## Model (`dpty-core::model`)

`Recipe` / `WorkRequest` / `Instance`; `Priority` (0–3), `UnloadPolicy`
(`unloadable-at-will`/`block_until`/`never`), `AgentProvenance`;
`Instance::transition()` (Never/block_until unload requires the Governor).

## Checks

`cargo build`, `cargo test`, `cargo clippy --workspace`, `cargo fmt --check`.
After any manifest/matcher change, update the capability-model tests
(multi-platform, drift, arch-pin matching).