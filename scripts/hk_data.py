"""hk data: a short dataset summary that anyone, and /hk-plan, can read in a minute.

/hk-plan reads this summary instead of the raw data, which saves AI tokens.
It prints the summary and saves it to docs/data-summary.md.

Usage: hk data [file ...]   (no file: every CSV, Parquet or JSON file in data/)
"""

from __future__ import annotations

import re
import sys
import warnings
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("hk data needs pandas: pip install pandas")

PHONE = re.compile(r"(?<!\d)[6-9]\d{9}(?!\d)")  # Indian mobile numbers
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
YES = {"true", "1", "yes"}
READERS = {
    ".csv": pd.read_csv,
    ".parquet": pd.read_parquet,
    ".json": pd.read_json,
    ".jsonl": lambda path: pd.read_json(path, lines=True),
}
OUT = Path("docs/data-summary.md")


def pct(share: float) -> str:
    return f"{share:.0%}" if share >= 0.1 or share == 0 else f"{share:.1%}"


def mask(value: str) -> str:
    return EMAIL.sub("[email]", PHONE.sub("[phone]", value))


def to_dates(values: pd.Series) -> pd.Series:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return pd.to_datetime(values, errors="coerce")


def kind(column: pd.Series) -> str:
    values = column.dropna()
    if values.empty:
        return "empty"
    text = values.astype(str)
    if column.dtype == bool or set(text.str.lower().unique()) <= YES | {"false", "0", "no"}:
        return "yes/no"
    if pd.api.types.is_numeric_dtype(column):
        return "number"
    if text.str.len().mean() >= 40:
        return "text"
    if to_dates(text.head(300)).notna().mean() > 0.95:
        return "date"
    if values.nunique() / len(values) > 0.98:
        return "id"
    return "category"


def describe(column: pd.Series, k: str) -> str:
    values = column.dropna()
    if k == "empty":
        return "always empty"
    if k == "number":
        return f"{values.min():g} to {values.max():g}, median {values.median():g}"
    if k == "date":
        dates = to_dates(values.astype(str))
        return f"{dates.min():%Y-%m-%d} → {dates.max():%Y-%m-%d}"
    if k == "yes/no":
        return f"{pct(values.astype(str).str.lower().isin(YES).mean())} yes"
    if k == "text":
        return f"free text, median {values.astype(str).str.len().median():.0f} characters"
    if k == "id":
        return "unique per row" if not values.duplicated().any() else "has repeated values"
    top = values.astype(str).value_counts(normalize=True).head(3)
    return ", ".join(f"{mask(name)} {pct(share)}" for name, share in top.items())


def shape(value: str) -> str:
    """'W12' -> 'A99', 'Ward 12' -> 'Aaaa 99'."""
    return re.sub(r"[A-Z]", "A", re.sub(r"[a-z]", "a", re.sub(r"\d", "9", value)))


def missing_note(df: pd.DataFrame, column: str, groups: list[str]) -> str | None:
    missing = df[column].isna()
    rates = {g: missing.groupby(df[g]).mean() for g in groups if g != column}
    for g, r in rates.items():
        always = sorted(str(v) for v in r[r >= 0.99].index)
        if always and r.min() <= 0.6:
            return (
                f"{column} is always empty when {g} is {', '.join(always)}. "
                "Probably filled in later: don't use it to predict."
            )
    for g, r in rates.items():
        worst = r.idxmax()
        elsewhere = missing[df[g] != worst].mean()
        if r.max() >= 0.10 and r.max() >= 5 * max(elsewhere, 0.001):
            return f"{column} is empty far more often when {g} is {worst} ({pct(r.max())} vs {pct(elsewhere)})."
    return None


def watch_outs(df: pd.DataFrame, kinds: dict[str, str]) -> list[str]:
    notes = []
    groups = [
        c for c in df.columns if kinds[c] in ("category", "yes/no") and 2 <= df[c].nunique() <= 12
    ]
    for column in df.columns:
        if 0.005 < df[column].isna().mean() < 0.995:
            note = missing_note(df, column, groups)
            if note:
                notes.append(note)
    for column, k in kinds.items():
        values = df[column].dropna().astype(str)
        if k == "category":
            shapes = values.map(shape)
            shares = shapes.value_counts(normalize=True)
            if 0.9 <= shares.iloc[0] < 1:
                odd = list(dict.fromkeys(values[shapes != shares.index[0]].map(mask)))[:3]
                notes.append(
                    f"{column}: {pct(1 - shares.iloc[0])} don't match the usual format "
                    f"{shares.index[0]} (e.g. {', '.join(odd)}). Clean these up."
                )
        elif k == "text":
            phones = values.map(lambda v: bool(PHONE.search(v))).mean()
            emails = values.map(lambda v: bool(EMAIL.search(v))).mean()
            if phones or emails:
                notes.append(
                    f"{column}: phone numbers in {pct(phones)} of rows, emails in {pct(emails)}. "
                    "Mask them before sending text to AI."
                )
        elif k == "yes/no":
            yes = values.str.lower().isin(YES).mean()
            if yes < 0.15 or yes > 0.85:
                rare, word = (yes, "yes") if yes < 0.5 else (1 - yes, "no")
                notes.append(
                    f"{column}: only {pct(rare)} {word}. "
                    "Rare cases: measure how many you catch, not accuracy."
                )
    return notes


def summarize(path: Path) -> list[str]:
    reader = READERS.get(path.suffix.lower())
    if reader is None:
        return [f"## {path.name}", "", f"Skipped: can't read {path.suffix} files yet.", ""]
    df = reader(path)
    kinds = {c: kind(df[c]) for c in df.columns}
    span = next((describe(df[c], "date") for c, k in kinds.items() if k == "date"), "")
    lines = [
        f"## {path.name}",
        "",
        f"{len(df):,} rows · {df.shape[1]} columns" + (f" · {span}" if span else ""),
        "",
        "Columns:",
    ]
    for column in df.columns:
        k = kinds[column]
        tags = [k]
        if k == "category":
            tags.append(f"{df[column].nunique()} values")
        filled = df[column].notna().mean()
        if filled < 0.995:
            tags.append(f"{pct(filled)} filled")
        lines.append(f"- {column} ({', '.join(tags)}): {describe(df[column], k)}")
    notes = watch_outs(df, kinds) or ["Nothing obvious."]
    return lines + ["", "Watch out:"] + [f"- {n}" for n in notes] + [""]


def main(args: list[str]) -> None:
    paths = [Path(a) for a in args] or sorted(
        p for p in Path("data").glob("*") if p.suffix.lower() in READERS
    )
    if not paths:
        sys.exit("No data files found. Put them in data/, or run: hk data path/to/file.csv")
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        sys.exit(f"Can't find: {', '.join(missing)}")
    lines = [
        "# Data summary",
        "",
        "Made by `hk data`. /hk-plan reads this instead of the raw data.",
        "",
    ]
    for path in paths:
        lines += summarize(path)
    text = "\n".join(lines)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(text)
    print(f"Saved to {OUT}")


if __name__ == "__main__":
    main(sys.argv[1:])
