"""Tests for the door lock with multiple inputs blueprint YAML structure."""
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
    path = Path(__file__).parent / "door_lock_with_multiple_inputs.yaml"
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


def test_has_expected_trigger_ids_for_core_paths():
    triggers = _load_blueprint().get("triggers", [])
    trigger_ids = {t.get("id") for t in triggers if isinstance(t, dict)}
    expected = {
        "door_closed_off",
        "door_closed_on",
        "away",
        "override_changed",
        "run_now_trigger",
    }
    assert expected.issubset(trigger_ids)


def test_uses_restart_mode_with_silent_max_exceeded():
    data = _load_blueprint()
    assert data.get("mode") == "restart"
    assert data.get("max_exceeded") == "silent"


def test_actions_include_lock_calls_and_wait_for_trigger():
    data = _load_blueprint()
    actions_blob = yaml.dump(data.get("actions", []))
    assert actions_blob.count("action: lock.lock") >= 3
    assert "wait_for_trigger" in actions_blob
    assert "id: override_changed" in actions_blob
