"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_data():
    """Provide sample data for testing."""
    return {
        "test_key": "test_value",
        "test_number": 42,
    }


@pytest.fixture
def mock_agent():
    """Provide mock agent for testing."""
    class MockAgent:
        def __init__(self):
            self.name = "MockAgent"
            self.state = "idle"

        def execute(self):
            self.state = "running"
            return {"status": "success"}

    return MockAgent()
