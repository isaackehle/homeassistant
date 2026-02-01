# Testing Automations

This directory contains pytest tests for Home Assistant automations.

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
