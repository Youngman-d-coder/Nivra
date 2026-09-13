from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPlainTextEdit
from PySide6.QtCore import Qt, QEvent, QObject
from PySide6.QtGui import QTextCursor
from nivra.core.command_engine import CommandEngine
from nivra.core.command_result import CommandResult
from nivra.services.trail_service import TrailService
from nivra.services.haven_service import HavenService



class MainWindow(QMainWindow):
    def __init__(self, engine: CommandEngine, trail: TrailService, haven: HavenService) -> None:
        super().__init__()

        self.engine = engine
        self._trail = trail
        self._haven = haven
        self._history_draft = ""

        self._history_index = len(self._trail.history)

        self.setWindowTitle("Nivra")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.label = QLabel("Welcome to Nivra!")
        self.main_layout.addWidget(self.label)
    
        self.output = QPlainTextEdit()
        self.output.setPlaceholderText("Output will appear here...")
        self.output.setReadOnly(True)
        self.main_layout.addWidget(self.output)

        self.pulse = QLineEdit()
        self.pulse.setPlaceholderText("Enter a command...")
        self.main_layout.addWidget(self.pulse)
        self.pulse.returnPressed.connect(self._submit_command)
        self.pulse.installEventFilter(self)

        self.engine.stdout_updated.connect(self._handle_stdout)
        self.engine.stderr_updated.connect(self._handle_stderr)
        self.engine.command_finished.connect(self._handle_command_finished)
        self.engine.process_failed.connect(self._handle_process_failed)


    def _submit_command(self) -> None:
        command = self.pulse.text()
        clean_command = command.strip()
        if clean_command:
            self._trail.add(clean_command)
            self._history_index = len(self._trail.history)
            self.engine.execute(clean_command, self._haven.workspace)
            self.label.setText(f"Command submitted: {clean_command}")
            self._history_draft = ""
            self.pulse.clear()

    def _handle_stdout(self, output: str) -> None:
        self.output.appendPlainText(output)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def _handle_stderr(self, error: str) -> None:
        self.output.appendPlainText(error)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def _handle_command_finished(self, result: CommandResult) -> None:
        self.output.appendPlainText(f"Command finished | exit code: {result.exit_code} | Success: {result.success}")
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def _handle_process_failed(self, error: str) -> None:
        self.output.appendPlainText(f"Process failed: {error}")
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched == self.pulse and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Up:
                if self._history_index > 0:
                    if self._history_index == len(self._trail.history):
                        self._history_draft = self.pulse.text()
                    self._history_index -= 1
                    self.pulse.setText(self._trail.history[self._history_index])
                return True
            elif event.key() == Qt.Key.Key_Down:
                if self._history_index < len(self._trail.history):
                    self._history_index += 1
                    if self._history_index == len(self._trail.history):
                        self.pulse.setText(self._history_draft)
                    else:
                        self.pulse.setText(self._trail.history[self._history_index])
                return True

        return super().eventFilter(watched, event)