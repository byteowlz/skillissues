# Worked examples

Concrete cases run through the framework in `SKILL.md`. Each one applies the litmus test, locates the **judgment/mechanism line**, and names which rules it turns on. Read these to calibrate the principles against real design decisions; add new ones in the same shape.

---

## Semantic search

**The setup.** Should your tool bake in semantic search (embeddings + vector similarity) to find relevant items in a corpus?

**It sits on both sides of the bitter lesson at once — disentangle them.**

**As a technique, semantic search *is* the lesson winning.** Learned embeddings beat hand-engineered information retrieval — the tf-idf weighting, the stemming rules, the hand-tuned BM25 features, the ontologies. A general method that scales with data and compute ate decades of retrieval craft. So "embeddings vs hand-built features" is settled the usual way: embeddings.

**But baking a specific semantic-search implementation into your core is exactly the scaffolding to avoid.** Run the litmus test:

- *Judgment test (rule 1):* relevance ranking is a judgment — "which of these best answers this query" — and that is precisely what a model does, better each year.
- *10× test:* an embedding index is **frozen judgment**. The vectors encode the similarity worldview of the one model that produced them. Two items an older model embeds as neighbors, a newer one may sharply distinguish. The index doesn't ride the capability curve — it's a fossil of a particular model's understanding, calcified into your durable layer. (Fails rule 2: the durable asset must survive model turnover.)

**The resolution is the recall/ranking split — the key distinction.** Embeddings are legitimate and lesson-consistent as a *recall* step: cheaply narrow 10M items to ~1000 candidates, because you genuinely cannot put the whole corpus in context. That's mechanism — fast, scalable candidate generation. The anti-pattern is letting the frozen cosine-similarity score be the *final relevance verdict*.

> **Recall is mechanism; ranking is judgment.** Use embeddings to get candidates; let the operating model decide what actually matters among them, with its current understanding. The moment the similarity score *is* the answer, you've shipped a frozen relevance opinion.

**The index is a disposable, rebuildable cache — never the source of truth.** The plain text is durable; the embeddings are a derived artifact you recompute when a better model arrives (rule 2 + rule 10, the build/artifact boundary). Design so re-embedding the whole corpus is cheap and routine, and never couple your *formats* to a specific embedding model. If your data can't be read without one model's vectors, the cache has colonized the core (rule 8).

**The scaffolding the lesson is actively eroding: the RAG pipeline around it.** The chunking strategies, the rerankers, the hand-tuned hybrid-search weights, the query-expansion heuristics — a pile of hand-engineered retrieval judgment, steadily obsoleted by longer context and models that drive their own search (agentic retrieval: the model issues a query, reads results, decides, queries again). Keep the retrieval layer thin and dumb and let the model iterate, rather than encoding a pipeline of retrieval taste a stronger model will route around.

**Design stance (bitter-lesson-proof):**

- Expose the corpus cleanly — plain text, good structure (rule 6, rule 9).
- Provide **deterministic** retrieval primitives in the core: exact, fuzzy, structured filters, full-text. Reproducible, no frozen model (rule 3).
- Offer embeddings as a **swappable recall cache** only when scale demands it — a derived, rebuildable artifact, not a durable asset (rules 2, 10).
- Let semantic **judgment** live with whatever model is operating, never baked in (rules 1, 5).

**The tell:** if you can't swap the embedding model — or drop the index entirely and fall back to "dump the corpus, let the agent read it" — without losing *data* (only convenience), you've kept it on the right side of the line. If dropping it loses *capability*, the scaffolding became load-bearing.

**Maps to rules:** 1 (judgment vs mechanism) · 2 (durable = data + contract) · 3 (determinism; reserve generation for judgment) · 5 (no embedded intelligence) · 6 (extension as data) · 8 (no colonization) · 10 (build/artifact boundary).
