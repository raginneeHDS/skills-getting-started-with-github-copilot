import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities_state():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_activity_data(client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert activity_name in payload
    assert "participants" in payload[activity_name]
    assert isinstance(payload[activity_name]["participants"], list)


def test_signup_for_activity_appends_participant(client):
    # Arrange
    activity_name = "Soccer Team"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_email(client):
    # Arrange
    first_activity = "Soccer Team"
    second_activity = "Chess Club"
    email = "duplicatestudent@mergington.edu"

    client.post(
        f"/activities/{first_activity}/signup",
        params={"email": email}
    )

    # Act
    response = client.post(
        f"/activities/{second_activity}/signup",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for an activity"


def test_remove_participant_unregisters_email(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_remove_participant_missing_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "missingstudent@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found for this activity"