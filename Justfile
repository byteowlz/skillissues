set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# Regenerate README skill list from skills/*/SKILL.md
update-readme:
  ./scripts/update-readme.sh
