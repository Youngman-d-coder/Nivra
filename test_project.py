from nivra.core.command_result import CommandResult
from project import format_command_result, on_command_finished, on_process_failed


class FakeLogger:
    def __init__(self) -> None:
        self.messages = []

    def info(self, message: str) -> None:
        self.messages.append(("INFO", message))

    def error(self, message: str) -> None:
        self.messages.append(("ERROR", message))


def test_format_command_result() -> None:
    result = CommandResult(
        command="test_command",
        stdout="Output text",
        stderr="Error text",
        duration=1.23,
        exit_code=0,
    )

    expected_output = (
        "command=test_command | "
        "duration=1.23s | "
        "exit_code=0 | "
        "success=True"
    )

    assert format_command_result(result) == expected_output


def test_format_command_result_failure() -> None:
    result = CommandResult(
        command="bad_command",
        stdout="",
        stderr="Command not found",
        duration=0.456,
        exit_code=1
    )

    expected_output = (
        "command=bad_command | "
        "duration=0.46s | "
        "exit_code=1 | "
        "success=False"
    )

    assert format_command_result(result) == expected_output


def test_on_command_finished() -> None:
    logger = FakeLogger()
    result = CommandResult(
        command="test_command",
        stdout="Output text",
        stderr="",
        duration=1.23,
        exit_code=0,
    )

    on_command_finished(result, logger)

    assert len(logger.messages) == 1
    assert logger.messages[0][0] == "INFO"
    assert "command finished" in logger.messages[0][1]
    assert "command=test_command" in logger.messages[0][1]


def test_on_process_failed() -> None:
    logger = FakeLogger()
    error_message = "Process failed due to an error."

    on_process_failed(error_message, logger)

    assert len(logger.messages) == 1
    assert logger.messages[0][0] == "ERROR"
    assert "process failed" in logger.messages[0][1]
    assert f"error_message={error_message}" in logger.messages[0][1]