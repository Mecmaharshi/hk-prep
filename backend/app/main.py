"""The team's API. Start it from the project folder with: hk run"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app import model
from contracts.api import Health, PredictRequest, PredictResponse

app = FastAPI(title="Team API")

# Any frontend, on any laptop, can call the API: fine for a demo, not for production.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.get("/health")
def health() -> Health:
    """Is the API up, and is it using the real model or the fake one?"""
    return Health(model=model.MODE, note=model.NOTE)


@app.post("/predict")
def predict(request: PredictRequest) -> PredictResponse:
    return PredictResponse(predictions=model.predict(request.items))
