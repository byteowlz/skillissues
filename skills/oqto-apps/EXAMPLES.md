# Oqto app examples

## Manifest (`oqto-app.toml`, TOML — never YAML)

```toml
schema = "oqto-app/v0"                # provisional pin; see ADR-0027 deferral

id = "quota-explorer"
version = "0.1.0"
title = { en = "Quota Explorer", de = "Quota-Explorer" }
description = "Inspect per-work-directory disk quota"

presentations = ["declarative", "sandboxed-web"]

[presentation.declarative]
profile = "oqto/tables-v1"            # versioned profile; host advertises support
entry = "ui/entry.json"               # validated UI data (JSON)

[presentation.sandboxed-web]
entry = "bundle/index.html"           # self-contained; CSP: packaged bundle only

requested_capabilities = ["kv", "theme", "notifications"]
bindings = ["work-directory"]         # narrowest binding containing all data
default_binding = "work-directory"

# Hot-switching across fidelity thresholds requires compatible state.
[instance_state]
versioned = true

[assets]
max_bytes = 2_000_000
```

Unknown fields are preserved by the resolver — never strip them.

## Sandboxed-web app skeleton (mini-apps SDK)

`src/index.ts`:

```ts
import { defineOqtoApp } from "@/mini-apps/sdk";
import { QuotaExplorer } from "./QuotaExplorer";

export const quotaExplorerApp = defineOqtoApp({
  id: "quota-explorer",
  title: "Quota Explorer",
  description: "Inspect per-work-directory disk quota",
  requestedCapabilities: ["kv", "theme", "notifications"],
  component: QuotaExplorer,
});
```

`src/QuotaExplorer.tsx` — reach the world only via `useOqtoHost()`:

```tsx
import { useOqtoHost } from "@/mini-apps/sdk";
import { useEffect, useState } from "react";

export function QuotaExplorer() {
  const host = useOqtoHost();
  const [lastRun, setLastRun] = useState<string | null>(null);

  useEffect(() => {
    host.kv.get<string>("lastRun").then(setLastRun);
  }, [host]);

  return (
    <main style={{ padding: 16 }}>
      <h1>Quota Explorer</h1>
      <p>Last run: {lastRun ?? "never"}</p>
      <button
        onClick={async () => {
          const ref = await host.files.pick({ accept: "text/*" });
          if (!ref) return;
          await host.kv.set("lastRun", ref.name);
          host.notifications.notify(`Picked ${ref.name}`, "success");
          setLastRun(ref.name);
        }}
      >
        Pick usage report
      </button>
    </main>
  );
}
```

Register it for the standalone workbench (`frontend/mini-apps/workbench/registry.ts`):

```ts
import { quotaExplorerApp } from "@/mini-apps/quota-explorer";

export const standaloneApps: ReadonlyArray<OqtoApp> = [
  // ...existing apps
  quotaExplorerApp,
];
```

## Declarative payload (`ui/entry.json`, data only)

```json
{
  "profile": "oqto/tables-v1",
  "view": {
    "kind": "table",
    "title": { "en": "Mounts", "de": "Einbindungen" },
    "columns": [
      { "key": "path", "label": { "en": "Path", "de": "Pfad" } },
      { "key": "free", "label": { "en": "Free", "de": "Frei" } }
    ],
    "rows": [
      { "path": "/tmp", "free": "1.6 GB" }
    ]
  }
}
```

## Manifest sanity checklist

- [ ] `schema` present; TOML, not YAML
- [ ] `id` stable and kebab-case; `version` semver
- [ ] every capability the code touches is declared (check `requestedCapabilities`
      against actual `host.*` usage)
- [ ] `bindings` is the narrowest scope that contains all data
- [ ] `bundle/` is self-contained — grep for `http://`, `https://`, `fetch(` against
      non-packaged origins
- [ ] declarative payloads validate against the declared profile; a fallback is
      declared if the profile may be unavailable
- [ ] unknown manifest fields left intact
