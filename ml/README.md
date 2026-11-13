# ML

When your model is ready, add `ml/predict.py` with one function:

```python
from contracts.api import Item, Prediction

# Load model files here, once, not inside predict().


def predict(items: list[Item]) -> list[Prediction]:
    # Return one Prediction per item, in the same order.
    ...
```

The API then uses your model instead of the fake one. Check: http://localhost:8000/health says `"model": "real"`.

- Put model files in `ml/artifacts/`. Files over 5 MB can't be pushed: share those by drive.
- Packages your model needs go in `ml/requirements.txt`.
