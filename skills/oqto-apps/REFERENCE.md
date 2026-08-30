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


## Files capability v0.1 (contract — tracked as oqto-xcgg)

```ts
interface OqtoFileRef {
  id: string;        // opaque, stable within the binding scope
  name: string;
  mime: string;
  size: number;
  version: string;   // opaque version token; changes on every write
}

interface OqtoWriteOptions { expectedVersion?: string }

interface OqtoFilesCapability {
  pick(opts?): Promise<OqtoFileRef | null>;
  pickMultiple(opts?): Promise<OqtoFileRef[]>;
  read(ref): Promise<{ bytes: Blob; ref: OqtoFileRef }>;
  write(ref, data: Blob, opts?: OqtoWriteOptions): Promise<OqtoFileRef>;
  writeNew(name: string, data: Blob): Promise<OqtoFileRef>;
  stat(ref): Promise<OqtoFileRef>;                      // no bytes
  watch(ref, cb: (ref: OqtoFileRef) => void): Promise<() => void>;
}

// Conditional write conflict:
class OqtoConflictError extends Error {
  currentVersion: string;
  current: OqtoFileRef;   // re-read and rebase from here
}

// Host-driven open ("Open with <app>", bound tab):
interface OqtoHostContext {
  instanceId: string;
  bound?: { ref: OqtoFileRef; role: "document" };
}
```

Semantics: `version` is opaque — treat as a token, round-trip it. `write` with
`expectedVersion` performs an atomic host-side replace and rejects with
`OqtoConflictError` on mismatch; without it the write is last-writer-wins
(never use for documents other agents edit). `stat` is the cheap staleness
check; `watch` replaces polling where the host supports events. `read` returns
the current version alongside the bytes. The bound resource arrives in host
context at mount — read it via `files.read(host.context.bound.ref)`. Refs are
opaque (work-directory id + policy-checked relative reference internally);
never construct or parse them.

## Authoring rules (full)

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

