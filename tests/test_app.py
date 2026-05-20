from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = deepcopy(activities)
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


client = TestClient(app)


def test_get_activities_returns_available_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_adds_participant():
    new_email = "newstudent@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup?email=newstudent%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert new_email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    duplicate_email = "michael@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup?email=michael%40mergington.edu"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_signup_unknown_activity_returns_404():
    response = client.post(
        "/activities/Nonexistent%20Club/signup?email=test%40example.com"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_removes_user():
    email = "john@mergington.edu"
    response = client.delete(
        "/activities/Gym%20Class/participants?email=john%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Removed john@mergington.edu from Gym Class"
    assert email not in activities["Gym Class"]["participants"]


def test_remove_nonexistent_participant_returns_404():
    response = client.delete(
        "/activities/Gym%20Class/participants?email=ghost%40mergington.edu"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
