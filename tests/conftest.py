import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def test_client():
    """Provide a TestClient for API testing"""
    return TestClient(app)


@pytest.fixture
def fresh_activities(monkeypatch):
    """
    Provide a fresh copy of activities for each test.
    
    Uses monkeypatch to temporarily replace the app's activities
    with a deep copy, ensuring test isolation and no side effects.
    """
    # Create a fresh copy of the original activities
    original_activities = copy.deepcopy(activities)
    
    # Patch the app's activities with the fresh copy
    monkeypatch.setattr("src.app.activities", original_activities)
    
    # Return the patched activities for test use
    return original_activities
