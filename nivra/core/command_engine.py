# ------------------------------------------------------------------------
# Nivra Command Engine
# ------------------------------------------------------------------------
# Responsibilities:
#   - Execute commands asynchronously with QProcess.
#   - Select the native shell for Windows, Linux, and macOS.
#   - Stream stdout/stderr back to the UI.
#   - Track command duration and exit status.
#   - Support graceful cancellation with a force-kill fallback.
#
# Important:
#   CommandEngine does NOT manage Haven, Trail, or UI widgets.
#   Those responsibilities stay outside the engine.
# ------------------------------------------------------------------------

import platform
import shutil
import time
from pathlib import Path

from PySide6.QtCore import QObject, QProcess, Signal, QTimer

from nivra.core.command_result import CommandResult


class CommandEngine(QObject):
    """Run commands asynchronously through the host operating system's shell."""

    stdout_updated = Signal(str)
    stderr_updated = Signal(str)
    process_failed = Signal(str)
    command_finished = Signal(object)
    command_cancelled = Signal()

    def __init__(self) -> None:
        super().__init__()

        self._process = QProcess(self)

        self._stdout: str = ""
        self._stderr: str = ""
        self._start_time: float | None = None
        self._current_command: str | None = None
        self._cancel_requested: bool = False

        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.timeout.connect(
            self._force_kill_if_running
        )

        self._process.readyReadStandardOutput.connect(
            self._read_stdout
        )
        self._process.readyReadStandardError.connect(
            self._read_stderr
        )
        self._process.errorOccurred.connect(
            self._process_error
        )
        self._process.finished.connect(
            self._process_finished
        )

    # ------------------------------------------------------------------
    # Process output
    # ------------------------------------------------------------------
    def _read_stdout(self) -> None:
        """Read newly available standard output and forward it to the UI."""
        data = self._process.readAllStandardOutput()
        text = bytes(data).decode(
            "utf-8",
            errors="replace"
        )

        self._stdout += text
        self.stdout_updated.emit(text)

    def _read_stderr(self) -> None:
        """Read newly available standard error and forward it to the UI."""
        data = self._process.readAllStandardError()
        text = bytes(data).decode(
            "utf-8",
            errors="replace"
        )

        self._stderr += text
        self.stderr_updated.emit(text)

    # ------------------------------------------------------------------
    # Process lifecycle
    # ------------------------------------------------------------------
    def _process_finished(
        self,
        exit_code: int,
        _exit_status: QProcess.ExitStatus
    ) -> None:
        """Create a CommandResult or report a user-requested cancellation."""
        self._kill_timer.stop()

        if self._cancel_requested:
            self._reset_state()
            self._cancel_requested = False

            self.command_cancelled.emit()
            return

        if self._start_time is None:
            return

        if self._current_command is None:
            return

        duration = time.perf_counter() - self._start_time

        result = CommandResult(
            command=self._current_command,
            stdout=self._stdout,
            stderr=self._stderr,
            duration=duration,
            exit_code=exit_code
        )

        self._reset_state()
        self.command_finished.emit(result)

    def _process_error(
        self,
        error: QProcess.ProcessError
    ) -> None:
        """Handle genuine process errors without misreporting cancellation."""
        if (
            self._cancel_requested
            and error == QProcess.ProcessError.Crashed
        ):
            return

        error_message = self._process.errorString()

        if error == QProcess.ProcessError.FailedToStart:
            self._kill_timer.stop()
            self._reset_state()

        self.process_failed.emit(error_message)

    def _reset_state(self) -> None:
        """Clear data associated with the completed/failed command."""
        self._stdout = ""
        self._stderr = ""
        self._start_time = None
        self._current_command = None

    # ------------------------------------------------------------------
    # Cancellation
    # ------------------------------------------------------------------
    def stop(self) -> None:
        """Request that the currently running command stop."""
        if (
            self._process.state()
            == QProcess.ProcessState.NotRunning
        ):
            return

        self._cancel_requested = True

        self._process.terminate()
        self._kill_timer.start(1500)

    def _force_kill_if_running(self) -> None:
        """Force-kill a command that ignored the graceful stop request."""
        if (
            self._process.state()
            != QProcess.ProcessState.NotRunning
        ):
            self._process.kill()

    # ------------------------------------------------------------------
    # Public command execution
    # ------------------------------------------------------------------
    def execute(
        self,
        command: str,
        working_directory: Path | None = None
    ) -> None:
        """Execute a command through the host OS shell."""
        if (
            self._process.state()
            != QProcess.ProcessState.NotRunning
        ):
            return

        if not command.strip():
            return

        self._cancel_requested = False

        self._stdout = ""
        self._stderr = ""
        self._current_command = command
        self._start_time = time.perf_counter()

        if working_directory is not None:
            self._process.setWorkingDirectory(
                str(working_directory)
            )
        else:
            self._process.setWorkingDirectory("")

        try:
            shell, arguments = self._build_shell_command(
                command
            )
        except RuntimeError as error:
            self._reset_state()
            self.process_failed.emit(str(error))
            return

        self._process.start(
            shell,
            arguments
        )

    # ------------------------------------------------------------------
    # Operating-system shell selection
    # ------------------------------------------------------------------
    def _build_shell_command(
        self,
        command: str
    ) -> tuple[str, list[str]]:
        """
        Return the shell executable and arguments needed to run a command.

        Windows:
            PowerShell 7 (pwsh) when available, otherwise Windows PowerShell.

        macOS:
            zsh when available, otherwise sh.

        Linux:
            bash when available, otherwise sh.
        """
        system = platform.system()

        if system == "Windows":
            shell = (
                shutil.which("pwsh")
                or shutil.which("powershell")
            )

            if shell is None:
                raise RuntimeError(
                    "PowerShell could not be found."
                )

            return shell, [
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                command
            ]

        if system == "Darwin":
            shell = (
                shutil.which("zsh")
                or shutil.which("sh")
            )

            if shell is None:
                raise RuntimeError(
                    "No supported shell could be found."
                )

            return shell, [
                "-lc",
                command
            ]

        if system == "Linux":
            shell = (
                shutil.which("bash")
                or shutil.which("sh")
            )

            if shell is None:
                raise RuntimeError(
                    "No supported shell could be found."
                )

            return shell, [
                "-lc",
                command
            ]

        raise RuntimeError(
            f"Unsupported operating system: {system}"
        )
