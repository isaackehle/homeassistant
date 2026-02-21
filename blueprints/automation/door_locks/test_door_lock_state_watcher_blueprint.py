"""Tests for the door lock state watcher blueprint YAML structure."""
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
    path = Path(__file__).parent / "door_lock_state_watcher.yaml"
    with path.open() as handle:
        return yaml.load(handle, Loader=_IgnoreTagLoader)


def test_blueprint_loads_successfully():
    data = _load_blueprint()
    assert data is not None
    assert "blueprint" in data


def test_blueprint_has_required_metadata():
    blueprint = _load_blueprint().get("blueprint", {})
    assert "name" in blueprint
    assert blueprint.get("domain") == "automation"


def test_blueprint_has_inputs():
    inputs = _load_blueprint().get("blueprint", {}).get("input", {})
    assert isinstance(inputs, dict)
    assert len(inputs) > 0


def test_trigger_fires_on_unlock_transition():
    trigger = _load_blueprint().get("trigger", [])
    assert isinstance(trigger, list)
    assert len(trigger) == 1
    assert trigger[0].get("platform") == "state"
    assert trigger[0].get("entity_id") == "lock_entity"
    assert trigger[0].get("from") == "locked"
    assert trigger[0].get("to") == "unlocked"


def test_action_sends_mobile_app_notification():
    action = _load_blueprint().get("action", [])
    assert isinstance(action, list)
    assert len(action) == 1
    notify = action[0]
    assert notify.get("domain") == "mobile_app"
    assert notify.get("type") == "notify"
    assert notify.get("device_id") == "notify_target"
    assert "unlocked" in notify.get("message", "").lower()
