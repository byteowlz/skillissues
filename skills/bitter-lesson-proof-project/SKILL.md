---
name: bitter-lesson-proof-project
description: Design or audit a software tool so its value survives better models. Use when architecting or reviewing a tool, deciding whether something should be a feature, or when someone invokes the bitter lesson or worries a tool will be obsoleted by stronger AI.
---

# Designing for better models

The skill name is a discovery handle, not a promise of being future-proof. Use this as a critical design lens, not an architectural law or a reason to endorse the user's preferred design.

## What the Bitter Lesson does and does not establish

Rich Sutton's [The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html) describes a historical pattern in AI: general methods that leverage computation, particularly search and learning, have outperformed approaches built around human domain knowledge over the long run.

That motivates asking whether bespoke reasoning scaffolding will survive better models. It does **not** establish that files beat databases, all judgment must be external, deterministic software is future-proof, or configuration is better than code. The guidance below is engineering inference, not a theorem derived from Sutton.

> **Let better models improve reasoning without replacing durable records or weakening guarantees.**

## Quick start: separate four concerns

For a feature, identify:

1. **Evidence and state:** observations, source records, user-authored content, decisions, and history that must survive implementation changes.
2. **Inference:** estimates, rankings, classifications, and proposals that may improve with a different model or algorithm. Make these evaluable and replaceable where worthwhile; do not silently promote them to facts.
3. **Policy:** explicit choices about permissions, consent, risk, cost, and workflow. Record who may set them. A stronger model does not acquire authority to change them.
4. **Mechanism and invariants:** transactions, validation, access checks, conflict detection, encryption, and faithful transformations. Enforce the promised guarantees independently of model suggestions.

These concerns can share a process or application. Separation means clear responsibilities and contracts, not mandatory microservices or shell-outs. A policy may itself be model-assisted; its adoption and enforcement still need explicit authority.

Read [REFERENCE.md](REFERENCE.md) for details and the audit procedure, and [EXAMPLES.md](EXAMPLES.md) for retrieval, CRM storage, and encryption cases.

## Questions before recommending a change

1. **Actual value:** what human workflow or measurable outcome does this feature serve? Do not replace user needs with model convenience.
2. **Better-model counterfactual:** if relevant model capability improves substantially, which parts become redundant, which become more useful, and which guarantees remain necessary? Separate capability from price, latency, privacy, and availability assumptions.
3. **Replacement:** can inference change without losing evidence, corrupting state, or bypassing policy? What migration and evaluation would a swap require?
4. **Correctness:** what must be reproducible, idempotent, transactional, or auditable? These are different properties. Name necessary randomness and external state.
5. **Shared semantics:** do interfaces use the same authoritative state and mutation rules? Are capability differences deliberate access policy rather than accidental gaps?
6. **Total complexity:** does the design remove complexity or move it into synchronization, a configuration language, a filesystem adapter, or operations?
7. **Evidence against the recommendation:** what simpler alternative could work, and what observation would change your mind?

## Ten design defaults, not commandments

1. **Separate inference, policy, and enforcement.** Replace uncertain reasoning without delegating authority or integrity to it.
2. **Protect durable assets and contracts.** Preserve source evidence, user data, identities, schemas, decisions, and migration paths.
3. **Make faithful transformations reproducible where appropriate.** Do not force determinism onto cryptography, concurrency, or genuinely live inputs.
4. **Share authoritative state and mutation semantics across surfaces.** Different permissions and ergonomics are legitimate.
5. **Make intelligence replaceable when the benefit warrants it.** Embedded models, external agents, and simple heuristics are all candidates; compare measured quality and operating costs.
6. **Choose the smallest adequate extension mechanism.** Data for parameters and templates; code for behavior when clearer. Recompilation is not inherently a design failure.
7. **Grow domain vocabulary from demonstrated needs.** Keep schemas small but enforce important semantics; bound and validate extension fields.
8. **Keep convenience layers replaceable without losing unique state.** Preserve user annotations and accessibility; allow justified domain-schema evolution.
9. **Prefer portable artifacts when the product promises artifacts.** Live services need explicit dependencies and failure behavior, not fictional self-containment.
10. **Distinguish snapshots, caches, and live views.** Specify source versions, freshness, rebuild costs, and access controls.

## Honesty requirements

- Do not call something obsolete merely because a model could reproduce it. Cost, reliability, offline use, accessibility, and latency can justify it.
- Do not mistake deterministic output for correct output, attribution for authenticated identity, or a model upgrade for permission.
- Report consequential ambiguity and stale state explicitly. Safe, documented fallbacks are allowed; silent changes to meaning or authority are not.
- Carry irreducible evidence rather than pretending to regenerate it. A reconstruction or inference is not the original observation.
- Give a conditional recommendation with trade-offs and a concrete verification step. Do not use this skill as a mandate for an unrequested rewrite.
