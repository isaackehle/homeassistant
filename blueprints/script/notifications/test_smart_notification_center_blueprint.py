"""Tests for the smart notification center script blueprint YAML structure."""
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
    path = Path(__file__).parent / "smart-notification-center.yaml"
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
    assert blueprint.get("domain") == "script"


def test_blueprint_has_inputs():
    inputs = _load_blueprint().get("blueprint", {}).get("input", {})
    assert isinstance(inputs, dict)
    assert len(inputs) > 0


def test_sequence_has_mobile_tts_and_persistent_paths():
    sequence = _load_blueprint().get("sequence", [])
    choose_count = sum(1 for step in sequence if "choose" in step)
    assert choose_count == 3

    sequence_blob = yaml.dump(sequence)
    assert "service: mobile_service" in sequence_blob
    assert "service: tts_service" in sequence_blob
    assert "service: persistent_notification.create" in sequence_blob


def test_mobile_notification_payload_includes_priority_fields():
    sequence_blob = yaml.dump(_load_blueprint().get("sequence", []))
    assert "priority_level" in sequence_blob
    assert "ttl: 0" in sequence_blob
    assert "importance: priority_level" in sequence_blob


def test_parallel_mode_and_max_concurrency():
    data = _load_blueprint()
    assert data.get("mode") == "parallel"
    assert data.get("max") == 10
