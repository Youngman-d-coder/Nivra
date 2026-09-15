from pathlib import Path

from PySide6.QtWidgets import QApplication
from nivra.core.command_engine import CommandEngine
from nivra.core.command_result import CommandResult
from nivra.ui.main_window import MainWindow
from nivra.services.logging_service import LoggingService
from nivra.services.trail_service import TrailService
from nivra.services.haven_service import HavenService
from nivra.ui.themes.theme_manager import ThemeManager
from nivra.ui.themes.qss_renderer import build_stylesheet


def main() -> None:
    logging_service = LoggingService("logs/nivra.log")
    trail_service = TrailService("data/trail.json")

    app = QApplication([])

    theme_manager = ThemeManager()
    theme = theme_manager.load_builtin_theme("nivra_glass")
    stylesheet = build_stylesheet(theme)
    app.setStyleSheet(stylesheet)

    engine = CommandEngine()
    haven_service = HavenService(Path.cwd())
    window = MainWindow(engine, trail_service, haven_service)


    engine.command_finished.connect(lambda result: on_command_finished(result, logging_service))
    engine.process_failed.connect(lambda error_message: on_process_failed(error_message, logging_service))

    window.show()
    app.exec()


def on_command_finished(result: CommandResult, logger: LoggingService) -> None:
    logger.info(f"command finished | {format_command_result(result)}")

def on_process_failed(error_message: str, logger: LoggingService) -> None:
    logger.error(f"process failed | error_message={error_message}")

def format_command_result(result: CommandResult) -> str:
    return f"command={result.command} | duration={result.duration:.2f}s | exit_code={result.exit_code} | success={result.success}"


if __name__ == "__main__":
    main()
