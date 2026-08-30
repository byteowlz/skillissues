# Oqto app examples

## Manifest (`oqto-app.toml`, TOML — never YAML)

```toml
schema = "oqto-app/v0"                # provisional pin; see ADR-0027 deferral

id = "quota-explorer"
version = "0.1.0"
title = { en = "Quota Explorer", de = "Quota-Explorer" }
description = "Inspect per-work-directory disk quota"

# TOML gotcha: every top-level key MUST come before the first [table] header,
# or it silently nests into that table.
presentations = ["declarative", "sandboxed-web"]
requested_capabilities = ["kv", "theme", "notifications"]
bindings = ["work-directory"]         # narrowest binding containing all data
default_binding = "work-directory"

[presentation.declarative]
profile = "oqto/tables-v1"            # versioned profile; host advertises support
entry = "ui/entry.json"               # validated UI data (JSON)

[presentation.sandboxed-web]
entry = "bundle/index.html"           # self-contained; CSP: packaged bundle only

[instance_state]                      # hot-switching across fidelity thresholds
versioned = true

[assets]
max_bytes = 2_000_000
```

Unknown fields are preserved by the resolver — never strip them.

## Sandboxed-web app skeleton (`@byteowlz/oqto-app-sdk`)

`src/main.tsx` — runtime metadata comes from the Host, not duplicated code:

```tsx
import { connectOqtoApp } from "@byteowlz/oqto-app-sdk";
import { OqtoHostProvider } from "@byteowlz/oqto-app-sdk/react";
import { createRoot } from "react-dom/client";
import { QuotaExplorer } from "./QuotaExplorer";

const host = await connectOqtoApp();
const root = document.getElementById("root");
if (!root) throw new Error("Missing #root");
createRoot(root).render(
  <OqtoHostProvider host={host}><QuotaExplorer /></OqtoHostProvider>,
);
```

`src/QuotaExplorer.tsx` — reach the world only through granted capabilities:

```tsx
import { useOqtoHost } from "@byteowlz/oqto-app-sdk/react";
import { useState } from "react";

export function QuotaExplorer() {
  const host = useOqtoHost();
  const [picked, setPicked] = useState("none");

  return (
    <main>
      <h1>Quota Explorer</h1>
      <p>Picked: {picked}</p>
      <button onClick={async () => {
        if (!host.files || !host.kv) return;
        const [file] = await host.files.pick({ accept: ["text/*"] });
        if (!file) return;
        await host.kv.set("lastOpenRef", file.ref);
        await host.notifications?.notify({ level: "success", message: `Picked ${file.label}` });
        setPicked(file.label);
      }}>
        Pick usage report
      </button>
    </main>
  );
}
```

No shell registry step exists: Oqto discovers the manifest/bundle at runtime. For
standalone tests, use `createTestHost()` from `@byteowlz/oqto-app-sdk/testing`.

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
- [ ] every capability the code touches is requested in manifest
      `requested_capabilities` (requests remain separate from grants)
- [ ] `bindings` is the narrowest scope that contains all data
- [ ] `bundle/` is self-contained — grep for `http://`, `https://`, `fetch(` against
      non-packaged origins
- [ ] declarative payloads validate against the declared profile; a fallback is
      declared if the profile may be unavailable
- [ ] unknown manifest fields left intact
- [ ] all top-level keys appear **before** the first `[table]` header (TOML nests
      anything after a header into that table)
