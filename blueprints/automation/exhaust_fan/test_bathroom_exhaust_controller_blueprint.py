from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

BLUEPRINT_PATH = Path(__file__).parent / "bathroom_exhaust_controller.yaml"


class HABlueprintLoader(yaml.SafeLoader):
    """YAML loader with Home Assistant tag support."""


def _ha_input_constructor(loader: HABlueprintLoader, node: yaml.Node) -> Any:
    if isinstance(node, yaml.ScalarNode):
        return {"__input__": loader.construct_scalar(node)}
    if isinstance(node, yaml.SequenceNode):
        return {"__input__": loader.construct_sequence(node)}
    return {"__input__": loader.construct_mapping(node)}


HABlueprintLoader.add_constructor("!input", _ha_input_constructor)


def _load_blueprint() -> dict[str, Any]:
    with BLUEPRINT_PATH.open("r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=HABlueprintLoader)
    assert isinstance(data, dict)
    return data


def _walk(node: Any):
    if isinstance(node, dict):
        for k, v in node.items():
            yield k, v
            yield from _walk(v)
    elif isinstance(node, list):
        for item in node:
            yield from _walk(item)


def test_blueprint_file_exists() -> None:
    assert BLUEPRINT_PATH.exists(), f"Missing blueprint file: {BLUEPRINT_PATH}"


def test_required_metadata() -> None:
    data = _load_blueprint()
    bp = data.get("blueprint", {})
    assert isinstance(bp, dict)

    for field in ("name", "domain", "description", "author", "source_url"):
        assert bp.get(field), f"Missing blueprint.{field}"

    assert bp["domain"] == "automation"
    assert bp["source_url"].startswith("https://github.com/isaackehle/homeassistant/")


def test_modern_top_level_keys() -> None:
    data = _load_blueprint()
    assert isinstance(data.get("triggers"), list)
    assert isinstance(data.get("conditions"), list)
    assert isinstance(data.get("actions"), list)
    assert "trigger" not in data
    assert "condition" not in data
    assert "action" not in data


def test_trigger_entries_use_trigger_key() -> None:
    data = _load_blueprint()
    for trig in data["triggers"]:
        assert "trigger" in trig
        assert "platform" not in trig


def test_required_inputs_present() -> None:
    data = _load_blueprint()
    inputs = data["blueprint"].get("input", {})
    required = {
        "humidity_sensor",
        "exhaust_fan",
        "manual_run_helper",
        "steam_shower_bypass",
        "steam_shower_timer",
    }
    missing = required - set(inputs.keys())
    assert not missing, f"Missing required inputs: {sorted(missing)}"


def test_no_deprecated_service_key_in_actions() -> None:
    data = _load_blueprint()
    bad = [k for k, _ in _walk(data.get("actions", [])) if k == "service"]
    assert not bad, "Use 'action:' instead of deprecated 'service:' in action steps"