"""Tests for the ceiling fan direction control blueprint YAML structure."""
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
    path = Path(__file__).parent / "ceiling_fan_direction_control.yaml"
    with path.open() as handle:
        return yaml.load(handle, Loader=_IgnoreTagLoader)


def _index_of_step(sequence, key):
    """Find index of a step containing the specified key."""
    for idx, step in enumerate(sequence):
        if key in step:
            return idx
    return -1


def _index_of_action_containing(sequence, action_name):
    """Find index of a step with action/service containing the specified name."""
    for idx, step in enumerate(sequence):
        action_value = step.get("action") or step.get("service")
        if action_value and action_name in str(action_value):
            return idx
    return -1


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
    assert "author" in blueprint
    assert "source_url" in blueprint

    assert blueprint["domain"] == "automation"
    assert "github.com/isaackehle/homeassistant" in blueprint["source_url"]


def test_blueprint_has_required_inputs():
    """Test that all required inputs are defined."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    required_inputs = [
        "ceiling_fan",
        "direction_relay",
        "direction_selector",
    ]

    for input_name in required_inputs:
        assert input_name in inputs, f"Missing required input: {input_name}"


def test_blueprint_has_optional_inputs():
    """Test that optional inputs are defined with defaults."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    # Check optional inputs exist
    assert "notification_targets" in inputs
    assert "motor_stop_delay" in inputs
    assert "relay_settle_delay" in inputs
    assert "enable_notifications" in inputs

    # Check defaults
    assert inputs["notification_targets"]["default"] == []
    assert inputs["motor_stop_delay"]["default"] == 10
    assert inputs["relay_settle_delay"]["default"] == 3
    assert inputs["enable_notifications"]["default"] is True


def test_uses_modern_yaml_syntax():
    """Test that blueprint uses triggers/conditions/actions (not singular)."""
    data = _load_blueprint()

    assert "triggers" in data, "Should use 'triggers' (plural), not 'trigger'"
    assert "trigger" not in data, "Should not use legacy 'trigger' (singular) at top level"

    assert "conditions" in data, "Should use 'conditions' (plural), not 'condition'"
    assert "condition" not in data, "Should not use legacy 'condition' (singular) at top level"

    assert "actions" in data, "Should use 'actions' (plural), not 'action'"
    assert "action" not in data, "Should not use legacy 'action' (singular) at top level"


def test_triggers_use_trigger_not_platform():
    """Test that trigger entries use 'trigger:' key, not legacy 'platform:'."""
    data = _load_blueprint()
    triggers = data.get("triggers", [])

    for t in triggers:
        assert "trigger" in t, "Each trigger should use 'trigger:' key, not 'platform:'"
        assert "platform" not in t, "Should not use legacy 'platform:' key"


def test_trigger_is_state_change():
    """Test that trigger is configured for input_select state changes."""
    data = _load_blueprint()
    triggers = data.get("triggers", [])

    assert isinstance(triggers, list)
    assert len(triggers) > 0

    # Should have a state trigger on direction_selector
    state_trigger = triggers[0]
    assert state_trigger.get("trigger") == "state"


def test_condition_checks_state_actually_changed():
    """Test that condition verifies the state actually changed."""
    data = _load_blueprint()
    conditions = data.get("conditions", [])

    assert isinstance(conditions, list)
    assert len(conditions) > 0

    # Should have template condition checking from_state != to_state
    template_condition = conditions[0]
    assert template_condition.get("condition") == "template"

    template = template_condition.get("value_template", "")
    assert "trigger.from_state.state" in template
    assert "trigger.to_state.state" in template
    assert "!=" in template


def test_action_sequence_has_correct_order():
    """Test that action sequence follows the safety protocol."""
    data = _load_blueprint()
    action = data.get("actions", [])

    # Find key steps in the sequence
    fan_off_idx = _index_of_action_containing(action, "fan.turn_off")
    first_delay_idx = -1
    relay_choose_idx = -1
    second_delay_idx = -1

    # Find first delay (motor stop)
    for idx, step in enumerate(action):
        if "delay" in step and idx > fan_off_idx:
            first_delay_idx = idx
            break

    # Find choose block for relay direction change (contains cover actions)
    for idx, step in enumerate(action):
        if "choose" in step:
            # Check if this choose block contains cover actions
            for branch in step.get("choose", []):
                sequence = branch.get("sequence", [])
                for seq_step in sequence:
                    action_value = seq_step.get("action") or seq_step.get("service")
                    if action_value and "cover." in str(action_value):
                        relay_choose_idx = idx
                        break
                if relay_choose_idx != -1:
                    break

    # Find second delay (relay settle) - should be after relay choose
    for idx, step in enumerate(action):
        if "delay" in step and idx > relay_choose_idx and relay_choose_idx != -1:
            second_delay_idx = idx
            break

    # Verify sequence order
    assert fan_off_idx != -1, "Missing fan.turn_off action"
    assert first_delay_idx != -1, "Missing motor stop delay"
    assert relay_choose_idx != -1, "Missing choose block for relay control"
    assert second_delay_idx != -1, "Missing relay settle delay"

    # Verify correct order: turn_off → delay → choose → delay
    assert fan_off_idx < first_delay_idx, "Fan turn_off must come before motor stop delay"
    assert first_delay_idx < relay_choose_idx, "Motor stop delay must come before relay change"
    assert relay_choose_idx < second_delay_idx, "Relay change must come before settle delay"


def test_choose_block_has_both_directions():
    """Test that choose block handles both Forward and Reverse directions."""
    data = _load_blueprint()
    action = data.get("actions", [])

    # Find the choose block that contains cover actions (relay control)
    relay_choose_step = None
    for step in action:
        if "choose" in step:
            # Check if this choose block contains cover actions
            for branch in step.get("choose", []):
                sequence = branch.get("sequence", [])
                for seq_step in sequence:
                    action_value = seq_step.get("action") or seq_step.get("service")
                    if action_value and "cover." in str(action_value):
                        relay_choose_step = step
                        break
                if relay_choose_step is not None:
                    break
            if relay_choose_step is not None:
                break

    assert relay_choose_step is not None, "Relay control choose block not found"

    choose_branches = relay_choose_step.get("choose", [])
    assert len(choose_branches) >= 2, "Choose should have at least 2 branches (Forward and Reverse)"

    # Check that both cover.open_cover and cover.close_cover exist
    found_open = False
    found_close = False

    for branch in choose_branches:
        sequence = branch.get("sequence", [])
        for step in sequence:
            action_value = step.get("action") or step.get("service")
            if action_value:
                if "cover.open_cover" in str(action_value):
                    found_open = True
                if "cover.close_cover" in str(action_value):
                    found_close = True

    assert found_open, "Missing cover.open_cover action for Forward direction"
    assert found_close, "Missing cover.close_cover action for Reverse direction"


def test_mode_is_single():
    """Test that automation mode is 'single' to prevent overlapping direction changes."""
    data = _load_blueprint()
    mode = data.get("mode")

    assert mode == "single", "Mode must be 'single' to prevent overlapping direction changes"


def test_variables_section_exists():
    """Test that variables section extracts key inputs."""
    data = _load_blueprint()
    variables = data.get("variables", {})

    assert isinstance(variables, dict)
    assert len(variables) > 0, "Variables section should extract inputs"


def test_notification_actions_use_targets():
    """Test that notification actions use the target parameter for multiple services."""
    data = _load_blueprint()
    action = data.get("actions", [])

    # Find notification actions (in choose blocks)
    notification_actions = []

    def find_notify_actions(steps):
        """Recursively find notify actions in steps."""
        for step in steps:
            if "choose" in step:
                for branch in step.get("choose", []):
                    find_notify_actions(branch.get("sequence", []))
            action_value = step.get("action") or step.get("service")
            if action_value and "notify" in str(action_value):
                notification_actions.append(step)

    find_notify_actions(action)

    # If notifications exist, they should use target parameter
    for notify_step in notification_actions:
        # Check that it uses target (for multiple notification services)
        assert "target" in notify_step, "Notification actions should use 'target' parameter"


def test_delays_use_variable_references():
    """Test that delay steps reference the configurable delay variables."""
    data = _load_blueprint()
    action = data.get("actions", [])

    # Find delay steps
    delay_steps = [step for step in action if "delay" in step]

    # Should have at least 2 delays (motor stop and relay settle)
    assert len(delay_steps) >= 2, "Should have at least 2 delay steps"

    # Check that delays use template syntax (indicating variable usage)
    for delay_step in delay_steps:
        delay_value = delay_step.get("delay", {})
        if isinstance(delay_value, dict):
            seconds = delay_value.get("seconds")
            # Should be a template string referencing a variable
            assert isinstance(seconds, str), "Delay seconds should reference a variable"
            assert "{{" in seconds or "{" in seconds, "Delay should use template/variable syntax"


def test_input_selectors_are_correctly_typed():
    """Test that input selectors have the correct types."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    # Check entity selectors
    assert "selector" in inputs["ceiling_fan"]
    assert "entity" in inputs["ceiling_fan"]["selector"]
    assert inputs["ceiling_fan"]["selector"]["entity"]["filter"]["domain"] == "fan"

    assert "selector" in inputs["direction_relay"]
    assert "entity" in inputs["direction_relay"]["selector"]
    assert inputs["direction_relay"]["selector"]["entity"]["filter"]["domain"] == "cover"

    assert "selector" in inputs["direction_selector"]
    assert "entity" in inputs["direction_selector"]["selector"]
    assert inputs["direction_selector"]["selector"]["entity"]["filter"]["domain"] == "input_select"

    # Check number selectors
    assert "selector" in inputs["motor_stop_delay"]
    assert "number" in inputs["motor_stop_delay"]["selector"]
    assert inputs["motor_stop_delay"]["selector"]["number"]["min"] >= 5
    assert inputs["motor_stop_delay"]["selector"]["number"]["max"] <= 30

    # Check boolean selector
    assert "selector" in inputs["enable_notifications"]
    assert "boolean" in inputs["enable_notifications"]["selector"]
