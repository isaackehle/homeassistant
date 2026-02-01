"""Pytest configuration for automation tests."""
import pytest
from pathlib import Path
import yaml


@pytest.fixture
def automation_yaml():
    """Fixture to load automation files for testing."""
    def _load_automation(filename):
        path = Path(__file__).parent.parent / "automations" / filename
        with open(path) as f:
            data = yaml.safe_load(f)
            return data[0] if isinstance(data, list) else data

    return _load_automation
