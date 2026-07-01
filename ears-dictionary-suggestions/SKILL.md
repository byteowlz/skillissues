---
name: ears-dictionary-suggestions
description: Analyze eaRS dictation transcript JSONL logs and suggest dictionary replacements. Use when the user asks to review transcription logs, mine dictation history, find speech-to-text mistakes, or propose entries for ears dictionary add.
---

# eaRS Dictionary Suggestions

Mine eaRS transcript history for observed phrases that should map to canonical dictionary replacements.

## Workflow

1. Locate inputs:
   - Transcript logs: `$XDG_STATE_HOME/ears/transcripts/*.jsonl`, falling back to `~/.local/state/ears/transcripts/*.jsonl`.
   - Global dictionary: `$XDG_CONFIG_HOME/ears/dictionaries/global.toml`, falling back to `~/.config/ears/dictionaries/global.toml`.
   - Completion: you know which log files and dictionary file were inspected, or report that none exist.

2. Read recent transcript logs:
   - Prefer the last 1-7 days unless the user asks for a different range.
   - Inspect both `raw` and `replaced` fields.
   - Group adjacent `type = "word"` records into short windows so multi-word errors can be spotted.
   - Completion: you have candidate raw phrases with example contexts and rough counts.

3. Compare against the current dictionary:
   - Do not suggest phrases already covered by an existing entry.
   - Treat phrase matching case-insensitively.
   - Completion: every candidate is either new or explicitly justified as a correction to an existing entry.

4. Suggest conservative entries:
   - Prefer specific multi-word phrases over broad single words.
   - Avoid replacements that would corrupt ordinary prose.
   - Include the exact command to add each suggestion, using flag-based syntax:
     `ears dictionary add --replacement "CANONICAL" --phrase "OBSERVED"`.
   - Completion: each suggestion has canonical output, observed phrase(s), evidence, and risk level.

5. Ask before mutating:
   - Do not run `ears dictionary add` unless the user asks to apply suggestions.
   - If applying, batch phrases under the same canonical replacement where possible.
   - After applying, run `ears dictionary test` on representative examples.
   - Completion: applied entries are verified or failures are reported.

## Output format

Use this compact structure:

```text
Inspected:
- transcripts: <paths/range>
- dictionary: <path>

High-confidence suggestions:
1. <observed> -> <canonical>
   evidence: <count/examples>
   command: ears dictionary add --replacement "..." --phrase "..."
   risk: low|medium|high

Maybe:
...

Skip/covered:
...
```

## Heuristics

Good candidates:

- project names, CLI names, acronyms, crate names, product names
- repeated odd phrases near known technical terms
- mistakes that appear in command-like utterances
- phrase-level errors such as `tricks issue -> trx issue`

Bad candidates:

- common words by themselves (`trick -> trx`) unless the user explicitly wants that
- one-off errors with no clear canonical form
- replacements that depend on context not available to eaRS yet
- entries that would fight existing dictionary mappings
