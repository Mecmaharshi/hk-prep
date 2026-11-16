"""Where the board gets its facts: git, PLAN.md, TEAM.md, the model, the LLM, gh.

Every function returns a dict and never raises: a missing tool or file becomes a "note" in the
answer, so one broken source greys out one card instead of the whole page. Read-only: nothing
here writes to git or to files, and raw data under data/ is never opened.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

log = logging.getLogger("uvicorn.error")
ROOT = Path(__file__).resolve().parents[3]
REMOTE = os.getenv("HK_REMOTE", "origin")
MAIN = os.getenv("HK_MAIN", "main")
TASK_ID = re.compile(r"^[A-Z]-\d\d$")
_cache: dict[str, tuple[float, object]] = {}


def run(*args: str, timeout: int = 15) -> str | None:
    """Stdout of a command run in the repo, or None if it fails or isn't installed."""
    try:
        done = subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout if done.returncode == 0 else None


def cached(key: str, seconds: float, compute):
    now = time.time()
    hit = _cache.get(key)
    if hit and now - hit[0] < seconds:
        return hit[1]
    value = compute()
    _cache[key] = (now, value)
    return value


def git(*args: str, timeout: int = 15) -> str | None:
    return run("git", *args, timeout=timeout)


def fetch() -> None:
    """At most once every 30 s, so a page of people refreshing doesn't hammer GitHub."""
    cached("fetch", 30, lambda: git("fetch", "--quiet", "--prune", REMOTE, timeout=20))


def read(path: str) -> str | None:
    file = ROOT / path
    return file.read_text(encoding="utf-8", errors="replace") if file.is_file() else None


def cells(line: str) -> list[str]:
    return [c.strip().replace("`", "") for c in line.strip().strip("|").split("|")]


# ----- plan -----------------------------------------------------------------------------------


def parse_plan(text: str) -> tuple[dict, list[dict]]:
    """PLAN.md → (header lines like Goal/How/Backup, task rows). Columns: ID Task For Files Needs Done when."""
    header: dict[str, str] = {}
    tasks: list[dict] = []
    for line in text.splitlines():
        if line.startswith("|"):
            row = cells(line)
            if row and TASK_ID.match(row[0]):
                row += [""] * (6 - len(row))
                tasks.append(
                    {
                        "id": row[0],
                        "task": row[1],
                        "for": row[2],
                        "files": row[3],
                        "needs": row[4],
                        "done_when": row[5],
                    }
                )
        elif line.startswith("# "):
            header["title"] = line[2:].strip()
        else:
            match = re.match(
                r"^(Goal|How|Backup|Demo|Watch out|Later, only if time|Times):\s*(.*)$", line
            )
            if match:
                header[match.group(1)] = match.group(2).strip()
    return header, tasks


def plan() -> dict:
    fetch()
    source = f"{REMOTE}/{MAIN}"
    text = git("show", f"{source}:PLAN.md")
    if text is None:
        text, source = read("PLAN.md"), "this laptop"
    if text is None:
        return {
            "tasks": [],
            "header": {},
            "counts": {},
            "note": "No PLAN.md yet. The lead makes it with /hk-plan.",
        }
    header, tasks = parse_plan(text)

    merged = [
        line.split("|")
        for line in (git("log", f"{REMOTE}/{MAIN}", "--format=%s|%an|%cI") or "").splitlines()
    ]
    branches = [
        line.split("|")
        for line in (
            git(
                "for-each-ref",
                "--format=%(refname:short)|%(authorname)|%(committerdate:iso-strict)",
                f"refs/remotes/{REMOTE}/task/",
            )
            or ""
        ).splitlines()
    ]
    counts = {"done": 0, "in_progress": 0, "free": 0}
    for task in tasks:
        tid = task["id"]
        done = next(
            (
                m
                for m in merged
                if len(m) == 3
                and (m[0].startswith(f"{tid}:") or re.search(rf"task/{tid}(-|$| )", m[0]))
            ),
            None,
        )
        branch = next(
            (b for b in branches if len(b) == 3 and re.search(rf"task/{tid}(-|$)", b[0])), None
        )
        if done:
            task.update(state="done", who=done[1], at=done[2])
            counts["done"] += 1
        elif branch:
            task.update(
                state="in progress", who=branch[1], at=branch[2], branch=branch[0].split("/", 1)[-1]
            )
            counts["in_progress"] += 1
        else:
            task.update(state="free", who="", at="")
            counts["free"] += 1
    return {
        "source": source,
        "header": header,
        "tasks": tasks,
        "counts": counts,
        "me": (git("config", "user.name") or "").strip(),
        "git": git("--version") is not None,
        "note": ""
        if git("rev-parse", "--git-dir")
        else "Not a git repo on this laptop: states come from nowhere yet.",
    }


# ----- guide ----------------------------------------------------------------------------------


def guide() -> dict:
    """docs/GUIDE.md as text for /board/guide. Falls back to origin/main if this laptop lacks it."""
    text = read("docs/GUIDE.md") or git("show", f"{REMOTE}/{MAIN}:docs/GUIDE.md")
    if text is None:
        return {"text": "", "note": "docs/GUIDE.md not found. Run: hk sync"}
    return {"text": text, "source": "docs/GUIDE.md"}


# ----- team -----------------------------------------------------------------------------------


def team() -> dict:
    text = read("TEAM.md")
    if text is None:
        return {"people": [], "note": "No TEAM.md."}
    people, event, ends, header_seen = [], "", "", False
    for line in text.splitlines():
        if line.startswith("Event:"):
            event = line[6:].strip()
        elif line.startswith("Ends:"):
            ends = line[5:].strip()
        elif line.startswith("|"):
            row = cells(line)
            if not header_seen:
                header_seen = True
                continue
            if set("".join(row)) <= set("-: "):
                continue
            row += [""] * (4 - len(row))
            if row[0] or row[1]:
                people.append({"name": row[0], "role": row[1], "good_at": row[2], "hours": row[3]})
    hours_left = None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            hours_left = round(
                (datetime.strptime(ends, fmt) - datetime.now()).total_seconds() / 3600, 1
            )
            break
        except ValueError:
            continue
    return {"people": people, "event": event, "ends": ends, "hours_left": hours_left}


# ----- api and model --------------------------------------------------------------------------


def _type_of(schema: dict, components: dict) -> str:
    if "$ref" in schema:
        return schema["$ref"].split("/")[-1]
    if "anyOf" in schema:
        return " | ".join(_type_of(s, components) for s in schema["anyOf"])
    kind = schema.get("type", "any")
    if kind == "array":
        return f"list of {_type_of(schema.get('items', {}), components)}"
    return kind


def shapes(openapi: dict) -> dict:
    """components.schemas → {Name: [{field, type, required, example}]}: the contracts, readable by anyone."""
    components = openapi.get("components", {}).get("schemas", {})
    out = {}
    for name, schema in components.items():
        if name.endswith("Error") or name == "ValidationError":
            continue
        required = set(schema.get("required", []))
        out[name] = [
            {
                "field": field,
                "type": _type_of(prop, components),
                "required": field in required,
                "example": (prop.get("examples") or [prop.get("default", "")])[0]
                if isinstance(prop, dict)
                else "",
            }
            for field, prop in schema.get("properties", {}).items()
        ]
    return out


def endpoints(openapi: dict) -> list[dict]:
    out = []
    for path, methods in openapi.get("paths", {}).items():
        if path.startswith("/board"):
            continue
        for method, op in methods.items():
            body = (
                op.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema", {})
            )
            resp = (
                op.get("responses", {})
                .get("200", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema", {})
            )
            out.append(
                {
                    "method": method.upper(),
                    "path": path,
                    "summary": op.get("summary") or op.get("description", ""),
                    "request": body.get("$ref", "").split("/")[-1],
                    "response": resp.get("$ref", "").split("/")[-1],
                }
            )
    return out


def model_info() -> dict:
    from backend.app import model

    artifacts = ROOT / "ml" / "artifacts"
    files = sorted(artifacts.rglob("*")) if artifacts.is_dir() else []
    return {
        "mode": model.MODE,
        "note": model.NOTE,
        "predict_file": model.ML_FILE.exists(),
        "artifacts": [
            {
                "name": str(f.relative_to(ROOT)).replace("\\", "/"),
                "mb": round(f.stat().st_size / 1_000_000, 2),
            }
            for f in files
            if f.is_file()
        ],
    }


# ----- llm ------------------------------------------------------------------------------------


def llm_status() -> dict:
    from backend.app import llm

    return llm.status()


def llm_test(prompt: str) -> dict:
    from backend.app import llm

    started = time.time()
    try:
        answer = llm.ask(prompt or "Reply with one short friendly sentence.", max_tokens=200)
        return {
            "ok": True,
            "answer": answer,
            "ms": int((time.time() - started) * 1000),
            "provider": llm.PROVIDER,
            "model": llm.MODEL,
        }
    except Exception as error:  # noqa: BLE001 - shown on the board, never crashes the API
        return {
            "ok": False,
            "error": str(error),
            "ms": int((time.time() - started) * 1000),
            "provider": llm.PROVIDER,
            "model": llm.MODEL,
        }


# ----- data -----------------------------------------------------------------------------------


def data() -> dict:
    folder = ROOT / "data"
    files = []
    if folder.is_dir():
        for f in sorted(folder.rglob("*")):
            if f.is_file() and f.name != "README.md":
                files.append(
                    {
                        "name": str(f.relative_to(folder)).replace("\\", "/"),
                        "mb": round(f.stat().st_size / 1_000_000, 2),
                    }
                )
    return {
        "summary": read("docs/data-summary.md"),
        "files": files,
        "note": "" if files else "Nothing in data/ on this laptop.",
    }


# ----- checks: doctor, CI, pull requests -------------------------------------------------------


def bash() -> str | None:
    found = shutil.which("bash")
    if found:
        return found
    for candidate in (
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
    ):
        if Path(candidate).exists():
            return candidate
    return None


def doctor() -> dict:
    shell = bash()
    if not shell:
        return {
            "output": "",
            "ok": False,
            "note": "bash not found, so hk doctor can't run from here. Run it in Git Bash.",
        }
    try:
        done = subprocess.run(
            [shell, "hk", "doctor"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=90,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return {"output": "", "ok": False, "note": f"hk doctor didn't finish: {error}"}
    return {"output": done.stdout + done.stderr, "ok": done.returncode == 0, "note": ""}


def github() -> dict:
    def compute():
        if not shutil.which("gh"):
            return {
                "prs": [],
                "ci": None,
                "note": "GitHub CLI (gh) not installed: no PR or CI info here. Still works on GitHub itself.",
            }
        import json

        prs_raw = run(
            "gh",
            "pr",
            "list",
            "--state",
            "open",
            "--limit",
            "30",
            "--json",
            "number,title,headRefName,author,url,reviewDecision,statusCheckRollup,createdAt",
            timeout=20,
        )
        if prs_raw is None:
            return {
                "prs": [],
                "ci": None,
                "note": "gh isn't logged in (gh auth login), or this isn't a GitHub repo yet.",
            }
        prs = []
        for pr in json.loads(prs_raw or "[]"):
            checks = pr.get("statusCheckRollup") or []
            states = {(c.get("conclusion") or c.get("state") or "").upper() for c in checks}
            if not checks:
                check = "none"
            elif states & {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED"}:
                check = "failing"
            elif states - {"SUCCESS", "NEUTRAL", "SKIPPED"}:
                check = "running"
            else:
                check = "passing"
            prs.append(
                {
                    "number": pr["number"],
                    "title": pr["title"],
                    "branch": pr["headRefName"],
                    "author": (pr.get("author") or {}).get("login", ""),
                    "url": pr["url"],
                    "review": (pr.get("reviewDecision") or "waiting").lower().replace("_", " "),
                    "checks": check,
                    "created": pr.get("createdAt", ""),
                }
            )
        ci_raw = run(
            "gh",
            "run",
            "list",
            "--branch",
            MAIN,
            "--limit",
            "1",
            "--json",
            "status,conclusion,url,displayTitle,updatedAt",
            timeout=20,
        )
        ci = (json.loads(ci_raw or "[]") or [None])[0]
        return {"prs": prs, "ci": ci, "note": ""}

    return cached("github", 60, compute)
