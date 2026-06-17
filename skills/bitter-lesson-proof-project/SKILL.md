---
name: bitter-lesson-proof-project
description: Design or audit a software tool so its value survives better models. Use when architecting or reviewing a tool, deciding whether something should be a feature, or when someone invokes the bitter lesson or worries a tool will be obsoleted by stronger AI.
---

# Building bitter-lesson-proof projects

## Quick start

For any feature, make one cut. Ask: does it exercise **judgment** (taste or choice a model makes, and makes better each year) or is it **mechanism** (a deterministic transform of inputs)?

- **Judgment → delegate it.** Expose the lever; never pull it. Keep it out of the core.
- **Mechanism → build it**, and keep it reproducible: same inputs → identical output.

Every rule below follows from that cut. Worked cases: [EXAMPLES.md](EXAMPLES.md). Full detail on each rule and how to audit a project: [REFERENCE.md](REFERENCE.md).

## The thesis

Sutton's *bitter lesson*: general methods that scale with compute beat hand-engineered domain knowledge, eventually, every time. For tool-building, the corollary is: the parts of your tool that encode *judgment* are scaffolding a stronger model does better — building them into the core builds your own obsolescence. So build a dumb, deterministic substrate and delegate every judgment to the model or human operating it.

> **The factoring is the product.** A tool that cleanly decomposes its domain into orthogonal, plain-text, deterministically-composed parts is leverage for a model. One that bundles judgment into the mechanism is something a strong model routes around.

## The crucial subtlety

The lesson kills **hand-coded knowledge that competes with learning** — not clean data models, deterministic transforms, or orthogonal decomposition. Those are *normalization*, which gives a model clean levers. So: **normalize ruthlessly** (schemas, formats, clean separations) and **encode zero judgment** (no heuristic that chooses). Storing records in clean tables is engineering; "automatically flag the ones that matter" is the trap.

## Defaults, not laws

These are strong defaults and design pressures, not commandments — and they are not one-dimensional. Every rule bends for a deliberate, stated reason; what's forbidden is bending by accident, neglect, or scaffolding. The test for any deviation: is it **chosen policy with a reason** (an auth layer gating the human surface, a genuinely live artifact, a pinned offline model, a safety sandbox) or **accidental drift** (a feature stranded in one surface, a forked implementation, a hidden dependency)? The first is design; the second is the smell. Hold the rules as defaults and make exceptions on purpose, in the open.

## Litmus test — before building any feature

1. **10× test** — if the operating model gets 10× better, is this dead weight? → scaffolding.
2. **Judgment test** — does it exercise taste/choice a model could do better? → delegate.
3. **Determinism test** — same inputs → identical output? If not, nondeterminism leaked in.
4. **Substrate test** — do the surfaces share one substrate, and is every capability *difference* deliberate policy (auth/trust/safety), not a feature stranded in one surface?
5. **Deletion test** — delete the GUI/wizard/"smart" layer: lost *data/capability*, or only convenience?
6. **Extension test** — are extension points *data the operator authors*, or a hardcoded enumeration?

## The ten rules (detail in [REFERENCE.md](REFERENCE.md))

1. **Separate judgment from mechanism** — the core decides nothing; it exposes levers.
2. **Durable assets = data + the deterministic contract** — formats, transform, the user's data. Everything else is disposable.
3. **Compute deterministically; reserve generation for the judgment layer** — regeneration is not idempotent.
4. **Every surface over one substrate** — build whatever interfaces your users need (the author's call, none mandatory); keep them over one shared substrate (no forked implementation). Capability *differences* are fine as deliberate policy (auth, least-privilege, sandboxing), not as a feature stranded in one surface by neglect.
5. **No embedded intelligence in the core** — no model calls, no judgment heuristics; shell out if needed.
6. **Extension points are data, not code** — loaded at runtime; recompiling-to-extend is the smell.
7. **Grow vocabulary by promotion, never speculation** — small core + escape hatch; promote recurring patterns.
8. **Disposable satellites, never colonization** — convenience layers never extend core formats.
9. **Self-contained, portable outputs** — no use-time dependency on services; embed at build.
10. **The build/artifact boundary** — the build resolves refs; the artifact never points back at its maker.

**Fail loud** (a determinism corollary): never silently substitute or guess; fail with a precise error naming what was searched and what's available — that *is* the agent-friendly behavior.

**The honest wall:** some information is *irreducible* (a measurement, a human judgment, a captured image, an external response) — carry or approximate it, never pretend to derive it.

## See also

- [EXAMPLES.md](EXAMPLES.md) — worked cases run through this framework (semantic search, …).
- [REFERENCE.md](REFERENCE.md) — full rule explanations, fail-loud, the honest wall, and a project-audit procedure.
