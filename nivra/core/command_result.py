# -----------------------------------------------------------------------------
# Command Result
# -----------------------------------------------------------------------------


class CommandResult:
    def __init__(self, command: str, stdout: str, stderr: str, duration: float, exit_code: int) -> None:
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.duration = duration

    @property
    def success(self) -> bool:
        return self.exit_code == 0