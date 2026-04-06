import json
from pathlib import Path
from typing import Any


def ensure_parent_dir(file_path: str) -> None:
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)


def write_json(file_path: str, payload: Any) -> None:
    ensure_parent_dir(file_path)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def read_json(file_path: str, default: Any = None) -> Any:
    path = Path(file_path)
    if not path.exists():
        return default
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
