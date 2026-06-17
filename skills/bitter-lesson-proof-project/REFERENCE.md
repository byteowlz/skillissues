# Reference

Full detail behind `SKILL.md`. Read `SKILL.md` first for the one-cut framing and the litmus test; this expands each of the ten rules, the fail-loud corollary, the honest wall, and how to audit an existing project.

## The ten rules, expanded

### 1. Separate judgment from mechanism

The core is a deterministic transform over plain inputs. All judgment — what to make, which to choose, what's good, what's relevant — belongs to the operator (human or agent). Expose levers; never pull them. A tool that decides *for* the user competes with the user's model and loses as that model improves.

### 2. The durable assets are data + the deterministic contract

Put your effort into the input formats (a real schema), the deterministic transform, and the user's accumulated data. These survive model turnover. Workflows, wizards, dashboards, and clever automations are disposable — assume you'll rewrite them when models shift, and design so that's cheap (they hold no unique state and no data only they understand).

### 3. Compute deterministically; reserve generation for the judgment layer

Where a transform *can* be reproducible, make it reproducible: idempotent, diffable, cacheable. **Regeneration is not idempotent** — ask a model to "redo" a thing and it can hand back a subtly different version, even of facts you gave it. Keep model calls (and any nondeterministic step) at the judgment layer, never in the substrate that's supposed to be a faithful function of its inputs. "Fresh" should mean *recomputed from source*, not *re-generated from scratch*.

### 4. Every surface over one substrate

Humans and agents have genuinely different ergonomic optima — interactive selection, completion, color, fuzzy "did-you-mean" for a human; structured output, deterministic exit codes, non-interactive batch input for an agent. Serving each well is good design, not waste. But *which* surfaces exist is the author's call, driven by who the tool actually serves: it may ship a human UI and an agent mode, just one, or nothing beyond the core. None is mandatory — a human-ergonomic interface is fine to have, not a must.

The invariant is not "build both," not "one interface," and *not* "identical capabilities everywhere" — it's two narrower things about whatever surfaces you build:

- **One canonical substrate.** Every surface drives the same plain data and the same core operations. Agent modes (JSON in/out, `--no-input`) are thin adapters that converge to the canonical form, not a parallel implementation with its own semantics or state. Two implementations drift; one substrate with several front-ends does not.
- **Capability differences are policy, not accident.** Surfaces may *deliberately* expose different capabilities — an auth layer gating destructive operations behind a human login, an agent sandboxed to a safe subset, role-based access. That is least-privilege design (mechanism vs policy): the gate sits *over* the shared substrate deciding who may invoke what; it does not fork the substrate. What you avoid is a feature *stranded* in one surface because nobody exposed it elsewhere, or a forked path that bypasses the auditable core. Asymmetry by chosen policy is good; asymmetry by neglect is the smell.

What to actually avoid: a *forked* agent implementation that bypasses the human-auditable substrate, and over-investing in elaborate agent-specific protocol that bakes in today's agent quirks — that scaffolding is what a better model routes around. A JSON mode most humans never touch is good design, not scaffolding: it's the right shape for a consumer that parses instead of reads.

### 5. No embedded intelligence in the core

The core makes no model calls and ships no judgment heuristics. It may *shell out* to a model/agent the user configured (a name in a config), but the judgment always lives outside the core. The intelligence operating your tool is the only intelligence the tool needs to contain.

### 6. Extension points are data, not code

Whatever your tool's units of extension are — rules, transforms, templates, connectors, policies, validators, checks — make them user-authored data loaded at runtime, not a hardcoded registry/switch in your source. Ship the built-ins *in that same format* (embedded in the binary, overridable by user files). Then a new capability is "author a new file," seconds of agent work, and expressiveness scales with model capability instead of being frozen at compile time. **Anything that requires recompiling to extend is the bitter-lesson smell.**

### 7. Grow vocabulary by promotion, never speculation

Give the format a small, stable core vocabulary **plus an unbounded escape hatch** (a raw/free-form field for the long tail). When a pattern recurs in the escape hatch across many uses, *promote* it into the core vocabulary. Never add a field/option speculatively for a use you merely imagine. The escape hatch absorbs the tail; promotion keeps the core small and earned.

### 8. Disposable satellites, never colonization

Interactive or convenience layers — GUIs, servers, builders, assistants — are welcome as **satellites** over the core, under hard rules: (a) deleting one loses no data and no capability, only convenience; (b) a satellite **never extends a core format** to serve itself — it derives what it reads from existing structure and writes only what the format already expresses. The moment a convenience layer needs a new field in your core data model, it's eroding the lean core one defensible field at a time.

### 9. Self-contained, portable outputs

Outputs must not depend on services at *use* time (no remote assets, license servers, live re-queries, or APIs fetched when the artifact is consumed). Resolve and embed dependencies at build time. Build-time network/compute is fine; *use-time* dependency is hidden coupling that rots and takes the artifact hostage to whatever it calls.

### 10. The build/artifact boundary

The build resolves every reference; the artifact never points back into the machine or service that produced it. Sources can live anywhere and reference each other freely; the *built thing* is frozen and portable. This is what makes outputs diffable, cacheable, archivable, and shippable.

## Fail loud — a determinism corollary

A deterministic tool must never silently substitute or guess. A missing reference, an ambiguous name, an unknown option → fail with a precise error naming what was searched and what's available. That error message is exactly what an agent needs to self-correct, so **fail-loud is the agent-friendly behavior.** A silent fallback that "still produces output" is the worst outcome: it ships wrong and is discovered late.

## The honest wall — what is not factorable

Some things are **derivable** (a function of inputs the tool can recompute) and some are **irreducible** (data the tool can only carry, never regenerate):

- Derivable: a computed total, a formatted document from structured data, a query result, anything a rule or transform produces. Factor these — express the rule, not the output.
- Irreducible: a measured value, a recorded signal, a human judgment call, a hand-authored passage, an external system's response, a captured image. No "rebuild it declaratively" recovers these; the faithful move is to *carry the data* (embed it) or approximate it — and say which.

When you hit this wall, state it plainly: "this is irreducible data, not a derivable design — it can only be carried or approximated, not reconstructed." Pretending otherwise wastes effort and erodes trust. The wall is a property of the information, not a failure of the tool.

## How to audit an existing project

Walk the codebase and, for each subsystem, run the litmus test from `SKILL.md`. Flag:

- Heuristics that exercise taste/choice baked into the core → delegate or delete.
- Nondeterministic steps in the substrate (model calls, hidden state, clocks, network) where a reproducible transform belonged → make deterministic, or move the nondeterminism out to the judgment layer.
- Hardcoded enumerations where user-authored data belongs → make it a loadable format.
- A forked implementation behind one surface, or a capability *stranded* in one surface by neglect → unify on one substrate. (A capability difference that is deliberate policy — auth, sandboxing, least-privilege — is fine; only accidental fragmentation is the smell.)
- Core formats carrying fields that exist only to serve a GUI/satellite → revert; the satellite must derive them.
- Use-time dependencies on services in the output → resolve and embed at build.
- Silent fallbacks/substitutions → fail loud with searched paths + available options.

Record keep/cut decisions as short ADRs (hard-to-reverse + surprising + a real trade-off). The explicit *no*'s — "the core will never embed a model," "satellites never extend formats," "no forked agent implementation" — are as valuable as the yes's: they stop the next contributor from "helpfully" reintroducing the scaffolding.

## One-paragraph summary

Build a dumb, deterministic transform over plain data with clean orthogonal parts; delegate every judgment to the model or human operating it; put whatever surfaces your users need over one shared substrate (capability differences allowed as deliberate policy, not accidental fragmentation); keep extension points as user-authored data, not code; let GUIs and servers exist only as deletable satellites that never extend the formats; resolve and embed dependencies so outputs are self-contained forever; fail loud, never guess; and be honest that some information is irreducible data the tool can only carry, not reconstruct. Everything that *exercises taste* lives outside the tool, where the bitter lesson makes it better every year instead of making your tool obsolete.
