"""Tests for the fireplace controller blueprint YAML structure."""
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
    path = Path(__file__).parent / "fireplace_controller.yaml"
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


def test_trigger_checks_time_pattern_and_mode_changes():
    trigger = _load_blueprint().get("trigger", [])
    assert isinstance(trigger, list)
    assert len(trigger) >= 2
    assert any(t.get("trigger") == "time_pattern" for t in trigger)
    assert any(t.get("trigger") == "state" for t in trigger)


def test_action_choose_controls_blower_switch():
    action = _load_blueprint().get("action", [])
    assert isinstance(action, list)
    choose_block = action[0].get("choose", [])
    action_blob = yaml.dump(choose_block)
    assert "service: switch.turn_on" in action_blob
    assert "service: switch.turn_off" in action_blob
    assert "should_turn_on" in action_blob
    assert "should_turn_off" in action_blob
