"""Tests for the scheduled lock controller blueprint YAML structure."""
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


# Ignore any unknown tag like !input by registering a fallback handler.
_IgnoreTagLoader.add_multi_constructor("", _construct_undefined)


def _load_blueprint():
    path = Path(__file__).parent / "scheduled_lock_controller.yaml"
    with path.open() as handle:
        return yaml.load(handle, Loader=_IgnoreTagLoader)


def test_blueprint_loads_successfully():
    """Test that the blueprint YAML loads without errors."""
    data = _load_blueprint()
    assert data is not None
    assert "blueprint" in data


def test_blueprint_has_required_metadata():
    """Test that blueprint metadata contains all required fields."""
    data = _load_blueprint()
    blueprint = data.get("blueprint", {})

    assert "name" in blueprint
    assert "description" in blueprint
    assert "domain" in blueprint

    assert blueprint["domain"] == "automation"
    assert blueprint["name"] == "Scheduled Lock Controller"


def test_blueprint_has_required_inputs():
    """Test that all required inputs are defined."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    required_inputs = [
        "lock_time",
        "locks",
        "lock_retry_delay",
        "lock_retries",
    ]

    for input_name in required_inputs:
        assert input_name in inputs, f"Missing required input: {input_name}"


def test_blueprint_has_optional_inputs():
    """Test that optional inputs are defined with defaults."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    # Check optional inputs exist
    assert "notify_service" in inputs
    assert "notify_on_failure_only" in inputs


def test_lock_time_input_config():
    """Test that lock_time input is configured correctly."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    lock_time_input = inputs.get("lock_time", {})
    assert lock_time_input.get("name") == "Time to Lock"
    assert "selector" in lock_time_input
    assert "time" in lock_time_input["selector"]
    assert lock_time_input.get("default") == "22:30:00"


def test_locks_input_config():
    """Test that locks input is configured correctly."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    locks_input = inputs.get("locks", {})
    assert locks_input.get("name") == "Locks to Control"
    assert "selector" in locks_input
    assert "entity" in locks_input["selector"]

    # Check entity selector has domain filter for locks
    selector = locks_input["selector"]["entity"]
    assert selector.get("multiple") is True
    assert "filter" in selector


def test_lock_retry_delay_input_config():
    """Test that lock_retry_delay input is configured correctly."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    retry_delay_input = inputs.get("lock_retry_delay", {})
    assert retry_delay_input.get("name") == "Retry Delay"
    assert "selector" in retry_delay_input
    assert "duration" in retry_delay_input["selector"]
    assert retry_delay_input.get("default", {}).get("seconds") == 30


def test_lock_retries_input_config():
    """Test that lock_retries input is a slider."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    retries_input = inputs.get("lock_retries", {})
    assert retries_input.get("name") == "Number of Retries"
    assert "selector" in retries_input
    assert "number" in retries_input["selector"]

    # Check slider configuration
    number_selector = retries_input["selector"]["number"]
    assert number_selector.get("min") == 1
    assert number_selector.get("max") == 5
    assert number_selector.get("step") == 1
    assert number_selector.get("mode") == "slider"
    assert retries_input.get("default") == 2


def test_notify_service_input_config():
    """Test that notify_service input is configured correctly."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    notify_input = inputs.get("notify_service", {})
    assert notify_input.get("name") == "Notification Service (Optional)"
    assert "selector" in notify_input
    assert "text" in notify_input["selector"]
    assert notify_input.get("default") == ""


def test_trigger_is_time_trigger():
    """Test that trigger is configured as a time trigger."""
    data = _load_blueprint()
    trigger = data.get("trigger", [])

    assert isinstance(trigger, list)
    assert len(trigger) > 0

    # Should be a time trigger
    assert trigger[0].get("trigger") == "time"


def test_blueprint_has_action_section():
    """Test that blueprint has an action section."""
    data = _load_blueprint()
    assert "action" in data

    action = data.get("action", [])
    assert isinstance(action, list)
    assert len(action) > 0


def test_blueprint_locks_all_doors_in_parallel():
    """Test that locks are triggered in parallel."""
    data = _load_blueprint()
    action = data.get("action", [])

    # Find the parallel lock action
    parallel_lock_action = None
    for step in action:
        if step.get("alias") == "Lock all doors in parallel":
            parallel_lock_action = step
            break

    assert parallel_lock_action is not None, "Missing parallel lock action"
    assert parallel_lock_action.get("action") == "homeassistant.turn_on"
    assert "entity_id" in parallel_lock_action.get("target", {})


def test_blueprint_has_retry_logic():
    """Test that blueprint includes retry logic for failed locks."""
    data = _load_blueprint()
    action = data.get("action", [])

    # Find the repeat loop for checking locks (comes after "Wait before checking lock status")
    check_repeat = None
    for idx, step in enumerate(action):
        if step.get("alias") == "Wait before checking lock status":
            # Found the delay, next should be the repeat loop
            if idx + 1 < len(action):
                next_step = action[idx + 1]
                if "repeat" in next_step and "for_each" in next_step.get("repeat", {}):
                    check_repeat = next_step
                    break

    assert check_repeat is not None, "Missing check repeat loop with for_each"

    # Now check that the sequence inside contains retry logic
    repeat_sequence = check_repeat.get("repeat", {}).get("sequence", [])
    has_retry_logic = False
    for seq_step in repeat_sequence:
        if "else" in seq_step:
            # Check if the else block contains a "Lock failed - retry loop"
            else_sequence = seq_step.get("else", [])
            for else_step in else_sequence:
                if else_step.get("alias") == "Lock failed - retry loop" and "repeat" in else_step:
                    has_retry_logic = True
                    break

    assert has_retry_logic, "Missing retry logic in lock check sequence"


def test_blueprint_mode_is_single():
    """Test that blueprint mode is set to single."""
    data = _load_blueprint()
    assert data.get("mode") == "single"
