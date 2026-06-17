#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

start='<!-- SKILLS:START -->'
end='<!-- SKILLS:END -->'

if [[ ! -f README.md ]]; then
  cat > README.md <<'EOF'
# skillissues

Tiny repo of reusable skills for coding agents (inspired by [agentskills.io](https://agentskills.io/home)).

## Skills

<!-- SKILLS:START -->
<!-- SKILLS:END -->
EOF
fi

if ! grep -qF "$start" README.md || ! grep -qF "$end" README.md; then
  {
    printf '\n## Skills\n\n'
    printf '%s\n' "$start"
    printf '%s\n' "$end"
  } >> README.md
fi

skill_lines="$(
  while IFS= read -r path; do
    name="$path"
    name="${name#skills/}"
    name="${name%/SKILL.md}"
    description="$(awk -F': ' '/^description: / { print $2; exit }' "$path")"
    description="$(printf '%s' "$description" | sed -E 's/^([^.!?]*[.!?]).*$/\1/')"
    printf -- '- [`%s`](%s) - %s\n' "$name" "$path" "$description"
  done < <(find skills -name SKILL.md -type f | sort)
)"

tmp="$(mktemp)"
awk -v start="$start" -v end="$end" -v skills="$skill_lines" '
  $0 == start {
    print
    if (skills != "") print skills
    in_section = 1
    next
  }
  $0 == end {
    in_section = 0
    print
    next
  }
  !in_section { print }
' README.md > "$tmp"

mv "$tmp" README.md

echo "Updated skills section in README.md"
