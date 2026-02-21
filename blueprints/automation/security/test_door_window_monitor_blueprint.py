"""Tests for the door window monitor blueprint YAML structure."""
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
    path = Path(__file__).parent / "door-window-monitor.yaml"
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


def test_trigger_opens_from_off_to_on():
    trigger = _load_blueprint().get("trigger", [])
    assert isinstance(trigger, list)
    assert trigger[0].get("platform") == "state"
    assert trigger[0].get("from") == "off"
    assert trigger[0].get("to") == "on"
    assert trigger[0].get("entity_id") == "door_window_entity"


def test_action_sends_initial_and_optional_reminder_notifications():
    action = _load_blueprint().get("action", [])
    assert isinstance(action, list)
    assert len(action) == 5

    first_notify = action[0]
    assert first_notify.get("service") == "notify_service"
    assert first_notify.get("data", {}).get("title") == "notification_title"
    assert first_notify.get("data", {}).get("message") == "notification_message"

    reminder_enabled_condition = action[1]
    assert reminder_enabled_condition.get("condition") == "template"
    assert "reminder_enabled" in reminder_enabled_condition.get("value_template", "")

    delay_step = action[2]
    assert delay_step.get("delay") == "reminder_delay"

    still_open_condition = action[3]
    assert still_open_condition.get("condition") == "state"
    assert still_open_condition.get("entity_id") == "door_window_entity"
    assert still_open_condition.get("state") == "on"

    reminder_notify = action[4]
    assert reminder_notify.get("service") == "notify_service"
    assert reminder_notify.get("data", {}).get("message") == "reminder_message"
