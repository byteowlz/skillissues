set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# Regenerate README skill list from skills/*/SKILL.md
update-readme:
  ./scripts/update-readme.sh

# Test evidence-report structure/completeness; does not certify a product
agent-readiness-check:
  uv run --no-project --with jsonschema==4.25.1 python -m unittest discover -s skills/agent-readiness/scripts -p 'test_*.py' -v
