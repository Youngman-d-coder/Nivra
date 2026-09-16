# ------------------------------------------------------------------------
# Command Engine
# ------------------------------------------------------------------------

import time
from PySide6.QtCore import QObject, QProcess, Signal, QTimer
from pathlib import Path

from nivra.core.command_result import CommandResult


class CommandEngine(QObject):
    stdout_updated = Signal(str)
    stderr_updated = Signal(str)
    process_failed = Signal(str)
    command_finished = Signal(object)
    command_cancelled = Signal()


    def __init__(self) -> None:
        super().__init__()
        self._process: QProcess = QProcess(self)
        self._cancel_requested: bool = False
        self._stdout: str = ""
        self._stderr: str = ""
        self._start_time: float | None = None
        self._current_command: str | None = None

        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.timeout.connect(
            self._force_kill_if_running
        )

        self._process.readyReadStandardOutput.connect(self._read_stdout)
        self._process.readyReadStandardError.connect(self._read_stderr)
        self._process.errorOccurred.connect(self._process_error)
        self._process.finished.connect(self._process_finished)


    def _read_stdout(self) -> None:
        data = self._process.readAllStandardOutput()
        text = bytes(data).decode("utf-8", errors="replace")
        self._stdout += text
        self.stdout_updated.emit(text)

    def _read_stderr(self) -> None:
        data = self._process.readAllStandardError()
        text = bytes(data).decode("utf-8", errors="replace")
        self._stderr += text
        self.stderr_updated.emit(text)

    def _process_finished(self, exit_code: int, exit_status: QProcess.ExitStatus) -> None:
        self._kill_timer.stop()

        if self._cancel_requested:
            self._stdout = ""
            self._stderr = ""
            self._start_time = None
            self._current_command = None
            self._cancel_requested = False

            self.command_cancelled.emit()
            return
        finished_time = time.perf_counter()

        if self._start_time is None:
            return
        duration = finished_time - self._start_time

        if self._current_command is None:
            return

        result = CommandResult(
            command=self._current_command,
            stdout=self._stdout,
            stderr=self._stderr,
            duration=duration,
            exit_code=exit_code
        )

        self._stdout = ""
        self._stderr = ""
        self._start_time = None
        self._current_command = None

        self.command_finished.emit(result)

    def _process_error(self, error: QProcess.ProcessError) -> None:
        if (
            self._cancel_requested
            and error == QProcess.ProcessError.Crashed
        ):
            return

        error_message = self._process.errorString()

        if error == QProcess.ProcessError.FailedToStart:
            self._stdout = ""
            self._stderr = ""
            self._start_time = None
            self._current_command = None

        self.process_failed.emit(error_message)

    def _force_kill_if_running(self) -> None:
        if self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()

    def stop(self) -> None:
        if self._process.state() == QProcess.ProcessState.NotRunning:
            return

        self._cancel_requested = True
        self._process.terminate()
        self._kill_timer.start(1500)

    def execute(self, command: str, working_directory: Path | None = None) -> None:
        if self._process.state() is not QProcess.ProcessState.NotRunning:
            return

        if not command.strip():
            return
        
        self._stdout = ""
        self._stderr = ""
        self._current_command = command
        self._start_time = time.perf_counter()

        if working_directory is not None:
            self._process.setWorkingDirectory(str(working_directory))
        else:
            self._process.setWorkingDirectory("")

        self._process.startCommand(command)