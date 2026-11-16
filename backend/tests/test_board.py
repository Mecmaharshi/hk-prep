"""The board must load with or without git, gh, a plan or a key. It never calls the network itself."""

from fastapi.testclient import TestClient

from backend.app.board.data import parse_plan
from backend.app.main import app

client = TestClient(app)

PLAN = """# Plan: Demo

Goal: classify complaints

| ID | Task | For | Files | Needs | Done when |
|---|---|---|---|---|---|
| B-01 | Real shapes | lead | contracts/api.py | – | /docs shows them |
| F-02 | Results table | anyone | frontend/src/Results.tsx | B-01 | table shows labels |
"""


def test_parse_plan_reads_header_and_rows():
    header, tasks = parse_plan(PLAN)
    assert header["title"] == "Plan: Demo"
    assert header["Goal"] == "classify complaints"
    assert [t["id"] for t in tasks] == ["B-01", "F-02"]
    assert tasks[1]["for"] == "anyone"
    assert tasks[1]["files"] == "frontend/src/Results.tsx"
    assert tasks[1]["done_when"] == "table shows labels"


def test_board_page_and_sections_load():
    assert "<title>Team board</title>" in client.get("/board").text
    for section in ("overview", "plan", "team", "api", "llm", "data"):
        response = client.get(f"/board/api/{section}")
        assert response.status_code == 200, section
        assert isinstance(response.json(), dict)


def test_api_tab_lists_the_contract_shapes():
    body = client.get("/board/api/api").json()
    assert "Item" in body["shapes"] and "Prediction" in body["shapes"]
    assert any(e["path"] == "/predict" for e in body["endpoints"])
    assert not any(e["path"].startswith("/board") for e in body["endpoints"])


def test_guide_page_and_text_load():
    assert "<title>Team guide</title>" in client.get("/board/guide").text
    assert client.get("/guide", follow_redirects=False).headers["location"] == "/board/guide"
    body = client.get("/board/api/guide").json()
    assert body["text"].startswith("# Team guide")
