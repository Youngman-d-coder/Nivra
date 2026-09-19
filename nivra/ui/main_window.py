from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPlainTextEdit, QPushButton, QFileDialog, QFileSystemModel, QTreeView, QSplitter, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QEvent, QObject, QModelIndex
from PySide6.QtGui import QTextCursor, QColor
from nivra.core.command_engine import CommandEngine
from nivra.core.command_result import CommandResult
from nivra.services.trail_service import TrailService
from nivra.services.haven_service import HavenService



class MainWindow(QMainWindow):
    def __init__(
        self,
        engine: CommandEngine,
        trail: TrailService,
        haven: HavenService,
        theme: dict
    ) -> None:
        super().__init__()

        # ------------------------------------------------------------------
        # Dependencies and state
        # ------------------------------------------------------------------
        self.engine = engine
        self._trail = trail
        self._haven = haven
        self._theme = theme

        self._history_index = len(self._trail.history)
        self._history_draft = ""

        # ------------------------------------------------------------------
        # Window setup
        # ------------------------------------------------------------------
        self.setWindowTitle("Nivra")

        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.main_layout)

        # ------------------------------------------------------------------
        # Widget creation
        # ------------------------------------------------------------------
        self.workspace_label = QLabel()
        self.status_label = QLabel()

        self.workspace_button = QPushButton()
        self.clear_output_button = QPushButton()
        self.clear_trail_button = QPushButton()
        self.stop_button = QPushButton()

        self.file_model = QFileSystemModel()
        self.file_tree = QTreeView()
        self.file_preview = QPlainTextEdit()

        self.output = QPlainTextEdit()
        self.pulse = QLineEdit()

        self.haven_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)

        self.output_container = QWidget()

        self.output_layout = QVBoxLayout()
        self.output_header_layout = QHBoxLayout()

        self.output_label = QLabel()

        self.pulse_container = QWidget()
        self.pulse_layout = QVBoxLayout()
        self.pulse_header_layout = QHBoxLayout()
        self.pulse_label = QLabel()

        self.workspace_container = QWidget()
        self.workspace_header_layout = QHBoxLayout()
        self.workspace_info_layout = QVBoxLayout()

        # ------------------------------------------------------------------
        # Widget configuration
        # ------------------------------------------------------------------
        self.workspace_label.setText(
            f"Current Workspace: {self._haven.workspace}"
        )
        self.status_label.setText("Status: Ready")

        self.workspace_button.setText("Change Workspace")
        self.clear_output_button.setText("Clear Output")
        self.clear_trail_button.setText("Clear Trail")

        self.file_tree.setModel(self.file_model)

        self.file_tree.hideColumn(1)
        self.file_tree.hideColumn(2)
        self.file_tree.hideColumn(3)

        self.file_preview.setPlaceholderText(
            "Double-click a file to preview it..."
        )
        self.file_preview.setReadOnly(True)

        self.output.setPlaceholderText(
            "Output will appear here..."
        )
        self.output.setReadOnly(True)

        self.pulse.setPlaceholderText(
            "Enter a command..."
        )
        self.pulse.installEventFilter(self)

        self.haven_splitter.addWidget(self.file_tree)
        self.haven_splitter.addWidget(self.file_preview)
        self.main_splitter.addWidget(self.haven_splitter)
        self.main_splitter.addWidget(self.output_container)

        self.output_label.setText("Output")

        self.output_container.setLayout(self.output_layout)

        self.output_header_layout.addWidget(self.output_label)
        self.output_header_layout.addStretch()
        self.output_header_layout.addWidget(self.clear_output_button)

        self.output_layout.addLayout(self.output_header_layout)
        self.output_layout.addWidget(self.output)


        self.pulse_label.setText("Pulse")

        self.pulse_container.setLayout(self.pulse_layout)

        self.pulse_header_layout.addWidget(self.pulse_label)
        self.pulse_header_layout.addStretch()
        self.pulse_header_layout.addWidget(self.clear_trail_button)

        self.pulse_layout.addLayout(self.pulse_header_layout)
        self.pulse_layout.addWidget(self.pulse)
        self.pulse_layout.addWidget(self.stop_button)

        self.workspace_info_layout.addWidget(self.workspace_label)
        self.workspace_info_layout.addWidget(self.status_label)

        self.workspace_header_layout.addLayout(self.workspace_info_layout)
        self.workspace_header_layout.addStretch()
        self.workspace_header_layout.addWidget(self.workspace_button)

        self.workspace_container.setLayout(self.workspace_header_layout)
        self._pulse_glow = self._create_pulse_glow()
        self.pulse_container.setGraphicsEffect(
            self._pulse_glow
        )
        self.stop_button.setText("Stop")
        self.stop_button.setEnabled(False)


        # ------------------------------------------------------------------
        # Layout
        # ------------------------------------------------------------------
        self.main_layout.addWidget(self.workspace_container)
        self.main_layout.addWidget(self.main_splitter)

        self.main_layout.addWidget(self.pulse_container)

        # ------------------------------------------------------------------
        # UI signal connections
        # ------------------------------------------------------------------
        self.workspace_button.clicked.connect(
            self._change_workspace
        )

        self.file_tree.doubleClicked.connect(
            self._handle_file_double_click
        )

        self.clear_output_button.clicked.connect(
            self.output.clear
        )

        self.clear_trail_button.clicked.connect(
            self._clear_trail
        )

        self.pulse.returnPressed.connect(
            self._submit_command
        )

        self.stop_button.clicked.connect(self.engine.stop)

        # ------------------------------------------------------------------
        # CommandEngine signal connections
        # ------------------------------------------------------------------
        self.engine.stdout_updated.connect(
            self._handle_stdout
        )

        self.engine.stderr_updated.connect(
            self._handle_stderr
        )

        self.engine.command_finished.connect(
            self._handle_command_finished
        )

        self.engine.process_failed.connect(
            self._handle_process_failed
        )

        self.engine.command_cancelled.connect(
            self._handle_command_cancelled
        )

        # ------------------------------------------------------------------
        # Initial UI state
        # ------------------------------------------------------------------
        self.workspace_container.setObjectName("workspaceHeader")
        self.workspace_label.setObjectName("workspaceTitle")
        self.status_label.setObjectName("statusText")

        self.output_container.setObjectName("outputPanel")
        self.pulse_container.setObjectName("pulsePanel")
        self.output_label.setObjectName("panelTitle")
        self.pulse_label.setObjectName("panelTitle")

        self.haven_splitter.setSizes([300, 700])
        self.main_splitter.setSizes([300, 700])
        self._update_file_tree()


    def _create_pulse_glow(self) -> QGraphicsDropShadowEffect:
        colors = self._theme["colors"]
        depth = self._theme["depth"]

        glow_color = QColor(colors["accent"])
        glow_color.setAlpha(45)

        glow = QGraphicsDropShadowEffect(self)
        glow.setBlurRadius(depth["shadow_blur"])
        glow.setOffset(0, 0)
        glow.setColor(glow_color)

        return glow

    # ------------------------------------------------------------------
    # Pulse command submission
    # ------------------------------------------------------------------
    def _submit_command(self) -> None:
        """
        Submit the current Pulse command.

        Nivra handles its own built-in commands first. Every other
        command is passed to CommandEngine and therefore to the
        operating system's native shell.
        """
        command = self.pulse.text()
        clean_command = command.strip()

        if not clean_command:
            return

        self._trail.add(clean_command)
        self._history_index = len(self._trail.history)
        self._history_draft = ""

        self.pulse.clear()

        if self.output.toPlainText().strip():
            self.output.appendPlainText(
                "────────────────────────────────────"
            )

        self.output.appendPlainText(
            f">. {clean_command}"
        )
        self.output.moveCursor(
            QTextCursor.MoveOperation.End
        )

        if self._handle_builtin_command(clean_command):
            return

        self.status_label.setText(
            f"Status: Executing '{clean_command}'..."
        )

        self._set_busy(True)

        self.engine.execute(
            clean_command,
            self._haven.workspace
        )

    # ------------------------------------------------------------------
    # Nivra built-in commands
    # ------------------------------------------------------------------
    def _handle_builtin_command(
        self,
        command: str
    ) -> bool:
        """
        Handle commands that must change Nivra's own application state.

        Returns True when Nivra handled the command itself.
        Returns False when the command should be sent to CommandEngine.
        """
        clean_command = command.strip()
        lower_command = clean_command.lower()

        if lower_command in {"clear", "cls"}:
            self.output.clear()
            self.status_label.setText(
                "Status: Output cleared"
            )
            return True

        if (
            lower_command == "cd"
            or lower_command.startswith("cd ")
        ):
            raw_path = clean_command[2:].strip()

            if raw_path:
                raw_path = (
                    raw_path
                    .strip('"')
                    .strip("'")
                )

                target = Path(
                    raw_path
                ).expanduser()

                if not target.is_absolute():
                    target = (
                        self._haven.workspace
                        / target
                    )
            else:
                target = Path.home()

            try:
                self._haven.change_workspace(
                    target.resolve()
                )
            except (
                FileNotFoundError,
                NotADirectoryError,
                OSError
            ) as error:
                self.status_label.setText(
                    f"Status: {error}"
                )
                return True

            self.workspace_label.setText(
                f"Current Workspace: "
                f"{self._haven.workspace}"
            )

            self.file_preview.clear()
            self._update_file_tree()

            self.status_label.setText(
                f"Status: Workspace changed to "
                f"{self._haven.workspace}"
            )

            return True

        return False

    def _handle_command_cancelled(self) -> None:
        self.output.appendPlainText("■ Cancelled")
        self.status_label.setText("Status: Cancelled")
        self._set_busy(False)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def _update_file_tree(self) -> None:
        root_index = self.file_model.setRootPath(str(self._haven.workspace))
        self.file_tree.setRootIndex(root_index)

    def _set_busy(self, busy: bool) -> None:
        self.pulse.setEnabled(not busy)
        self.workspace_button.setEnabled(not busy)
        self.stop_button.setEnabled(busy)

        if not busy:
            self.pulse.setFocus()
        
    def _change_workspace(self) -> None:
        new_workspace = QFileDialog.getExistingDirectory(
            self,
            "Select Workspace Directory",
            str(self._haven.workspace)
        )

        if new_workspace:
            try:
                self._haven.change_workspace(new_workspace)

                self.workspace_label.setText(
                    f"Current Workspace: {self._haven.workspace}"
                )
                self.status_label.setText("Status: Workspace changed")

                self.file_preview.clear()
                self._update_file_tree()

            except (FileNotFoundError, NotADirectoryError) as e:
                self.status_label.setText(f"Status: {e}")

    def _clear_trail(self) -> None:
        self._trail.clear()
        self._history_index = len(self._trail.history)
        self._history_draft = ""
        self.status_label.setText("Status: Command history cleared")

    def _handle_file_double_click(self, index: QModelIndex) -> None:
        file_path = self.file_model.filePath(index)
        path_obj = Path(file_path)

        if self.file_model.isDir(index):
            self.file_preview.clear()
            self.status_label.setText(
                f"Status: Directory selected: {path_obj.name}"
            )
            return

        extension = path_obj.suffix.lower()

        supported_extensions = {
            ".py",
            ".txt",
            ".md",
            ".json",
            ".csv",
            ".toml",
            ".ini",
            ".cfg",
            ".yaml",
            ".yml",
            ".html",
            ".css",
            ".js",
            ".xml",
            ".c",
            ".cpp",
            ".h",
            ".hpp",
            ".java",
            ".sh",
            ".bat",
            ".rb",
            ".log",
            ".rst",
        }

        if extension not in supported_extensions:
            self.file_preview.setPlainText(
                f"Preview unavailable for '{extension or 'unknown'}' files."
            )
            self.status_label.setText(
                f"Status: Preview unavailable for {path_obj.name}"
            )
            return

        size = self.file_model.size(index)

        if size > 1 * 1024 * 1024:
            self.file_preview.setPlainText(
                "File is too large to preview."
            )
            self.status_label.setText(
                f"Status: {path_obj.name} is too large to preview"
            )
            return

        try:
            content = path_obj.read_text(encoding="utf-8")
            self.file_preview.setPlainText(content)

            status_text = (
                f"Status: Previewing {path_obj.name} | "
                f"Size: {size} bytes"
            )
            self.status_label.setText(status_text)

        except UnicodeDecodeError:
            self.file_preview.setPlainText(
                "This file could not be decoded as UTF-8 text."
            )
            self.status_label.setText(
                f"Status: Could not preview {path_obj.name}"
            )

        except OSError as e:
            self.file_preview.setPlainText(
                f"Error reading file: {e}"
            )
            self.status_label.setText(
                f"Status: Error reading {path_obj.name}"
            )

    def _handle_stdout(self, output: str) -> None:
        self.output.appendPlainText(output)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def _handle_stderr(self, error: str) -> None:
        self.output.appendPlainText(error)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def _handle_command_finished(self, result: CommandResult) -> None:
        if result.success:
            self.output.appendPlainText("✓ Finished")
            self.status_label.setText("Status: Finished")
        else:
            self.output.appendPlainText(
                f"✗ Failed (exit code {result.exit_code})"
            )
            self.status_label.setText(
                f"Status: Failed (exit code {result.exit_code})"
            )

        self._set_busy(False)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def _handle_process_failed(self, error: str) -> None:
        self.output.appendPlainText(f"Process failed: {error}")
        self.status_label.setText("Status: Process failed")
        self._set_busy(False)
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