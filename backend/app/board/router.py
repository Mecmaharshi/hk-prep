"""GET /board (the page), /board/guide (the team guide), /board/api/<section> (facts as JSON)."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from backend.app.board import data

router = APIRouter(prefix="/board", include_in_schema=False)
PAGE = Path(__file__).with_name("index.html")
GUIDE = Path(__file__).with_name("guide.html")


def safe(section: str, compute) -> dict:
    try:
        return compute()
    except Exception as error:  # noqa: BLE001 - one broken card, not a broken page
        data.log.warning("board/%s failed: %s", section, error)
        return {"error": f"{type(error).__name__}: {error}"}


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
def page() -> HTMLResponse:
    return HTMLResponse(PAGE.read_text(encoding="utf-8"), headers={"Cache-Control": "no-store"})


@router.get("/guide", response_class=HTMLResponse)
def guide_page() -> HTMLResponse:
    return HTMLResponse(GUIDE.read_text(encoding="utf-8"), headers={"Cache-Control": "no-store"})


@router.get("/api/guide")
def guide() -> dict:
    return safe("guide", data.guide)


@router.get("/api/overview")
def overview(request: Request) -> dict:
    return {
        "plan": safe("plan", data.plan),
        "team": safe("team", data.team),
        "model": safe("model", data.model_info),
        "llm": safe("llm", data.llm_status),
        "github": safe("github", data.github),
    }


@router.get("/api/plan")
def plan() -> dict:
    return safe("plan", data.plan)


@router.get("/api/team")
def team() -> dict:
    return {"team": safe("team", data.team), "plan": safe("plan", data.plan)}


@router.get("/api/api")
def api(request: Request) -> dict:
    openapi = request.app.openapi()
    return {
        "model": safe("model", data.model_info),
        "endpoints": safe("endpoints", lambda: data.endpoints(openapi)),
        "shapes": safe("shapes", lambda: data.shapes(openapi)),
    }


@router.get("/api/llm")
def llm() -> dict:
    return safe("llm", data.llm_status)


class TestPrompt(BaseModel):
    prompt: str = ""


@router.post("/api/llm/test")
def llm_test(body: TestPrompt) -> dict:
    return safe("llm_test", lambda: data.llm_test(body.prompt))


@router.get("/api/data")
def data_tab() -> dict:
    return safe("data", data.data)


@router.get("/api/checks")
def checks() -> dict:
    return {"doctor": safe("doctor", data.doctor), "github": safe("github", data.github)}
