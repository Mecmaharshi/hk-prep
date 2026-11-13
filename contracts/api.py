"""Shapes shared by the whole team: the frontend, the API and the ML code all build on these.

At the start, the lead replaces these examples with the real shapes for the problem.
See them live at http://localhost:8000/docs (start the API with: hk run).
"""

from pydantic import BaseModel, Field


class Item(BaseModel):
    """One thing to make a prediction for, like one complaint or one order."""

    id: str = Field(examples=["item-001"])
    text: str = Field(examples=["Water pipe leaking near the bus stand"])


class Prediction(BaseModel):
    """The answer for one item."""

    id: str = Field(examples=["item-001"])
    label: str = Field(examples=["Water Supply"])
    score: float = Field(ge=0, le=1, examples=[0.82])
    reasons: list[str] = Field(default_factory=list, examples=[["Mentions a leak"]])


class PredictRequest(BaseModel):
    items: list[Item]


class PredictResponse(BaseModel):
    predictions: list[Prediction]


class Health(BaseModel):
    status: str = "ok"
    model: str = Field(examples=["fake"], description="real = the ML team's model, fake = backup")
    note: str = ""
