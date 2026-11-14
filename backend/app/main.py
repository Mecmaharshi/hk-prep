"""The team's API. Start it from the project folder with: hk run

/docs   try the endpoints        /board   the team board (plan, team, API, LLM, data, checks)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app import model
from backend.app.board.router import router as board
from contracts.api import Health, PredictRequest, PredictResponse

app = FastAPI(title="Team API")

# Any frontend, on any laptop, can call the API: fine for a demo, not for production.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(board)


@app.get("/health")
def health() -> Health:
    """Is the API up, and is it using the real model or the fake one?"""
    return Health(model=model.MODE, note=model.NOTE)


@app.post("/predict")
def predict(request: PredictRequest) -> PredictResponse:
    return PredictResponse(predictions=model.predict(request.items))
