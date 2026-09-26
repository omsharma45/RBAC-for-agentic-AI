from fastapi.testclient import TestClient

from app.main import AUDIT_LOG, app

client = TestClient(app)


def setup_function() -> None:
    AUDIT_LOG.clear()


def test_viewer_can_read_report() -> None:
    response = client.post(
        "/agent/run", headers={"X-User-Id": "alice"}, json={"task": "show the quarterly report"}
    )
    assert response.status_code == 200
    assert response.json()["steps"][0]["status"] == "executed"


def test_viewer_cannot_invite_user_and_event_is_audited() -> None:
    response = client.post(
        "/agent/run", headers={"X-User-Id": "alice"}, json={"task": "invite sam@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["steps"][0]["status"] == "denied"
    assert AUDIT_LOG[0].allowed is False


def test_admin_can_invite_user() -> None:
    response = client.post(
        "/agent/run", headers={"X-User-Id": "carol"}, json={"task": "invite sam@example.com"}
    )
    assert response.status_code == 200
    assert response.json()["steps"][0]["status"] == "executed"


def test_unknown_user_is_rejected() -> None:
    response = client.post("/agent/run", headers={"X-User-Id": "unknown"}, json={"task": "show report"})
    assert response.status_code == 401
