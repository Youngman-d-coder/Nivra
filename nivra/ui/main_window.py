from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPlainTextEdit
from PySide6.QtGui import QTextCursor
from nivra.core.command_engine import CommandEngine
from nivra.core.command_result import CommandResult
from nivra.services.trail_service import TrailService



class MainWindow(QMainWindow):
    def __init__(self, engine: CommandEngine, trail: TrailService) -> None:
        super().__init__()

        self.engine = engine
        self._trail = trail

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

        self.engine.stdout_updated.connect(self._handle_stdout)
        self.engine.stderr_updated.connect(self._handle_stderr)
        self.engine.command_finished.connect(self._handle_command_finished)
        self.engine.process_failed.connect(self._handle_process_failed)


    def _submit_command(self) -> None:
        command = self.pulse.text()
        clean_command = command.strip()
        if clean_command:
            self._trail.add(clean_command)
            self.engine.execute(clean_command)
            self.label.setText(f"Command submitted: {clean_command}")
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