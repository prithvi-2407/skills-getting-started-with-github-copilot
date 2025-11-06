import urllib.parse

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_signup_and_delete_flow():
    activity = "Chess Club"
    encoded = urllib.parse.quote(activity, safe="")
    email = "test.user@example.com"

    # Ensure clean start
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Sign up
    resp = client.post(f"/activities/{encoded}/signup", params={"email": email})
    assert resp.status_code == 200, resp.text
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email in data[activity]["participants"]

    # Duplicate signup should fail
    resp = client.post(f"/activities/{encoded}/signup", params={"email": email})
    assert resp.status_code == 400

    # Remove participant
    resp = client.delete(f"/activities/{encoded}/participants", params={"email": email})
    assert resp.status_code == 200, resp.text

    # Verify removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity]["participants"]

    # Removing again returns 404
    resp = client.delete(f"/activities/{encoded}/participants", params={"email": email})
    assert resp.status_code == 404


def test_nonexistent_activity():
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404

    resp = client.delete("/activities/NoSuchActivity/participants", params={"email": "a@b.com"})
    assert resp.status_code == 404
