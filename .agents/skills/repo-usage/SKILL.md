---
name: repo-usage
description: Repository onboarding and conventions for Home Assistant blueprints in this repo.
---

# Repo Usage Skill

Use this skill when an AI tool needs to understand repository layout, blueprint conventions, and test workflow.

## Purpose

This repository publishes reusable Home Assistant blueprints and validation tests.

## Key Directories

- `blueprints/automation/`: Automation blueprints (one directory per blueprint).
- `blueprints/script/`: Script blueprints.
- `tests/`: Shared pytest helpers and non-blueprint tests.
- `blueprints/**/test_*_blueprint.py`: Colocated blueprint tests.
- `.github/workflows/validate.yml`: CI YAML + blueprint structure validation.

## Blueprint Layout

1. `blueprints/<domain>/<blueprint_name>/<blueprint_file>.yaml`
2. `blueprints/<domain>/<blueprint_name>/README.md`
3. `blueprints/<domain>/<blueprint_name>/test_*_blueprint.py`

## Authoring Rules

1. Use modern HA syntax:
   - top-level `triggers`, `conditions`, `actions`
   - trigger entries use `trigger:` (not `platform:`)
   - action entries prefer `action:`
2. Include metadata:
   - `blueprint.name`
   - `blueprint.description`
   - `blueprint.domain`
   - `blueprint.source_url`
3. Keep tests next to the blueprint they validate.
4. If a blueprint path changes, update the colocated test loader path.

## Test Workflow

```bash
pytest -q tests blueprints
pytest -q blueprints/automation/<name>/test_*_blueprint.py
```

Local loader pattern inside blueprint tests:

```python
path = Path(__file__).parent / "<blueprint_file>.yaml"
```

## Sync Safety

When this repo is synced into live HA config, test files must be excluded:

- ignore `blueprints/**/test_*.py` in sync rules
- verify watcher/sync tooling skips Python tests

## Change Checklist

1. Update YAML and README together.
2. Update or add colocated tests.
3. Run `pytest -q tests blueprints`.
4. Confirm no stale old paths in tests after renames.
