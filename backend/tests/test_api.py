"""API tests. Update them when contracts/api.py changes."""

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health_says_which_model():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["model"] in ("real", "fake")


def test_predict_gives_one_answer_per_item():
    items = [{"id": "1", "text": "Water pipe leaking"}, {"id": "2", "text": "Pothole on main road"}]
    response = client.post("/predict", json={"items": items})
    assert response.status_code == 200
    predictions = response.json()["predictions"]
    assert [p["id"] for p in predictions] == ["1", "2"]
    assert all(0 <= p["score"] <= 1 for p in predictions)
