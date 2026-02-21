# Testing Automations

This directory contains shared pytest helpers and non-blueprint tests.
Blueprint tests are colocated next to each blueprint file in `blueprints/`.

## Setup

Install test dependencies:

```bash
pip install -r requirements-test.txt
```

## Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_example_automation.py

# Run a colocated blueprint test
pytest blueprints/automation/coffee_pot_monitor/test_coffee_pot_monitor_blueprint.py

# Run in verbose mode
pytest -v
```

## Writing Tests

1. **YAML Validation Tests**: Verify automations parse correctly (included)
2. **Logic Tests**: Mock triggers and verify automation behaves correctly
3. **Integration Tests**: Test with Home Assistant components

Example test structure:

```python
@pytest.mark.asyncio
async def test_my_automation(hass):
    """Test my automation."""
    # Setup
    hass.states.set('sensor.temperature', '72')

    # Trigger automation
    await hass.services.async_call('automation', 'trigger', {
        'entity_id': 'automation.my_automation'
    })

    # Assert expected result
    assert hass.states.get('light.my_light').state == 'on'
```

## Current Tests

- `test_example_automation.py`: Basic validation that all automations are valid YAML
