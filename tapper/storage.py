import json
from pathlib import Path

from .logic import GameState

SAVE_PATH = Path("tapper_save.json")


def save(state: GameState, path: Path = SAVE_PATH) -> None:
    path.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def load(path: Path = SAVE_PATH) -> GameState:
    """Загружает сохранение; если файла нет или он повреждён — новая игра."""
    if not path.exists():
        return GameState()
    try:
        return GameState.from_dict(json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, ValueError, TypeError):
        return GameState()
