import copy
from urllib.parse import quote
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

# Keep a copy of the initial in-memory data so tests can reset state
INITIAL = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset activities before each test to ensure test isolation
    activities.clear()
    activities.update(copy.deepcopy(INITIAL))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL))


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_reflects_in_activities():
    email = "new@test.com"
    activity = "Chess Club"

    url = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    r = client.post(url)
    assert r.status_code == 200
    assert f"Signed up {email}" in r.json()["message"]

    # Confirm the participant is present in the activities listing
    r2 = client.get("/activities")
    assert email in r2.json()[activity]["participants"]


def test_signup_duplicate_returns_400():
    email = "michael@mergington.edu"
    activity = "Chess Club"
    url = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    r = client.post(url)
    assert r.status_code == 400


def test_unregister_success():
    email = "michael@mergington.edu"
    activity = "Chess Club"
    url = f"/activities/{quote(activity)}/unregister?email={quote(email)}"
    r = client.post(url)
    assert r.status_code == 200
    assert f"Unregistered {email}" in r.json()["message"]

    r2 = client.get("/activities")
    assert email not in r2.json()[activity]["participants"]


def test_unregister_not_found():
    email = "not@there.com"
    activity = "Chess Club"
    url = f"/activities/{quote(activity)}/unregister?email={quote(email)}"
    r = client.post(url)
    assert r.status_code == 404
