"""Tests for the IR code sender blueprint YAML structure."""
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
    path = Path(__file__).parent / "ir_code_sender.yaml"
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


def test_uses_input_trigger_and_single_mode():
    data = _load_blueprint()
    assert data.get("mode") == "single"
    assert data.get("trigger") == "trigger_config"


def test_action_repeats_publish_for_each_ir_code():
    action = _load_blueprint().get("action", [])
    assert isinstance(action, list)
    assert len(action) >= 2

    repeat_block = action[1].get("repeat", {})
    assert "count" in repeat_block
    repeat_sequence = repeat_block.get("sequence", [])
    publish_step = repeat_sequence[0]
    assert publish_step.get("service") == "mqtt.publish"
    publish_data = publish_step.get("data", {})
    assert publish_data.get("topic") == "{{ mqtt_topic }}"
    assert "ir_code_to_send" in publish_data.get("payload", "")

    delay_step = repeat_sequence[1]
    assert "delay" in delay_step
