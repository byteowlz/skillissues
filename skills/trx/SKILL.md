---
name: trx
description: Use trx, the git-backed issue tracker, to manage issues, epics and dependencies, configure repo-local or named central stores, onboard shared-store users, migrate ledgers, and sync across machines.
---

# trx

## Core rules

- Use the installed `trx` directly, not `cargo run`.
- Run issue commands inside the intended checkout. Inspect `trx doctor`, `trx central status`, and `trx store sync status` before changing storage or remotes.
- Preserve existing issues and unrelated git changes. Never delete ledgers to resolve initialization or migration errors.
- Check `trx <command> --help` when flags differ across installed versions. `install.sh` installs the latest **published release**, not the latest `master` commit.

## Issue workflow

```bash
trx ready
trx list
trx list --type epic
trx list --epic <epic-id>          # epic + descendants
trx list --epic <epic-id> --all    # include closed; not cross-repo scope
trx show <id>
trx create "Title" -t task -p 2
trx create "Child task" --parent <epic-id>
trx dep tree <id>
trx update <id> --status in_progress
trx close <id> -r "Done"
```

Include actionable instructions and evidence-checkable acceptance criteria in issue descriptions. Close only after verifying the outcome. Priorities: 0 critical, 1 high, 2 medium, 3 low, 4 backlog.

## Choose the storage mode explicitly

**Repo-local (default):** `trx init` creates `.trx/` ledgers in the code repository. Use `trx sync` for repo-local synchronization.

**Central:** issues live outside the checkout in a per-user git store. `.trx/central` is a routing marker, not the issue ledger. Use `trx central init` to bind a checkout and `trx store sync` for central-store synchronization.

Central ledgers are partitioned by repository identity (`git:<root-commit>` for git repositories): clones/worktrees share a ledger; different repositories keep separate issue lists in the same store. Do not assume matching directory names establish shared identity.

Global configuration is at `$XDG_CONFIG_HOME/trx/config.toml` (normally `~/.config/trx/config.toml`). Example:

```toml
# Root-level keys MUST precede all [table] headers.
migrate = "auto"
default_mode = "central" # optional: auto-central for checkouts without .trx
store_root = "~/.local/share/trx"

[stores.team]
root = "~/.local/share/trx-team"
```

Repo-local remains the default unless explicitly configured otherwise. `default_mode` is a root-level setting, NOT a field inside `[stores.team]`. Named stores have independent roots and git remotes.

Store selection: explicit `--store NAME` / `--store-root PATH`, then `TRX_STORE` / `TRX_STORE_ROOT`, then checkout marker, then config default. `--config PATH` / `TRX_CONFIG` selects a configuration file; explicit files must exist. A global default does not bind a project to a particular named team store: bind it explicitly.

## Shared-store onboarding

Use this sequence for colleagues joining an existing team store; replace the name and URL as appropriate:

```bash
# Once per machine: connect the named store to its remote.
trx store sync init --store team --remote git@github.com:ORG/trx-issue-tracker.git

# In EACH participating code checkout:
cd /path/to/project
trx central init --store team
trx doctor
trx store sync
trx list
```

For Optimaite, use `--store optimaite` and remote `git@github.com:Optimaite/trx-issue-tracker.git`; run the checkout steps inside the Optimaite v2 clone and each other participating repository. Require appropriate remote access. Do not onboard unrelated personal repositories into the team store.

Verify that doctor reports the **named store's root** (e.g. `~/.local/share/trx-optimaite/repos/...`), not the personal default root. `store sync init` configures the store; it does not by itself bind the current checkout.

Use `central init --store` for compatibility with 0.8.1. The later `init --store` fix exists on master but is not part of the original 0.8.1 release; older binaries silently ignore store flags on plain `init`.

If local issues exist, central initialization refuses to shadow them. Inspect and migrate instead:

```bash
trx migrate --store team --dry-run
trx migrate --store team
trx doctor
trx store sync
```

Migration merges and verifies data before moving originals to timestamped backups and writing a central marker. On conflicts or unparsable snapshots, stop, inspect the reported records, and preserve originals; do not invent a winning version or discard verification evidence. Rebinding to another store does NOT migrate issues already stored in the previous central store.

## Personal machine bootstrap / bulk migration

Use only with explicit approval of remote, scan roots and exclusions:

```bash
trx onboard --remote ssh://HOST/USER/trx-store.git \
  --scan ~/byteowlz --scan ~/work --exclude /path/to/team-repo --yes
```

This connects the default central store, sets automatic migration policy, and scans/migrates repo-local ledgers. Add `--default-central` only when requested for new checkouts. Do not substitute this bulk personal workflow for the per-checkout named-team workflow above.

Preview bulk migration before applying it:

```bash
trx migrate --all --scan /path/to/repos --exclude /path/to/team-repo --dry-run
```

`--scan` and `--exclude` are repeatable. `--untrack` removes migrated ledgers from the code repository's index and leaves those changes uncommitted: review them before committing. Report partial failures explicitly rather than claiming all repositories migrated.

## Sync and diagnosis

```bash
trx central status
trx doctor
trx store sync status
trx store sync             # central-store commit/pull/push
trx store sync pull
trx store sync push
```

Central-mode CLI commands auto-pull (throttled) and attempt sync on exit; offline work can leave pending commits. Verify the intended remote and pending count rather than treating a local write as proof of remote delivery. Metadata conflicts require investigation, not forced pushes.

Encrypted SSH keys may prompt repeatedly because auto-sync makes multiple SSH connections. Do not ask for passphrases, persist decrypted keys, or promise trx caches credentials. Configure the user's SSH agent/Keychain with their consent, or investigate reducing redundant connections separately.
