---
name: wiki-workflow
description: Wiki knowledge architecture for shared markdown repos. Use when editing, creating, refactoring, indexing, linking, or summarizing durable wiki knowledge; when deciding whether something belongs in the wiki; or when another skill needs a traceable shared knowledge page.
---

# Wiki Workflow Skill

## Purpose

Turn messy working context into durable, findable, linked wiki knowledge without losing git traceability.

## Standard repository

The shared wiki lives at `~/wiki` unless the user specifies another wiki repository.

## Flow

1. **Pull and inspect.** Run `git pull` in the wiki repo, then check `git status --short`. If the tree is dirty or conflicted, stop and report before editing. Completion: the repo is clean and current, or the user has been told why work stopped.
2. **Triage destination.** Decide whether the content belongs in the wiki. Completion: every requested item has a destination: wiki, repo docs/`AGENTS.md`, `trx`, memory, list/calendar, or scratch.
3. **Search before creating.** Search the wiki for existing pages and related terms with `rg`/`find`. Completion: either an existing target page is chosen, or a new page location is justified by the search result.
4. **Choose the page pattern.** Use one of the patterns below. Completion: the page has the sections needed for its pattern, not a shapeless note dump.
5. **Edit and link.** Make focused edits, preserve local style, add relative links, and update the nearest index/parent page. Completion: every substantial page has an incoming link from an index or parent, and outbound links where useful.
6. **Validate.** Check touched links/paths and review `git diff`. Completion: diff contains only the coherent requested change set.
7. **Commit and push.** Commit and push the coherent change set. Completion: report changed files and commit hash.

## Destination matrix

- Durable shared knowledge -> wiki.
- Repo-specific operating rules -> repo `AGENTS.md` or repo docs.
- Active implementation state -> `trx` issue or repo docs.
- Reusable agent fact/pattern -> `mmry`
- Temporary scratch or raw generated noise -> not wiki.

If content fits multiple destinations, put the durable synthesis in the wiki and link to the operational source of truth.

## Page patterns

### Concept

Use for stable explanations.

```markdown
# <Concept>

## Summary
## Context
## Details
## See also
```

### Decision

Use for architecture, workflow, or tool choices.

```markdown
# Decision: <Title>

## Status
Proposed | Accepted | Superseded

## Context
## Decision
## Consequences
## Alternatives considered
## Links
```

### Runbook

Use for repeatable operations.

```markdown
# Runbook: <Task>

## When to use
## Preconditions
## Steps
## Verification
## Rollback / failure handling
## Links
```

### System or machine profile

Use for infrastructure, services, hosts, agents, and sync topology.

```markdown
# <System or Machine>

## Role
## Access
## Important paths
## Services
## Operations
## Open questions
## Links
```

### Research digest

Use for external research or comparisons.

```markdown
# <Topic> Research

## Question
## Findings
## Sources
## Recommendation
## Open questions
```

## Link and index rules

- Prefer relative markdown links.
- Avoid duplicate pages for the same concept; merge or link instead.
- Every substantial new page needs one incoming link from an index, parent, or related page.
- Add a `See also` section when related pages exist.
- When moving pages, fix inbound and outbound links in the same commit.

## Commit rules

Commit every coherent wiki change set and push after committing.

Recommended format:

```text
wiki: <short action summary>

Context: <reason or task/session context>
```

## Avoid

- Writing to the wiki without pulling first.
- Continuing on a dirty/conflicted wiki tree without user confirmation.
- Creating isolated orphan pages.
- Dumping raw chat logs, temporary scratch, secrets, tokens, private keys, or sensitive raw logs.
- Large unrelated edits in one commit.
