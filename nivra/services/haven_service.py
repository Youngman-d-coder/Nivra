from pathlib import Path


class HavenService:
    def __init__(self, haven: Path | str) -> None:
        self._workspace = self._validate_workspace(haven)

    def change_workspace(self, haven: Path | str) -> None:
        self._workspace = self._validate_workspace(haven)

    @property
    def workspace(self) -> Path:
        return self._workspace

    def _validate_workspace(self, haven: Path | str) -> Path:
        candidate = Path(haven)

        if not candidate.exists():
            raise FileNotFoundError(f"Workspace path '{candidate}' does not exist.")
        if not candidate.is_dir():
            raise NotADirectoryError(f"Workspace path '{candidate}' is not a directory.")

        return candidate