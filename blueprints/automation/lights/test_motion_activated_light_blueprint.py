"""Tests for the motion activated light blueprint YAML structure."""
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
    path = Path(__file__).parent / "motion_activated_light.yaml"
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


def test_trigger_fires_on_motion_on_transition():
    trigger = _load_blueprint().get("trigger", [])
    assert isinstance(trigger, list)
    assert len(trigger) == 1
    assert trigger[0].get("platform") == "state"
    assert trigger[0].get("from") == "off"
    assert trigger[0].get("to") == "on"
    assert trigger[0].get("entity_id") == "motion_entity"


def test_condition_checks_illuminance_when_configured():
    condition = _load_blueprint().get("condition", [])
    assert len(condition) == 1
    template = condition[0].get("value_template", "")
    assert "illuminance_sensor" in template
    assert "illuminance_threshold" in template


def test_action_flow_turns_on_waits_and_turns_off():
    action = _load_blueprint().get("action", [])
    assert action[0].get("service") == "light.turn_on"
    assert "wait_for_trigger" in action[1]
    wait = action[1].get("wait_for_trigger", {})
    assert wait.get("from") == "on"
    assert wait.get("to") == "off"
    assert action[3].get("service") == "light.turn_off"
