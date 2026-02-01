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


# Ignore the !input tag used by Home Assistant blueprints.
_IgnoreTagLoader.add_constructor('!input', _construct_undefined)


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
    assert "source_url" in blueprint

    assert blueprint["domain"] == "automation"
    assert "github.com/isaackehle/homeassistant" in blueprint["source_url"]


def test_blueprint_has_required_inputs():
    """Test that all required inputs are defined."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    required_inputs = [
        "power_sensor",
        "indicator_light",
        "coffee_pot_switch",
        "brewing_state",
        "log_toggle",
    ]

    for input_name in required_inputs:
        assert input_name in inputs, f"Missing required input: {input_name}"


def test_blueprint_has_brewing_state_input():
    """Test that brewing_state input is properly configured for state management."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    assert "brewing_state" in inputs
    brewing_state = inputs["brewing_state"]

    assert "selector" in brewing_state
    assert "entity" in brewing_state["selector"]
    assert brewing_state["selector"]["entity"]["filter"]["domain"] == "input_boolean"


def test_blueprint_has_threshold_inputs():
    """Test that all threshold inputs are defined with defaults."""
    data = _load_blueprint()
    inputs = data.get("blueprint", {}).get("input", {})

    threshold_inputs = [
        "start_threshold",
        "finish_threshold",
        "in_progress_low",
        "in_progress_high",
    ]

    for input_name in threshold_inputs:
        assert input_name in inputs, f"Missing threshold input: {input_name}"
        assert "default" in inputs[input_name], f"Missing default for {input_name}"


def test_triggers_include_numeric_state_and_time_pattern():
    """Test that triggers include both numeric_state and time_pattern triggers."""
    data = _load_blueprint()
    triggers = data.get("trigger", [])

    trigger_types = [t.get("trigger") or t.get("platform") for t in triggers]

    assert "numeric_state" in trigger_types, "Missing numeric_state trigger"
    assert "time_pattern" in trigger_types, "Missing time_pattern trigger"


def test_action_has_choose_block():
    """Test that action contains a choose block for handling different states."""
    data = _load_blueprint()
    action = data.get("action", [])

    assert len(action) > 0, "Action sequence is empty"

    # First action should be a choose block
    choose_block = action[0]
    assert "choose" in choose_block, "First action should be a choose block"

    branches = choose_block.get("choose", [])
    assert len(branches) >= 4, "Should have at least 4 branches (start, progress, finish, auto-off)"


def test_brewing_started_checks_brewing_state():
    """Test that brewing started branch checks brewing_state is OFF."""
    data = _load_blueprint()
    choose = data.get("action", [])[0].get("choose", [])

    # Find the brewing started branch (checks power > start_threshold, but NOT below)
    brewing_started = None
    for branch in choose:
        conditions = branch.get("conditions", [])
        for cond in conditions:
            if (cond.get("condition") == "numeric_state"
                and "above" in cond
                and "below" not in cond):
                brewing_started = branch
                break
        if brewing_started:
            break

    assert brewing_started is not None, "Brewing started branch not found"

    # Check that it also has a state condition for brewing_state = off
    conditions = brewing_started.get("conditions", [])
    has_brewing_state_check = False
    for state_cond in conditions:
        if state_cond.get("condition") == "state" and state_cond.get("state") == "off":
            has_brewing_state_check = True
            break

    assert has_brewing_state_check, "Brewing started should check brewing_state = off"


def test_brewing_finished_checks_brewing_state():
    """Test that brewing finished branch checks brewing_state is ON."""
    data = _load_blueprint()
    choose = data.get("action", [])[0].get("choose", [])

    # Find the brewing finished branch (checks power < finish_threshold)
    brewing_finished = None
    for branch in choose:
        conditions = branch.get("conditions", [])
        for cond in conditions:
            if cond.get("condition") == "numeric_state" and "below" in cond:
                brewing_finished = branch
                break

    assert brewing_finished is not None, "Brewing finished branch not found"

    # Check that it also has a state condition for brewing_state = on
    conditions = brewing_finished.get("conditions", [])
    has_brewing_state_check = False
    for cond in conditions:
        if cond.get("condition") == "state" and cond.get("state") == "on":
            has_brewing_state_check = True
            break

    assert has_brewing_state_check, "Brewing finished should check brewing_state = on"


def test_brewing_started_sets_brewing_state_on():
    """Test that brewing started sequence sets brewing_state to ON."""
    data = _load_blueprint()
    choose = data.get("action", [])[0].get("choose", [])

    # Find the brewing started branch (checks power > start_threshold, but NOT below)
    brewing_started = None
    for branch in choose:
        conditions = branch.get("conditions", [])
        for cond in conditions:
            if (cond.get("condition") == "numeric_state"
                and "above" in cond
                and "below" not in cond):
                brewing_started = branch
                break
        if brewing_started:
            break

    assert brewing_started is not None

    sequence = brewing_started.get("sequence", [])
    has_turn_on = False
    for step in sequence:
        action = step.get("action") or step.get("service")
        if action == "input_boolean.turn_on":
            has_turn_on = True
            break

    assert has_turn_on, "Brewing started should turn ON brewing_state"


def test_brewing_finished_sets_brewing_state_off():
    """Test that brewing finished sequence sets brewing_state to OFF."""
    data = _load_blueprint()
    choose = data.get("action", [])[0].get("choose", [])

    # Find the brewing finished branch
    brewing_finished = None
    for branch in choose:
        conditions = branch.get("conditions", [])
        for cond in conditions:
            if cond.get("condition") == "numeric_state" and "below" in cond:
                brewing_finished = branch
                break

    assert brewing_finished is not None

    sequence = brewing_finished.get("sequence", [])
    has_turn_off = False
    for step in sequence:
        action = step.get("action") or step.get("service")
        if action == "input_boolean.turn_off":
            has_turn_off = True
            break

    assert has_turn_off, "Brewing finished should turn OFF brewing_state"


def test_auto_off_resets_brewing_state():
    """Test that auto-off sequence resets brewing_state to OFF."""
    data = _load_blueprint()
    choose = data.get("action", [])[0].get("choose", [])

    # Find the auto-off branch (checks switch state with for: minutes)
    auto_off = None
    for branch in choose:
        conditions = branch.get("conditions", [])
        for cond in conditions:
            if cond.get("condition") == "state" and "for" in cond:
                auto_off = branch
                break

    assert auto_off is not None, "Auto-off branch not found"

    sequence = auto_off.get("sequence", [])
    has_reset_state = False
    for step in sequence:
        action = step.get("action") or step.get("service")
        if action == "input_boolean.turn_off":
            has_reset_state = True
            break

    assert has_reset_state, "Auto-off should reset brewing_state to OFF"


def test_auto_off_turns_off_switch():
    """Test that auto-off sequence turns off the coffee pot switch."""
    data = _load_blueprint()
    choose = data.get("action", [])[0].get("choose", [])

    # Find the auto-off branch
    auto_off = None
    for branch in choose:
        conditions = branch.get("conditions", [])
        for cond in conditions:
            if cond.get("condition") == "state" and "for" in cond:
                auto_off = branch
                break

    assert auto_off is not None

    sequence = auto_off.get("sequence", [])
    has_switch_off = False
    for step in sequence:
        action = step.get("action") or step.get("service")
        if action == "switch.turn_off":
            has_switch_off = True
            break

    assert has_switch_off, "Auto-off should turn off the switch"


def test_mode_is_restart():
    """Test that automation mode is 'restart'."""
    data = _load_blueprint()
    mode = data.get("mode")

    assert mode == "restart", "Mode should be 'restart'"


def test_variables_section_includes_brewing_state():
    """Test that variables section extracts brewing_state input."""
    data = _load_blueprint()
    variables = data.get("variables", {})

    assert "brewing_state" in variables, "Variables should include brewing_state"
