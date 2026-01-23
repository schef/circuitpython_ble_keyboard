# AGENTS.md

This repository contains CircuitPython code for a BLE keyboard running on
an nRF52840 board. This file is written for agentic coding tools so they can
work in the repo without guessing conventions.

There are no Cursor rules in `.cursor/rules/` or `.cursorrules`, and no
GitHub Copilot instructions in `.github/copilot-instructions.md`.

## Repository layout
- `src/`: CircuitPython application code that runs on the device.
- `make.py`: CLI helper for syncing code to the board and opening a REPL.
- `segger_client.py`: RTT helper for J-Link debugging.
- `README.md`: Hardware flash/build notes for bootloader/firmware.

Runtime flow:
- `src/code.py` is the entrypoint that calls `runner.run()`.
- `src/boot.py` configures USB behavior before CircuitPython starts.
- `src/runner.py` wires async tasks for buttons, LEDs, and BLE logic.
- `src/common.py` hosts shared helpers for GPIO, timing, and async loops.

## Build, lint, and test commands
There is no lint/test runner configured in this repo. Most work is verified
by deploying to hardware and watching logs over the REPL/RTT.

Common commands (run from repo root):
- Sync CircuitPython files to the mounted device:
  - `python make.py sync`
- Remove all files from the device mount:
  - `python make.py rm_all`
- Open a serial REPL with the device:
  - `python make.py repl`
- Start the J-Link RTT client:
  - `python make.py segger`

Single test or targeted test:
- No automated tests exist. When adding tests, document the runner and
  the single-test invocation in this section.

Manual verification checklist:
- Connect over serial REPL (`python make.py repl`) and confirm boot logs.
- Press buttons and verify LED toggles plus BLE keycodes.
- Disconnect/reconnect BLE and verify advertising restarts.

Firmware/bootloader build notes from `README.md`:
- Build custom bootloader (external repo):
  - `git clone https://github.com/adafruit/Adafruit_nRF52_Bootloader`
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install intelhex`
  - `git submodule update --init --recursive`
  - `make BOARD=pca10056 clean`
  - `make BOARD=pca10056 sd`
  - `make BOARD=pca10056 flash`
- Build custom CircuitPython firmware (external repo):
  - `git clone https://github.com/adafruit/circuitpython`
  - `python -m venv .venv && source .venv/bin/activate`
  - `make -C mpy-cross`
  - `cd ports/nordic && make BOARD=pca10056 clean`
  - `cd ports/nordic && make BOARD=pca10056 flash`

Library install notes (host machine):
- `pip3 install circup`
- `circup install asyncio adafruit_ble adafruit_bus_device adafruit_hid neopixel simpleio`

## Code style and conventions
Follow the existing style in `src/` and keep things simple for
CircuitPython constraints.

Formatting and layout:
- Use 4 spaces for indentation.
- Keep line lengths reasonable (prefer under ~100 chars).
- Use blank lines between top-level definitions.
- Avoid heavy formatting tools; match the existing hand-formatted style.
- Keep functions short and focused; avoid deep nesting in polling loops.

Imports:
- Prefer grouping standard library, CircuitPython/third-party, then local
  modules, but do not reorder existing files unless touching them.
- Use absolute imports for local modules (e.g., `import common`).
- Avoid `from x import *`; keep imports explicit.

Naming:
- Modules, functions, and variables use `snake_case`.
- Classes use `CamelCase` (`Button`, `Led`, `Pin`).
- Constants use `UPPER_SNAKE_CASE` when they are intended to be fixed values.
- Keep log tags consistent (e.g., `[RUNNER]`, `[LOGIC]`, `[BUTTONS]`).

Types:
- Type hints are used sparingly; use them when they improve clarity.
- Prefer simple hints (`bool | None`, class return types) rather than complex
  generics, to keep CircuitPython compatibility.
- Avoid `typing` features not supported by CircuitPython.

Error handling:
- The existing code uses early exits with `sys.exit(1)` for host scripts.
- On-device code generally logs and keeps running; avoid raising unless
  unrecoverable.
- Check for `None` before dereferencing returned objects (see `get_*_by_name`).

Logging:
- Use `print()` with bracketed component tags for debugging.
- Keep log messages short and structured; avoid large multiline dumps.
- Prefer single-line status updates inside loops to avoid noisy spam.
- Avoid heavy f-string formatting in tight loops.

Async patterns:
- `common.loop_async()` drives periodic work; keep sleeps short
  (typically `await asyncio.sleep(0.01)`).
- Do not block in async loops; keep hardware polling lightweight.

Hardware abstraction:
- Define pins in `src/common_pins.py` using the `Pin` class.
- Access GPIO via `common.create_input()` / `common.create_output()` helpers.
- Keep hardware objects (`ble`, `advertisement`, `k`) as module-level globals
  when they need to be shared across tasks.
- Use `active_high` consistently and invert signals in the helper classes.

State management:
- Store hardware objects at module scope to avoid reallocation.
- Keep lists of `Button`/`Led` instances and fetch by name helpers.
- Guard callbacks with `if callback is not None` checks.

BLE/HID behavior:
- Reuse the `adafruit_ble` stack and `HIDService` setup in `src/logic.py`.
- Ensure advertising restarts on disconnect (`ble.start_advertising`).
- Only send keycodes when `ble.connected` is true.

Memory/performance:
- Avoid allocating new objects in polling loops; reuse buffers/lists.
- Keep BLE or GPIO state in module-level globals to minimize churn.
- Prefer simple data structures over heavy abstractions.

CLI tool (`make.py`) conventions:
- Commands are implemented with `typer` and use synchronous helpers.
- If a command needs `sudo`, use `get_root_password()` and the interaction
  map in `run_bash_cmd()`.
- Default device settings live in the `options` dict at module scope.

Editing guidance:
- Keep changes minimal and consistent with existing patterns.
- Avoid introducing new dependencies unless necessary for CircuitPython.
- When adding new modules, place them in `src/` and sync to the device
  with `python make.py sync`.
- Update `README.md` when adding new hardware or flashing procedures.

## Operational notes for agents
- The repo does not include automated tests; validation is manual on device.
- Hardware flashing commands in `README.md` are destructive; do not run
  them unless explicitly requested by the user.
- When adding new instructions, update this file so future agents can
  follow the same workflow.
