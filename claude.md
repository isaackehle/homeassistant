# Home Assistant Blueprints Repository

Public collection of reusable Home Assistant automation and script blueprints.

**Repo**: `https://github.com/isaackehle/homeassistant`

## Project Structure

```
blueprints/
  automation/       # Automation blueprints (domain: automation)
    <name>/
      <name>.yaml   # Blueprint file
      README.md     # Documentation
  script/           # Script blueprints (domain: script)
    <name>/
      <name>.yaml
      README.md
tests/              # pytest suite validating blueprint structure
.github/workflows/  # CI: YAML validation, structure checks, file organization
```

## Blueprint Conventions

- **Filenames**: kebab-case (e.g., `coffee-pot-monitor.yaml`)
- **Directories**: one directory per blueprint, matching the blueprint filename
- **Domain placement**: automation blueprints go in `blueprints/automation/`, scripts in `blueprints/script/`
- Every blueprint YAML must include: `blueprint.name`, `blueprint.domain`, `blueprint.description`, `blueprint.author`, `blueprint.source_url`
- `source_url` must start with `https://github.com/isaackehle/homeassistant/`
- Every blueprint directory must include a `README.md` with features, configuration, and troubleshooting

## Blueprint YAML Syntax (HA 2024.10+)

Use the modern YAML syntax introduced in Home Assistant 2024.10:

| Old (deprecated) | New (current) |
|---|---|
| `trigger:` (top-level) | `triggers:` |
| `- platform: state` | `- trigger: state` |
| `condition:` (top-level) | `conditions:` |
| `action:` (top-level) | `actions:` |
| `service:` (in action steps) | `action:` |

## Blueprint YAML Patterns

- Required inputs first, optional inputs (with `default:`) after
- Use appropriate selectors (`entity`, `number`, `time`, `duration`, `boolean`, `select`, `target`, `action`)
- Use `!input` tags to reference blueprint inputs
- Use trigger IDs when handling multiple triggers with `choose` blocks
- Use `variables:` for template expressions to improve readability
- Prefer `mode: restart` for motion/state-based automations, `mode: single` for notifications
- Use `continue_on_error: true` where appropriate
- Use `input_boolean` helpers for state management to prevent duplicate actions

## Testing

- Framework: **pytest**
- Run tests: `python -m pytest`
- Tests validate YAML structure, metadata, inputs, triggers, actions, and state logic
- Custom YAML loader handles `!input` tags via `yaml.SafeLoader.add_constructor`
- New blueprints should have corresponding test files in `tests/`

## CI Validation (.github/workflows/validate.yml)

The GitHub Actions workflow validates:
1. YAML syntax (using `yaml.BaseLoader` to handle HA-specific tags)
2. Required blueprint fields (`name`, `domain`)
3. `source_url` points to the correct repository (not the old `homeassistant-blueprints` repo)
4. File organization (automation domain files in `automation/`, script domain files in `script/`)

## Template Best Practices

- Always use `| float(0)` or `| int(0)` with defaults
- Check for `unavailable`/`unknown` states before using values
- Prefer `state` triggers over `template` triggers for performance
- Use `for:` in state triggers to debounce
