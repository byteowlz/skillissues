---
name: oqto-apps
description: Author user/agent-creatable Oqto apps per ADR-0038 — workspace-source apps (manifest + declarative UI data and/or self-contained sandboxed-web bundle) that the host discovers at runtime. Use when creating, reviewing, or debugging an Oqto app, writing an oqto-app manifest, or wiring app capabilities (files, kv, theme, notifications). Covers the sandboxed-web and declarative presentations; never YAML.
---

# Authoring Oqto apps (ADR-0038)

## What you are building

An **Oqto app** is workspace source that the host discovers at runtime:
a manifest, app source, tests, and relative assets — ordinary inspectable files,
never hidden state or installed blobs.

## The contract (ADR-0038, accepted 2026-08-09)

- An app is **workspace source**: manifest, source, tests, relative assets. Ordinary
  inspectable files — never hidden state, never installed blobs.
- Two optional presentations:
  - **declarative**: validated UI *data* (JSON payloads rendered by the host's native
    registry) — forms, tables, dashboards, approvals.
  - **sandboxed web**: a self-contained bundle (HTML/TS/JS) rendered in an
    iframe/WebView with CSP; egress only through granted capabilities.
- **No agent-authored React, Rust, Swift, or other code loads into an OqtoUI host
  process.** Your code runs in its own document (standalone workbench today,
  sandboxed frame later). This is a contract, not a preference.
- Capabilities (files, kv/instance-storage, notifications, theme, user; later:
  session input, navigation, dialogs, egress) are **declared, never self-granted**.
- Binding is the narrowest durable owner that contains the app's data
  (work-directory → workspace → account → deployment). Never widen silently.
- The manifest preserves unknown fields; assets are bounded; discovery rejects
  symlink escape and path traversal.

## No YAML

App implementation is code and data. Manifests are **TOML** (repo precedent:
`sandbox.toml`, `dependencies.toml`); declarative UI payloads are **JSON**
(validated against the host's advertised profile). If you find yourself writing a
`.yaml` file for an Oqto app, stop — that is out of contract. The manifest format
is provisionally TOML pending the format decision ADR-0027 deferred; the
`schema` key marks compatibility.

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

## Authoring rules

1. Use the mini-apps SDK (`frontend/mini-apps/sdk/`): `defineOqtoApp()` +
   `useOqtoHost()`. It is promise-based, serializable, and bridge-ready — the same
   app code runs standalone today and in the sandboxed frame later.
2. Reach the outside world **only** through the host capabilities on `useOqtoHost()`
   (`files`, `kv`, `notifications`, `theme`, `user`). No `fetch` to Oqto, no
   direct DOM/window escapes, no imports from the Oqto shell or its stores.
3. Theme via the `theme` capability (`Base24Scheme`/`ThemeMode`), never hardcoded
   colors. Derive from scheme tokens (see `mini-apps/theming/`).
4. Capabilities you use must be listed in `requestedCapabilities` and in the
   manifest. Extending the capability set means editing `sdk/host.ts` **and**
   `sdk/mock-host.ts` together — host contract and mock move in lockstep.
5. The bundle is self-contained: no external network, no CDN scripts. CSP defaults
   to packaged-bundle-only.
6. Declarative payloads carry no logic — data only, validated against the
   advertised profile; fail loudly with a declared fallback when unsupported.

## Verification loop

Standalone today (no running Oqto required — the mock host backs everything):

```bash
cd frontend
bun run typecheck:oqto-ui        # mini-apps are in tsconfig include
bunx biome check mini-apps/<app>
bunx vitest run                  # app tests live in frontend/tests/
bun run build                    # workbench.html is a vite entry
# open http://localhost:3000/workbench.html — mock host, real UI
```

Then the screenshot loop at real viewports (1440×900, 390×844) against the
workbench, same as shell parity work.

## Boundary — do not fabricate

The runtime side of ADR-0038 is **designed, not implemented**: filesystem
discovery/resolver, Installation/Instance/binding records, capability grants, the
Gate, bridge transport. If your task seems to require those, stop and say so —
track against `oqto-171p` — instead of inventing loader code, grant APIs, or
manifest fields the host will never read. When asked how the app gets "installed"
today, the honest answer is: it doesn't; it runs standalone via the workbench and
is structured for discovery.

## Open questions — ask, don't assume

- Binding kind and capability set beyond the SDK's five (ADR-0038 lists more).
- Whether the app needs a Sidecar (server-side execution — ADR-0027, gated).
- Catalog/distribution mechanics (deferred in ADR-0027).
