"""Tests for the helper button click actions blueprint YAML structure."""
from pathlib import Path
from typing import Any

import yaml


class _IgnoreTagLoader(yaml.SafeLoader):
    """YAML loader that ignores unknown tags like !input."""


def _construct_undefined(loader: yaml.Loader, _suffix: str, node: yaml.Node) -> Any:
    """Construct undefined tags by returning their content or None."""
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


_IgnoreTagLoader.add_multi_constructor("", _construct_undefined)


def _load_blueprint():
    path = Path(__file__).parent / "helper_button_click_actions.yaml"
    with path.open() as handle:
        return yaml.load(handle, Loader=_IgnoreTagLoader)


def test_blueprint_loads_successfully():
    data = _load_blueprint()
    assert data is not None
    assert "blueprint" in data


def test_blueprint_has_required_metadata():
    blueprint = _load_blueprint().get("blueprint", {})
    assert "name" in blueprint
    assert "description" in blueprint
    assert blueprint.get("domain") == "automation"


def test_blueprint_has_inputs():
    inputs = _load_blueprint().get("blueprint", {}).get("input", {})
    assert isinstance(inputs, dict)
    assert len(inputs) > 0


def test_uses_modern_plural_sections():
    data = _load_blueprint()
    assert "triggers" in data
    assert "actions" in data
    assert "trigger" not in data
    assert "action" not in data


def test_logs_clicks_and_waits_for_second_click():
    actions = _load_blueprint().get("actions", [])
    assert len(actions) >= 2

    log_action = actions[0]
    assert log_action.get("service") == "system_log.write"

    click_detection = actions[1]
    assert "wait_for_trigger" in click_detection
    assert click_detection.get("continue_on_timeout") is True
    assert click_detection.get("timeout", {}).get("seconds") == 1


def test_emits_single_and_double_click_events():
    actions = _load_blueprint().get("actions", [])
    click_detection = actions[1]

    then_event = click_detection.get("then", [])[0]
    else_event = click_detection.get("else", [])[0]

    assert then_event.get("event") == "system_action"
    assert then_event.get("event_data", {}).get("action") == "KeyPressed2x"
    assert else_event.get("event") == "system_action"
    assert else_event.get("event_data", {}).get("action") == "KeyPressed"
