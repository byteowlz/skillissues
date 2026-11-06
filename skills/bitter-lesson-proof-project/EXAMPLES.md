# Worked examples

Use these to challenge a recommendation, not to mechanically select an architecture. Each separates durable state, replaceable inference, explicit policy, and correctness mechanisms.

## Semantic search: replaceable retrieval, not a universal winner

**Question:** should a tool include embeddings and semantic ranking?

Learned retrieval is consistent with the Bitter Lesson, but embeddings have not universally displaced lexical search. Exact identifiers, rare terms, names, and specialist vocabulary can favor lexical methods; semantic or hybrid methods may do better on other queries. Measure against the actual task.

Both candidate selection and final ranking encode relevance assumptions. A reranker cannot recover a relevant document the candidate stage omitted. "Recall is mechanism, ranking is judgment" is therefore not a clean architectural boundary. Deterministic fuzzy or lexical retrieval also makes choices about matching and ordering.

**Durable assets:** source documents, stable identifiers, access metadata, and any reviewed relevance judgments. Embeddings and search indexes can be versioned derived artifacts if their sources are retained. Account for rebuild expense and access restrictions.

**Replaceable components:** lexical, vector, hybrid, reranking, and agent-directed search. A vector score can be the final ranking if it meets the task's quality and cost requirements; a model reranker is not mandatory. Longer context and better agents may change the trade-off, not automatically eliminate retrieval.

**Policy and mechanism:** enforce document access before disclosure, track freshness, preserve source citations, and handle unavailable components honestly. Keep query semantics stable enough to compare implementations.

**Verification:** evaluate lexical, vector, and hybrid baselines on representative exact-match and semantic queries. Measure candidate recall, final ranking quality, latency, cost, freshness, and access-control behavior. Replace a pipeline when a simpler or stronger alternative meets the requirements, not because the pipeline is supposedly obsolete by definition.

## CRM storage: files, SQLite, or a filesystem view

**Question:** does designing for better models favor a file-backed CRM?

Not by itself. A capable agent can use SQL, a CLI, or text files. Direct human editing, ordinary search tools, interoperability, and partial encryption are actual workflow requirements; compatibility with one current agent's favorite tools is a weaker justification.

**Durable assets:** contact records, source evidence, stable identities, permissions, relationship history, and issued-document snapshots.

**Replaceable inference:** enrichment, prioritization, suggested classifications, and proposed entity merges. Keep proposals distinguishable from adopted records. Better matching does not authorize a merge or override an opt-out.

**Policy and mechanism:** explicit permission rules, tenant selection, validated updates, concurrency checks, safe recovery, and faithful document history remain useful as models improve. Neither Git history nor an application journal automatically proves authenticated identity or resists tampering. Direct file or SQL writes can bypass application rules.

Compare three credible designs:

| Design | Strength | Complexity and limitation |
|---|---|---|
| Typed files as truth, derived SQLite index | Direct file editing and text-tool access; meaningful source diffs | Cross-file integrity, crash recovery, external edits, and index freshness become application responsibilities |
| SQLite as truth, exports and an edit command | Transactional state and journal updates; central constraints | Exports are derived snapshots; arbitrary edits require explicit validated import, not invisible bidirectional sync |
| SQLite as truth, FUSE file view | Ordinary filesystem access over transactional records | Writable views must translate partial writes, editor temp files, renames, invalid content, and concurrent saves into defined mutations; deployment and mount availability also matter |

SQLite plus FUSE moves complexity into filesystem semantics; a database transaction does not explain when an editor's sequence of writes becomes a complete valid record. Read-only views or ordinary exports are smaller experiments.

**Conditional recommendation:** choose files when direct editing and text-native ownership justify their integrity costs. Choose SQLite when transactional mutation dominates and exports satisfy file access. Explore writable FUSE only after simpler approaches fail a concrete workflow. Accounting and issued-document history still need their own explicit transactional and snapshot guarantees.

**Verification:** exercise a real edit/search/export workflow, stale concurrent updates, crash recovery at promised durability boundaries, invalid input, and restoration from backup. Test index rebuilding for file truth, export/import conflict handling for SQLite truth, and representative editor save sequences for writable FUSE. Passing recovery tests supports correctness; it does not by itself prove that the architecture's complexity is worthwhile.

## Encryption and snippet exports: correctness is not determinism

**Question:** should selective encryption and text-expander integration be deterministic mechanisms?

Formatting an approved set of ordinary fields into snippets can be reproducible. Cryptographic encryption generally requires secure randomness or carefully managed nonces; identical plaintext need not produce identical ciphertext. Do not change the cryptographic construction merely to make diffs stable.

**Durable assets:** original records, encrypted sensitive content, and the metadata required for authorized recovery. Keys need a separate, explicit custody and backup plan.

**Policy:** which fields may leave the CRM, who may decrypt, and whether decrypted content may enter a persistent index. A model recommending a useful snippet does not grant permission to export it.

**Mechanism:** use established encryption tools or libraries, explicit unlock behavior, and allowlisted one-way exports. Keep decrypted sensitive values out of persistent indexes, snippets, logs, and temporary files unless a separately authorized design protects them. Plaintext snippets are copies with their own retention and distribution risks.

**Limits:** encrypted text cannot be searched directly with ordinary grep. Filenames and references may reveal metadata. Encrypting a field now does not erase its previous plaintext from Git history, backups, or earlier exports. Files, SQLite, and FUSE each need an explicit protection design; none supplies selective encryption by virtue of its interface.

**Verification:** test that locked reads disclose no protected values, ordinary search and generated snippets exclude sensitive fields, unauthorized export is rejected, and an authorized recovery works from the intended backup. Inspect persistent artifacts for leaks using synthetic fixtures. No claim of tamper-proof auditing or secure deletion follows from these tests alone.
