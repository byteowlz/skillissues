---
name: oqto-apps
description: Author user/agent-creatable Oqto apps per ADR-0038 — workspace-source apps (manifest + declarative UI data and/or self-contained sandboxed-web bundle) that the host discovers at runtime. Use when creating, reviewing, or debugging an Oqto app, writing an oqto-app manifest, or wiring app capabilities (files, kv, theme, notifications). Covers the sandboxed-web and declarative presentations; never YAML.
---

# Authoring Oqto apps (ADR-0038)

## What you are building

An **Oqto app** is workspace source that the host discovers at runtime:
a manifest, app source, tests, and relative assets — ordinary inspectable files,
never hidden state or installed blobs.

## Quick start

```bash
cd <workdir>/oqto-apps/<app-id>
pnpm install
pnpm typecheck && pnpm test && pnpm build
# use @byteowlz/oqto-app-sdk/testing for deterministic host/concurrency tests
```

App skeleton, manifest example, and sanity checklist: see [EXAMPLES.md](EXAMPLES.md).
Full contract and capability semantics: see [REFERENCE.md](REFERENCE.md).

## App layout (working convention — provisional)

```
<workdir>/oqto-apps/<app-id>/
  oqto-app.toml          # manifest (TOML, schema "oqto-app/v0")
  src/                   # app source (see EXAMPLES.md for the SDK skeleton)
  bundle/                # built sandboxed-web entry (self-contained)
  ui/                    # declarative UI data payloads (JSON)
  test/                  # app tests
```

Everything about this layout except the vocabulary is provisional: the recognized
filesystem roots and the resolver are specified in ADR-0038 but not implemented
(`oqto-171p`). Keep the layout mechanical so migration is a move, not a rewrite.

## Hard rules

1. Only surface to the outside world: `connectOqtoApp()` and its granted
   capabilities (`files`, `kv`, `notifications`, `theme`). No `fetch` to Oqto,
   DOM/window escape, shell/store import, credential, path, mount, or socket.
2. Theme via read-only Host theme snapshots/tokens — never mutate or hardcode Oqto
   appearance.
3. Capabilities used must appear in manifest `requested_capabilities`; a request
   is not a grant. Test with `@byteowlz/oqto-app-sdk/testing`.
4. Bundles are self-contained (CSP: packaged bundle only, no CDN, no network).
5. Declarative payloads are data only, validated against the advertised profile,
   with a declared fallback.
6. Manifests are TOML — never YAML.

## Verification loop

The SDK test Host exercises the real MessageChannel protocol — no running Oqto
required. Test host-driven bound resources, external-writer conflicts, watcher
coalescing, missing grants, and disconnects. Then run the App's own preview and
screenshot loop at real viewports (1440×900, 390×844).

## Boundary — do not fabricate

The runtime side of ADR-0038 is **designed, not implemented**: filesystem
discovery/resolver, Installation/Instance/binding records, live capability grants,
the Gate, and OqtoUI iframe host. The SDK and Bridge protocol exist locally in
`~/byteowlz/oqto-app-sdk`; the live adapters do not. If your task requires those,
stop and say so — track against `oqto-efbj` / `oqto-xcgg` — instead of inventing loader code, grant APIs, or
manifest fields the host will never read. When asked how the app gets "installed"
today, the honest answer is: it doesn't; it runs standalone via the workbench and
is structured for discovery.

## Reference

Full contract, capability semantics, and authoring rules: [REFERENCE.md](REFERENCE.md).
Examples, manifest, and sanity checklist: [EXAMPLES.md](EXAMPLES.md).

## Open questions — ask, don't assume

- Binding kind and capability set beyond the SDK's initial four (ADR-0038 lists more).
- Whether the app needs a Sidecar (server-side execution — ADR-0027, gated).
- Catalog/distribution mechanics (deferred in ADR-0027).
