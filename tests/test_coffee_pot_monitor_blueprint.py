"""Tests for the coffee pot monitor blueprint YAML structure."""
from pathlib import Path

import yaml


class _IgnoreTagLoader(yaml.SafeLoader):
    """YAML loader that ignores unknown tags like !input."""


def _construct_undefined(loader, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    if isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    if isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    return None


# Ignore any unknown tag like !input by registering a fallback handler.
_IgnoreTagLoader.add_constructor(None, _construct_undefined)


def _load_blueprint():
    path = (
        Path(__file__).parent.parent
        / "blueprints"
        / "automation"
        / "coffee-pot-monitor"
        / "coffee-pot-monitor.yaml"
    )
    with path.open() as handle:
        return yaml.load(handle, Loader=_IgnoreTagLoader)


def _find_choose_by_trigger_id(choose, trigger_id):
    for branch in choose:
        conditions = branch.get("conditions", [])
        for condition in conditions:
            if (
                condition.get("condition") == "trigger"
                and condition.get("id") == trigger_id
            ):
                return branch
    return None


def _index_of_step(sequence, key):
    for idx, step in enumerate(sequence):
        if key in step:
            return idx
    return -1


def _has_notify_guard(sequence):
    guard_idx = -1
    notify_idx = -1
    for idx, step in enumerate(sequence):
        if step.get("condition") == "template":
            template = step.get("value_template", "")
            if "trigger.from_state" in template and "unknown" in template:
                guard_idx = idx
        notify_value = None
        if "action" in step:
            notify_value = step.get("action")
        elif "service" in step:
            notify_value = step.get("service")

        if notify_value is not None:
            notify_str = str(notify_value)
            if notify_str.startswith("notify.") or notify_str == "notify_service":
                notify_idx = idx
    return guard_idx != -1 and notify_idx != -1 and guard_idx < notify_idx


def test_triggers_have_expected_ids():
    data = _load_blueprint()
    triggers = data.get("trigger", [])
    trigger_ids = {item.get("id") for item in triggers}
    assert {
        "brewing_started",
        "brewing_in_progress",
        "brewing_finished",
        "auto_off",
    }.issubset(trigger_ids)


def test_auto_off_waits_for_finish_before_turning_off():
    data = _load_blueprint()
    choose = data.get("action", [])[0].get("choose", [])
    auto_off_branch = _find_choose_by_trigger_id(choose, "auto_off")
    assert auto_off_branch is not None

    sequence = auto_off_branch.get("sequence", [])
    wait_idx = _index_of_step(sequence, "wait_for_trigger")
    turn_off_idx = _index_of_step(sequence, "service")
    assert wait_idx != -1
    assert turn_off_idx != -1
    assert wait_idx < turn_off_idx

    wait_step = sequence[wait_idx]
    assert wait_step.get("timeout") == "00:30:00"
    assert wait_step.get("continue_on_timeout") is False


def test_finished_and_auto_off_have_notify_guard():
    data = _load_blueprint()
    choose = data.get("action", [])[0].get("choose", [])

    finished_branch = _find_choose_by_trigger_id(choose, "brewing_finished")
    assert finished_branch is not None
    assert _has_notify_guard(finished_branch.get("sequence", []))

    auto_off_branch = _find_choose_by_trigger_id(choose, "auto_off")
    assert auto_off_branch is not None
    assert _has_notify_guard(auto_off_branch.get("sequence", []))
