# Home Assistant Blueprints Repository Conventions

This repository contains a public collection of reusable Home Assistant automation and script blueprints.

## Project Structure

- `blueprints/automation/<name>/`: Automation blueprints (domain: automation). Contains `<name>.yaml`, `README.md`, and `test_*_blueprint.py`.
- `blueprints/script/<name>/`: Script blueprints (domain: script). Contains `<name>.yaml` and `README.md`.
- `tests/`: Shared pytest fixtures/helpers and non-blueprint tests.
- `.github/workflows/`: CI workflows for YAML validation, structure checks, and file organization.

## Blueprint Conventions

- **Filenames**: Use kebab-case (e.g., `coffee_pot_monitor.yaml`).
- **Directories**: One directory per blueprint, matching the blueprint filename.
- **Domain placement**: Automation blueprints go in `blueprints/automation/`, scripts in `blueprints/script/`.
- **Required Metadata**: Every blueprint YAML must include: `blueprint.name`, `blueprint.domain`, `blueprint.description`, `blueprint.author`, `blueprint.source_url`.
- **Source URL**: `source_url` must start with `https://github.com/isaackehle/homeassistant/`.
- **Documentation**: Every blueprint directory must include a `README.md` detailing features, configuration, and troubleshooting.

## Blueprint YAML Syntax (HA 2024.10+)

Always use the modern YAML syntax introduced in Home Assistant 2024.10:

- Use `triggers:` instead of `trigger:` at the top level.
- Use `- trigger: state` instead of `- platform: state`.
- Use `conditions:` instead of `condition:` at the top level.
- Use `actions:` instead of `action:` at the top level.
- Use `action:` instead of `service:` in action steps.

## Blueprint YAML Patterns

- Place required inputs first, followed by optional inputs (with `default:`).
- Use appropriate selectors (`entity`, `number`, `time`, `duration`, `boolean`, `select`, `target`, `action`).
- Use `!input` tags to reference blueprint inputs.
- Use trigger IDs when handling multiple triggers with `choose` blocks.
- Use `variables:` for template expressions to improve readability.
- Prefer `mode: restart` for motion/state-based automations, and `mode: single` for notifications.
- Use `continue_on_error: true` where appropriate.
- Use `input_boolean` helpers for state management to prevent duplicate actions.

## Template Best Practices

- Always use `| float(0)` or `| int(0)` with defaults.
- Check for `unavailable`/`unknown` states before using values.
- Prefer `state` triggers over `template` triggers for performance.
- Use `for:` in state triggers to debounce.

## Testing

- **Framework**: pytest
- **Run tests**: `python -m pytest` or `pytest -q tests blueprints`
- Tests validate YAML structure, metadata, inputs, triggers, actions, and state logic.
- A custom YAML loader handles `!input` tags via `yaml.SafeLoader.add_constructor`.
- New blueprints should have corresponding colocated tests in the same blueprint directory (e.g., `test_<name>_blueprint.py`).
- When renaming or moving blueprints, ensure the colocated test loader path is updated.

## Sync Safety

When this repo is synced into live HA config, test files must be excluded. Ensure any watcher/sync tooling ignores `blueprints/**/test_*.py`.
