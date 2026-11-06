# Reference

Read [SKILL.md](SKILL.md) first. These are engineering defaults informed by the Bitter Lesson, not consequences proven by it. Apply them against actual workloads and constraints.

## The ten defaults, expanded

### 1. Separate inference, policy, and enforcement

A suggested contact merge is inference. Whether unattended merges are allowed is policy. Applying an authorized merge without losing references is mechanism. Referential integrity is an invariant.

The core is allowed to make decisions: reject invalid input, enforce access, exclude opted-out contacts, calculate totals. These are not obsolete merely because a model can reason about them. Keep uncertain predictions distinct from recorded facts and explicit decisions. Record supporting evidence and uncertainty where useful.

Policies may evolve or use model outputs, but the authority to adopt them is separate from the model's ability to propose them. Text from a record, a retrieved document, or an agent's self-reported identity does not grant permission.

### 2. Protect durable assets and contracts

Preserve source evidence, user-authored data, stable identities, links, adopted decisions, and the contracts that explain their meaning. Provide migrations and exports that retain semantics, not merely bytes. Historical decisions may require the policy or model version that produced them.

Plain text is useful, but not uniquely durable. SQLite with a documented schema and reliable exports can be as legitimate as files. Files do not automatically provide referential integrity, safe concurrency, or trustworthy history. Storage choice follows workload, ownership, and recovery requirements.

A derived artifact is disposable only if its sources and derivation are available and rebuilding it is operationally feasible. Do not delete expensive caches or unique outputs simply because they are theoretically reproducible.

### 3. Make faithful transformations reproducible where appropriate

Distinguish these properties:

- **Determinism:** identical specified inputs and relevant state yield identical output.
- **Idempotency:** repeating an operation has the same intended effect as doing it once.
- **Atomicity:** a defined group of changes commits together or not at all.
- **Auditability:** evidence supports understanding what occurred, within a stated trust boundary.

None implies the others or guarantees correctness. A deterministic transform can be wrong; a repeated append can duplicate data; a transactional update can lack attribution.

Use reproducible serialization, calculations, exports, and pinned-input builds where helpful. Make clocks, source versions, and external responses explicit when replay matters. Preserve original generated content rather than assuming another model call will reproduce it.

Do not weaken secure randomness to obtain repeatable ciphertext. Concurrency and live systems have changing inputs; define consistency and retry behavior instead of pretending they are pure functions. Tests can control entropy and clocks without imposing those controls on production security.

### 4. Share authoritative state and mutation semantics across surfaces

Human and agent interfaces can have different ergonomics and permissions. Interactive completion, accessibility affordances, structured output, and batch APIs are legitimate features, not necessarily temporary scaffolding.

Use common domain operations where practical. Intentional restrictions should gate those operations rather than create contradictory implementations. Direct file or SQL access can bypass application checks; document that trust boundary and how external modifications are detected or reconciled. A shared format alone does not enforce a shared mutation contract.

Do not mandate every possible interface. Provide the surfaces users need and avoid trapping essential state or operations in an undocumented implementation.

### 5. Make intelligence replaceable when the benefit warrants it

Embedding a model in an application is not inherently contrary to the Bitter Lesson; adopting scalable learned methods can be an application of it. An external agent also introduces dependencies, latency, and failure modes. A shell-out is not automatically a sound architectural boundary.

Use clear input/output contracts and evaluation cases where models are likely to change. Preserve raw evidence independently of predictions. Keep access and mutation checks effective regardless of which model supplies a proposal.

Compare embedded inference, external inference, deterministic algorithms, and simple heuristics on quality, latency, cost, privacy, offline availability, and failure consequences. Prefer a cheap adequate heuristic over an elaborate abstraction when evidence supports it. Do not build a general model-provider framework for a hypothetical future need.

### 6. Choose the smallest adequate extension mechanism

Data is excellent for mappings, parameters, templates, and bounded policies. Code is often clearer for new algorithms, connectors, and complex behavior. A configuration language with loops, conditions, and opaque evaluation errors may be a worse programming language, not simpler architecture.

Choose based on expressiveness, validation, testing, deployment, and trust boundaries. Recompilation may be acceptable. Runtime plugins need versioning and security controls; runtime-loaded data can also carry unsafe behavior. Model authorship does not make either trustworthy.

### 7. Grow domain vocabulary from demonstrated needs

Prefer a small, meaningful schema over speculative ontologies. Allow notes or namespaced extension fields where they serve real work, with size limits, validation, and a promotion path for recurring concepts.

Do not hide important semantics in free text merely to keep the schema small. Money, permissions, identifiers, and lifecycle states often deserve explicit types early. Unknown fields must not silently grant authority or change behavior. Distinguish an adopted domain fact from an annotation or model suggestion.

### 8. Keep convenience layers replaceable without losing unique state

Ask what is lost if a GUI, wizard, search component, or assistant is removed. Unique annotations, review decisions, and user preferences need a durable home or export path. Presentation state can remain local when its loss is acceptable and explicit.

Do not insist that deleting a useful component loses no capability: a search engine provides search, and an accessible UI provides real human access. The goal is to avoid accidental captivity of data and semantics, not to make every component useless.

A UI can reveal a genuine domain need. Adding a review decision to the shared schema may be correct; adding viewport geometry to a contact record is usually not. Judge the meaning, not which interface first requested it.

### 9. Prefer portable artifacts when the product promises artifacts

Issued invoices, reports, and exported documents generally benefit from self-contained assets and durable snapshots. Resolve needed references at production time when that matches the contract and permissions.

Live dashboards, collaboration tools, and current inventory views legitimately depend on services. Document those dependencies, freshness, offline behavior, and failure modes. A stale snapshot is not a substitute for a promised live answer. Embedding private data into an artifact can increase exposure; portability does not override access or retention policy.

### 10. Distinguish snapshots, caches, and live views

A **snapshot** preserves a particular state. A **cache** accelerates a derivation and has invalidation/rebuild rules. A **live view** reflects changing sources under an explicit consistency model. Label which you supply.

Track source versions, schema/model versions where relevant, and freshness. A rebuildable search index can still contain sensitive information and need access controls. A read-only export is not a second writable authority; bidirectional synchronization is a separate feature with conflict semantics and recovery costs.

## Explicit failure and the honest wall

Report invalid references, stale revisions, ambiguous identities, and incomplete operations with actionable diagnostics. A documented fallback is appropriate when safe and visible; never silently reinterpret permissions, fabricate evidence, or claim stale state is current. Error messages must not disclose secrets or inaccessible records.

Some information is irreducible: observations, captured images, external responses, original text, and human decisions cannot be reconstructed merely by retaining a schema. Carry the source when permitted. If only an approximation survives, label it as such. Even a derivable issued document may need its original snapshot to preserve what was actually delivered.

## Audit procedure

1. State the product goal, actual users, workload, and relevant trust boundaries. Read existing decisions before proposing changes.
2. Classify the important state and operations as evidence/state, inference, policy, and mechanism/invariants. Mixed features are normal; identify their boundaries.
3. Identify what better models might replace, and what they would still rely on. Do not assume capability improvements also solve latency, privacy, authorization, or availability.
4. Compare the current design with the simplest credible alternative. Count moved complexity: recovery protocols, synchronization, model operations, filesystem semantics, and configuration interpreters.
5. Test replacement and failure boundaries: model swaps, unavailable inference, stale edits, lost indexes, external edits, permission denial, and data export as relevant. Avoid claiming tests prove guarantees outside their scope.
6. Make a conditional keep/change/remove recommendation with evidence, uncertainties, and a concrete reversal criterion. Record significant accepted decisions in an ADR; do not rewrite a product from this lens alone.

Useful output shape:

| Component | Durable value | Replaceable inference | Policy/invariants | Recommendation and evidence |
|---|---|---|---|---|
| Example | What must survive | What may improve | What remains enforced | Keep/change/remove, why, verification |

## Summary

Preserve evidence and business state, enforce explicit constraints, and make inference replaceable where useful. Choose formats, interfaces, extension mechanisms, and runtime boundaries by demonstrated needs and measured costs. Better models are a design pressure, not a reason to abandon domain guarantees or human workflows.
