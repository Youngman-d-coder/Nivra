# Nivra

#### Video Demo: [Add your CS50 demo video URL here]

## Description

Nivra is a beginner-friendly visual developer shell built with Python and PySide6. It was created as my CS50P final project and grew from a simple command runner into a modular desktop environment for working with commands, files, workspaces, and command history from one interface.

The goal of Nivra is not to replace a full IDE or operating-system terminal. Instead, it provides a more approachable visual layer around common command-line workflows. Traditional terminals can be intimidating to new developers because they provide very little visual guidance. Nivra combines command execution with workspace navigation, file preview, persistent history, clear status feedback, and a themed graphical interface.

Nivra currently includes four main user-facing ideas:

- **Pulse** — the command input area.
- **Haven** — the active workspace and file browser.
- **Trail** — persistent command history.
- **Output** — live command output, errors, and completion state.

The application also includes a theme system, logging, command cancellation, and a modular structure intended to make future features easier to add without turning the application into one large file.

## Features

### Pulse

Pulse is Nivra's command-entry system. Commands are entered in a `QLineEdit` and executed asynchronously using Qt's `QProcess`.

Because the process runs asynchronously, the graphical interface remains responsive while a command is running. Standard output and standard error are streamed into the Output area as they become available.

While a command is running, Pulse is temporarily disabled and a **Stop** button becomes available. Nivra first attempts to terminate the process normally. If the process does not stop within the fallback period, it is forcefully killed. A user-requested stop is reported as **Cancelled** rather than being treated as an application error.

### Trail

Trail stores command history between Nivra sessions.

Commands are written to a JSON file and restored when the application starts. Blank commands are ignored and consecutive duplicate commands are not stored.

The Up and Down arrow keys can be used to move through previous commands. Nivra also preserves unfinished text typed into Pulse before history navigation begins, allowing the user to return to that draft after reaching the newest history entry.

Trail can be cleared directly from the interface.

### Haven

Haven represents the user's current working directory.

The user can select another directory using the **Change Workspace** button. Commands executed through Pulse run inside the selected Haven workspace.

Haven includes a file-system tree and a read-only preview panel. Double-clicking a supported text file displays its content inside Nivra. The preview system intentionally limits file types and file size so that unsupported, binary, or very large files do not accidentally freeze or overwhelm the application.

Supported preview formats currently include common source-code, configuration, documentation, and text formats such as Python, C, C++, JavaScript, JSON, Markdown, YAML, HTML, CSS, CSV, TOML, shell scripts, logs, and plain text.

### Output

The Output panel displays live standard output, standard error, command separators, completion state, failure state, and cancellation state.

The output panel is read-only and can be cleared with the **Clear Output** button.

### Nivra Glass

Nivra uses a JSON-driven theme system. The default built-in theme is **Nivra Glass**.

The theme defines reusable design tokens such as application background, surfaces, text colours, accent colours, border colours, corner radius, spacing, motion timing, and depth values.

`ThemeManager` loads and validates theme data, while `qss_renderer.py` converts the validated theme into a Qt stylesheet.

Keeping theme data outside the UI code was an intentional design decision. It prevents visual values from being scattered throughout the application and creates a foundation for future user-created themes.

## Project Structure

```text
Nivra/
├── project.py
├── test_project.py
├── requirements.txt
├── README.md
├── data/
│   └── trail.json
├── logs/
│   └── nivra.log
└── nivra/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   ├── command_engine.py
    │   └── command_result.py
    ├── services/
    │   ├── __init__.py
    │   ├── haven_service.py
    │   ├── logging_service.py
    │   └── trail_service.py
    └── ui/
        ├── __init__.py
        ├── main_window.py
        └── themes/
            ├── __init__.py
            ├── theme_manager.py
            ├── qss_renderer.py
            └── builtin/
                ├── __init__.py
                └── nivra_glass.json
```

## Important Files

### `project.py`

`project.py` is the application entry point and composition root.

It creates the services used by the program, starts `QApplication`, loads the active theme, builds the stylesheet, creates the command engine and workspace service, and finally creates the main window.

It also contains top-level helper functions used for command-result formatting and logging.

### `command_engine.py`

`CommandEngine` is responsible for running commands.

It uses `QProcess` rather than Python's blocking subprocess APIs because blocking the main thread would freeze the GUI. It emits Qt signals when output arrives, when an error occurs, when a command finishes, or when a user cancels a command.

The engine deliberately does not know about Trail, Haven, logging, or the GUI. This keeps command execution independent from presentation.

### `command_result.py`

`CommandResult` represents the result of a completed command.

It stores the command, stdout, stderr, duration, and exit code. Its `success` property reports whether the exit code was zero.

### `trail_service.py`

`TrailService` manages persistent command history.

It loads history from JSON, validates the loaded data, saves new commands, prevents consecutive duplicates, and exposes a copy of the current history.

### `haven_service.py`

`HavenService` manages the active workspace.

It validates that a requested workspace exists and is a directory before allowing Nivra to use it.

### `logging_service.py`

`LoggingService` writes application metadata to a rotating log file.

Nivra logs command completion and process failures, but does not automatically dump command stdout and stderr into the log. This avoids unnecessarily recording everything the user runs.

### `main_window.py`

`MainWindow` coordinates presentation and interaction.

It builds the workspace header, Haven file browser, preview panel, Output panel, Pulse controls, history navigation, command status updates, and Qt signal connections.

Although the file is currently the largest UI module, the rest of the application's responsibilities remain separated into core and service modules.

### Theme Files

`theme_manager.py` loads and validates themes.

`qss_renderer.py` converts theme tokens into Qt stylesheet rules.

`nivra_glass.json` contains the built-in Nivra Glass design tokens.

## Installation

Python 3 is required.

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The current requirements are:

```text
PySide6
pytest
```

## Running Nivra

From the project directory:

```powershell
python project.py
```

Nivra opens with the directory from which it was launched as the initial Haven workspace.

Use **Change Workspace** to select another directory.

Enter a command in Pulse and press Enter.

## Running the Tests

Run:

```powershell
pytest
```

The current automated tests cover the top-level functions required by the CS50P project specification, including command-result formatting and logging behaviour.

## Design Decisions

One of the most important design decisions in Nivra was to keep the command engine independent from the UI and other services.

`CommandEngine` does not import Trail, Haven, or LoggingService. Instead, signals are emitted and the application coordinates the appropriate response.

This makes the system easier to reason about and reduces coupling between modules.

Another important decision was using `QProcess` instead of a blocking command-execution method. A GUI application must keep its event loop responsive, so asynchronous execution was necessary.

The theme system was also separated into three responsibilities:

1. theme data in JSON,
2. validation and loading in `ThemeManager`,
3. stylesheet generation in `qss_renderer.py`.

This allows the visual system to evolve without mixing theme logic directly into `MainWindow`.

## Current Limitations

Nivra v0.1 intentionally focuses on a small, working core.

Some current limitations include:

- file preview is read-only,
- not every file type can be previewed,
- user-created themes do not yet have a graphical editor,
- shell behaviour may differ between operating systems,
- Nivra has primarily been developed and tested on Windows,
- the current UI is designed for desktop use,
- advanced terminal emulation is outside the scope of this version.

Nivra is not intended to fully emulate a terminal such as PowerShell, Bash, or Windows Terminal. It provides a visual interface for executing commands rather than implementing an entire terminal emulator.

## Future Development

The architecture leaves room for several future modules.

Planned ideas include:

- **Navigator** — an action and command palette,
- **Canvas** — theme creation and customisation,
- **Guide Mode** — additional help for beginners,
- **Focus Mode** — a more minimal workspace,
- **Lumen** — optional AI-assisted development features,
- **Chronos** — visual version-control tooling,
- **Thread** — a future Nivra scripting system.

These features are intentionally outside the scope of the CS50P v0.1 release. The goal of this version is to provide a reliable foundation before adding larger systems.

## Conclusion

Nivra began as an idea for making terminal-based development more approachable and became an exploration of GUI programming, asynchronous processes, persistence, modular architecture, file-system interaction, theming, and application state.

Building Nivra required combining many concepts from CS50P while also learning PySide6 and Qt-specific concepts such as signals, slots, `QProcess`, layouts, models, widgets, and graphics effects.

The current version is a functional first release: commands can be executed and stopped, output is streamed live, workspaces can be explored, text files can be previewed, command history persists between sessions, and the interface is controlled by a reusable theme system.
