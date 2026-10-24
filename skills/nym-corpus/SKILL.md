---
name: nym-corpus
description: Prepare agent sessions or document corpora for training or publication with nym - discover recurring sensitive terms, build reviewed redaction profiles, gate sources with deny rules, transform with a private ledger and hand a hash-bound manifest to a consumer such as Kompressor. Use when asked to anonymize, scrub, sanitize or publish many sessions, logs or documents, to build a dictionary of terms to redact, or to prepare a training corpus.
---

# Prepare a corpus with nym

nym transforms and accounts. It never certifies anonymity, decides rights or
publishes. Every stage below either proposes or verifies; a human approves.

Check the installed binary first: `nym --version`, `nym terms dict --help`,
`nym corpus --help`. Use `--json` for machine output everywhere.

## Ground rules

- Work on a copy of the sources. Plans, ledgers, discovery and review files contain
  original values: keep them outside the source tree and outside git, never upload them.
- Never auto-approve. A model, a dictionary or a missing finding is never evidence
  that something is safe. Excluded or unreviewed terms are unmeasured, not benign.
- Nothing downloads implicitly. Dictionaries come from `nym terms dict pull`, models
  from the configured cache. Ask before any network action.
- Report aggregates (counts, classes, rates), not values, unless the user asks to see them.

## 1. Discover recurring terms

```bash
nym terms dict pull en de            # once; pinned, hash-verified, CC-BY-SA lists
nym terms discover SESSIONS --recursive --bounded \
  --dict system,en,de --exclude-shapes \
  [--exclude-words glossary.txt] [--demote-words registry.txt] \
  --ner-rank --limit 2000 --output PRIVATE/discovery.json
```

- `--dict` and `--exclude-words` remove known words before ranking; matching is
  case-aware so names that are also words survive.
- `--demote-words` is for large public registries (package or domain names): rank
  last, never exclude - they contain people's names.
- `--ner-rank` puts model-recognised entities first. Add `--specific` to prefer
  terms concentrated in few sources over ones spread across everything.

## 2. Review terms into a profile

```bash
nym terms review PRIVATE/discovery.json --html --output PRIVATE/review.html
# user decides sensitive / contextual / dismiss / unsure in the browser
nym terms export PRIVATE/discovery.json --review PRIVATE/review.json --output PRIVATE/terms.txt
nym profiles import default --list sensitive PRIVATE/terms.txt
```

Approved terms are applied deterministically by `anon`, `detect` and `traces anon`.
Product names that models mistake for people (Claude Opus, GPT-4) are suppressed by
nym's built-in list; add your own harmless terms with
`nym profiles add default --list allow TERM...`.

## 3. Detect and review values

```bash
nym traces anon WORKING --plan PRIVATE/values.json [--redaction-profile NAME]
```

The values file lists, per session, every value nym would replace (class, count,
context). This is the review queue: a human marks false positives to keep, and
should also check a sample of retained text for misses. Removing a value from the
file keeps it; everything left in the file is replaced.

## 4. Propose, approve, account and gate

```bash
nym corpus inventory WORKING -o PRIVATE/plan.json --scope session --deny-file deny.txt
nym corpus propose PRIVATE/plan.json --source WORKING --values PRIVATE/approved-values.json \
  -o PRIVATE/proposed.json --rename-files --export-profile pi-training-v1
nym corpus approve PRIVATE/proposed.json -o PRIVATE/approved.json \
  --receipt "values reviewed by <who> on <date>" --all-classes --unflagged --renames \
  --fields --drops
nym corpus review PRIVATE/approved.json -o PRIVATE/reviewed.json --basis owned \
  --evidence "<rights statement>" --privacy-review "<who, how, when>" --serialization-reviewed
nym corpus apply PRIVATE/reviewed.json --source WORKING -o CANDIDATE --ledger PRIVATE/ledger.json
nym corpus verify --ledger PRIVATE/ledger.json --source WORKING --bundle CANDIDATE
nym corpus report --ledger PRIVATE/ledger.json --json > PRIVATE/report.json
```

- `propose` turns every occurrence of a reviewed value into a numbered placeholder
  (`<EMAIL_1>`) and proposes retention elsewhere. Values apply across all sessions
  by default (`--values-scope corpus`): a name caught in one session is usually
  present, undetected, in others. Sources missing from the values file stay
  unresolved and block.
- `--export-profile pi-training-v1` removes provider signatures
  (`thinkingSignature`, `textSignature` on content blocks), which nobody downstream
  can read or review, and replaces entry and provider ids with linked tokens. Rules
  are record-relative paths (`--drop-path`, `--replace-path`), never key names
  anywhere: ids inside tool arguments are data. Readable thinking, tool data and
  media are kept; `--strip-media` is opt-in and needs the consumer's agreement.
- Proposals are not approvals. `approve` needs an explicit receipt and selection
  (`--class`, `--all-classes`, `--unflagged`, `--renames`, `--media`); its summary
  lists what is still pending. Only approve `--unflagged` after the retained-text
  sample was reviewed, and `--media` only after someone looked at the images.
- `deny.txt` holds regexes for projects, clients or topics that must never ship. A
  match disqualifies the whole source; it is never redacted into acceptability.
- A blocked run explains itself in `error.reason` (`--json`) or on stderr with `-v`.
- Every step writes a new plan and never overwrites; keep the sequence as the audit trail.

## 5. Hand off

Give the consumer `CANDIDATE/` with its `manifest.json` (transformed-source paths,
SHA-256 and sizes only) and `corpus report` output (value-free per-source and
per-rule counts, receipts, provenance, manifest digest). Rescan the bundle with the
consumer's own detector and report residual hits with their review status; never
claim detector-clean or silently redact against a review decision. Teacher labels must bind those transformed hashes, never
hashes of the private originals. Rights, segmentation and training gates belong to
the consumer; publishing is a separate, explicitly authorised action.

## Known limits

- Recall is gated on planted canaries; natural-PII recall and precision on a new
  corpus are unmeasured until someone reviews a sample. Run a small pilot first.
- Reviewed values match on word boundaries. Detector hits inside longer
  alphanumeric runs (digit runs inside IDs, subword entities) are not replaced by
  `propose`; review those classes rather than assuming they are covered.
- Embedded images are retained unless replaced explicitly; nym cannot inspect them.
- Discovery ranking cannot be validated with canaries that occur in few sessions:
  identities recurring across many sessions only show up in a real review.
