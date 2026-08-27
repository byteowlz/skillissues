---
name: design-probe-gallery
description: Build standalone design-probe galleries to explore UI variants BEFORE touching production code. Use when the user asks for UI/UX concepts, interaction mockups, navigator/layout explorations, theme or component comparisons, or says "mockup", "variant", "design probe", "gallery", "let's try X direction". Implements the byteowlz de-sloping-agent-ui workflow.
---

# Design Probe Gallery

Explore UI directions as standalone fixture artifacts, never inside the
product. One probe = N variants side-by-side, browser-verified, decision
recorded. Canonical example: `oqto_refactor/artifacts/oqto-ui/corner-mode-concepts/`.

## Quick start

```
artifacts/<tool>/<probe-name>/
  index.html   # gallery chrome: variant tabs + note panel + device frame(s)
  app.js       # state machine + per-variant render fns; "?v=N" cache-busted
  styles.css   # tokens at :root matching the product's palette (sample real colors!)
  README.md    # purpose, variants, decisions appended per revision
```

Serve read-only on the tailnet: `python3 -m http.server 8902 --bind <tailscale-ip>` from
the artifacts root, so the user can open it on a phone.

## Workflow

1. **Constraints first.** List workflows, states, platform limits, spatial
   rules that any variant must satisfy. New feedback during iteration is
   evaluated as a constraint change before implementation.
2. **3–4 variants, not 1.** Each is one entry in the gallery's variant tab
   list with a `<b>` note describing its tradeoffs. Compare, don't commit yet.
3. **Fixture data, real shape.** Seed deterministic fixtures at realistic
   scale/density (hash-seeded names/statuses). No product imports.
4. **Interaction fidelity.** Wire real pointer events (pointerdown/up,
   hold timers, drag select) — static frames hide gesture problems. Every
   hold/gesture action MUST have a plain-tap equivalent.
5. **Browser-verify every claim.** Use `agent-browser` (DISPLAY=:0): drive
   events via dispatched PointerEvents, assert geometry/DOM state via `eval`,
   screenshot each state. If you didn't screenshot it, it isn't verified.
6. **Record the outcome.** Append decisions to README.md ("v4: adopted X,
   superseded Y because Z"), commit as `docs(artifacts): ...`, post the URL.

## Conventions & pitfalls

- Cache-bust every revision: bump `?v=N` on CSS/JS links; users get stale
  bundles otherwise.
- Prefer layout-affecting fit (e.g. `zoom` driven by a `--phone-scale`
  variable) over `transform: scale()` for device frames — transforms break
  anchor math for overlay positioning (getBoundingClientRect returns zoomed
  coords; divide by the zoom factor).
- Pause overlays must claim full screen; route-level fallbacks must match the
  page background or they flash.
- Match product palette by *sampling* verified screenshots of the production
  UI, not by memory; flat surfaces, token hairlines, zero radius unless the
  product says otherwise.
- Mobile ergonomics: bottom = act, top = navigation; search and status should
  follow the user's stated placement (record it once, stop re-litigating).
- Gallery control panels overlap small viewports — provide a collapse button
  and keep notes short.

## After adoption

The winning variant graduates: port the anatomy into the product's dev-only
showcase/show route against scripted then live adapters. The probe stays as
the decision record.
