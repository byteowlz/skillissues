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
cd frontend
bun run typecheck:oqto-ui && bunx biome check mini-apps/<app>
bunx vitest run && bun run build
# open http://localhost:3000/workbench.html — mock host, real UI, no Oqto login
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

1. Only surface to the outside world: `useOqtoHost()` capabilities (`files`, `kv`,
   `notifications`, `theme`, `user`). No `fetch` to Oqto, no DOM/window escapes, no
   imports from the Oqto shell or its stores.
2. Theme via the `theme` capability (`Base24Scheme`/`ThemeMode`) — never hardcoded
   colors.
3. Capabilities used = capabilities declared (`requestedCapabilities` + manifest).
   Extending the set means editing `sdk/host.ts` **and** `sdk/mock-host.ts`
   together.
4. Bundles are self-contained (CSP: packaged bundle only, no CDN, no network).
5. Declarative payloads are data only, validated against the advertised profile,
   with a declared fallback.
6. Manifests are TOML — never YAML.

## Verification loop

The mock host backs everything — no running Oqto required. Run the quick-start
gates, then the screenshot loop at real viewports (1440×900, 390×844) against
`/workbench.html`, same as shell parity work. App tests live in `frontend/tests/`.

## Boundary — do not fabricate

The runtime side of ADR-0038 is **designed, not implemented**: filesystem
discovery/resolver, Installation/Instance/binding records, capability grants, the
Gate, bridge transport. If your task seems to require those, stop and say so —
track against `oqto-171p` — instead of inventing loader code, grant APIs, or
manifest fields the host will never read. When asked how the app gets "installed"
today, the honest answer is: it doesn't; it runs standalone via the workbench and
is structured for discovery.

## Reference

Full contract, capability semantics, and authoring rules: [REFERENCE.md](REFERENCE.md).
Examples, manifest, and sanity checklist: [EXAMPLES.md](EXAMPLES.md).

## Open questions — ask, don't assume

- Binding kind and capability set beyond the SDK's five (ADR-0038 lists more).
- Whether the app needs a Sidecar (server-side execution — ADR-0027, gated).
- Catalog/distribution mechanics (deferred in ADR-0027).
