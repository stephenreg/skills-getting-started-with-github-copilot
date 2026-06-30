import copy
import pytest
from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app

INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset in-memory activities state before each test."""
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all(client):
    # Arrange — no setup needed, default state is sufficient

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == len(INITIAL_ACTIVITIES)
    for name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success(client):
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in app_module.activities[activity]["participants"]


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity = "Underwater Basket Weaving"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity = "Chess Club"
    email = app_module.activities[activity]["participants"][0]  # already signed up

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success(client):
    # Arrange
    activity = "Chess Club"
    email = app_module.activities[activity]["participants"][0]

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email not in app_module.activities[activity]["participants"]


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    activity = "Underwater Basket Weaving"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_unregister_not_signed_up_returns_404(client):
    # Arrange
    activity = "Chess Club"
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()
