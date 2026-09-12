from pathlib import Path
import json

class TrailService:
    def __init__(self, path: str) -> None:
        self._history_path = Path(path)
        self._history_path.parent.mkdir(parents=True, exist_ok=True)
        self._history: list[str] = []
        self._load()

    def _save(self) -> None:
        with self._history_path.open("w", encoding="utf-8") as f:
            json.dump(self._history, f, ensure_ascii=False, indent=4)

    def _load(self) -> None:
        try:
            if not self._history_path.exists():
                return
            
            history_data = json.loads(self._history_path.read_text(encoding="utf-8"))
            if isinstance(history_data, list) and all(isinstance(item, str) for item in history_data):
                self._history = history_data
        except (json.JSONDecodeError, OSError):
            self._history = []

    def add(self, command: str) -> None:
        clean_command = command.strip()

        if clean_command and (not self._history or self._history[-1] != clean_command):
            self._history.append(clean_command)
            self._save()

    def clear(self) -> None:
        self._history.clear()
        self._save()

    @property
    def history(self) -> list[str]:
        return self._history.copy()