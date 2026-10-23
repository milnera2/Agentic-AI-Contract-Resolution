import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_FILE = LOG_DIR / "decisions.jsonl"


def _ensure_dir():
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def log_decision(agent: str, action: str, details: dict, result: dict):
    _ensure_dir()
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": agent,
        "action": action,
        "details": details,
        "result": result,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_logs():
    _ensure_dir()
    if not LOG_FILE.exists():
        return []
    entries = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return entries


def clear_logs():
    _ensure_dir()
    if LOG_FILE.exists():
        LOG_FILE.unlink()
