"""The one place the API gets its predictions from.

Uses the ML team's ml/predict.py once it exists. Until then, or if it fails to load,
it uses the fake below, so the API always works.
Turn the fake into the plan's Backup (simple rules) early: then the demo works no matter what.
"""

import hashlib
import logging
from collections.abc import Callable
from pathlib import Path

from contracts.api import Item, Prediction

log = logging.getLogger("uvicorn.error")
ML_FILE = Path(__file__).resolve().parents[2] / "ml" / "predict.py"
FAKE_LABELS = ["label-a", "label-b", "label-c"]

Predictor = Callable[[list[Item]], list[Prediction]]


def fake_predict(items: list[Item]) -> list[Prediction]:
    """Made-up but stable answers: the same text always gets the same result."""
    predictions = []
    for item in items:
        number = int(hashlib.md5(item.text.encode()).hexdigest(), 16)
        predictions.append(
            Prediction(
                id=item.id,
                label=FAKE_LABELS[number % len(FAKE_LABELS)],
                score=number % 101 / 100,
                reasons=["Fake model: the real one isn't in yet"],
            )
        )
    return predictions


def _choose() -> tuple[Predictor, str, str]:
    if not ML_FILE.exists():
        return fake_predict, "fake", "ml/predict.py isn't written yet"
    # Broken code or a missing package must not take the API down.
    try:
        from ml.predict import predict
    except Exception as error:  # noqa: BLE001
        log.warning("ml/predict.py didn't load, so the API uses the fake model: %s", error)
        return fake_predict, "fake", f"ml/predict.py didn't load: {error}"
    return predict, "real", ""


predict, MODE, NOTE = _choose()
log.info("Predictions come from the %s model", MODE)
