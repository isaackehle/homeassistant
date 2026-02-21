"""Tests for the lights controller blueprint YAML structure."""
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
    path = Path(__file__).parent / "lights_controller.yaml"
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


def test_trigger_ids_cover_door_motion_timer_and_buttons():
    trigger = _load_blueprint().get("trigger", [])
    trigger_ids = {t.get("id") for t in trigger if isinstance(t, dict)}
    expected_ids = {
        "door_opened",
        "door_closed",
        "motion_detected",
        "motion_timer_ended",
        "top_paddle_single",
        "bottom_paddle_single",
        "top_paddle_double",
        "bottom_paddle_double",
        "bypass_action_single",
        "bypass_action_double",
    }
    assert expected_ids.issubset(trigger_ids)


def test_actions_include_light_and_timer_control_paths():
    action_blob = yaml.dump(_load_blueprint().get("action", []))
    assert "action: light.turn_on" in action_blob
    assert "action: light.turn_off" in action_blob
    assert "action: timer.start" in action_blob
    assert "action: timer.pause" in action_blob
    assert "action: timer.set_duration" in action_blob


def test_uses_single_mode():
    assert _load_blueprint().get("mode") == "single"
