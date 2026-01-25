import pytest
from pathlib import Path

import yaml

# Custom loader to ignore unknown tags like !input
class IgnoreUnknownTagsLoader(yaml.SafeLoader):
    pass

def ignore_unknown(loader, tag_suffix, node):
    if isinstance(node, yaml.ScalarNode):
        return loader.construct_scalar(node)
    elif isinstance(node, yaml.SequenceNode):
        return loader.construct_sequence(node)
    elif isinstance(node, yaml.MappingNode):
        return loader.construct_mapping(node)
    else:
        return None

IgnoreUnknownTagsLoader.add_multi_constructor('!', ignore_unknown)

def load_blueprint_yaml():
    blueprint_path = Path(__file__).parent / "coffee-pot-monitor.yaml"
    with open(blueprint_path) as f:
        return yaml.load(f, Loader=IgnoreUnknownTagsLoader)

def test_blueprint_yaml_valid():
    """Test that the coffee pot monitor blueprint YAML is valid."""
    data = load_blueprint_yaml()
    assert isinstance(data, dict)
    assert 'blueprint' in data
    assert 'input' in data['blueprint']
    assert 'trigger' in data
    assert 'action' in data

def test_blueprint_has_auto_off():
    """Test that the blueprint includes the auto-off trigger and action."""
    data = load_blueprint_yaml()
    triggers = data.get('trigger', [])
    # Look for a trigger with 15 minute for and coffee_pot_switch
    found = False
    for trig in triggers:
        entity_id = trig.get('entity_id')
        # Accept both the literal string and the parsed value
        if (
            (trig.get('platform') == 'state') and
            (entity_id == '!input coffee_pot_switch' or str(entity_id).endswith('coffee_pot_switch')) and
            (trig.get('to') == 'on') and
            (trig.get('for', {}).get('minutes') == 15)
        ):
            found = True
            break
    if not found:
        print('DEBUG: triggers:', triggers)
    assert found, "Auto-off trigger for coffee_pot_switch after 15 minutes not found"

    # Check action for switch.turn_off
    choose = data.get('action', [{}])[0].get('choose', [])
    found_action = False
    for branch in choose:
        seq = branch.get('sequence', [])
        for step in seq:
            if isinstance(step, dict) and step.get('service') == 'switch.turn_off':
                found_action = True
                break
    assert found_action, "No switch.turn_off action found in blueprint for auto-off"
