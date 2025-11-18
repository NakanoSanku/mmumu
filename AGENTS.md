# Repository Guidelines

This document describes how to work on `mmumu` consistently and safely.

## Project Structure & Module Organization

- `src/mmumu/base.py` – registry lookup and dataclasses for MuMu installation and player metadata.
- `src/mmumu/manger.py` – wrapper around the MuMu manager executable for creating and controlling players.
- `src/mmumu/api.py` – `ctypes` bindings to the MuMu SDK DLL for low-level input and display APIs.
- Add new modules under `src/mmumu/` and expose stable public APIs via `mmumu/__init__.py` when appropriate.

## Build, Test, and Development Commands

- Create a virtualenv and install locally: `python -m venv .venv && .venv\Scripts\activate && python -m pip install -e .`.
- Build a distributable wheel for release: `python -m pip install build && python -m build`.
- Run the test suite from the repo root with `pytest` once tests are added.

## Coding Style & Naming Conventions

- Use Python 3.9+ syntax with type hints and 4-space indentation; keep lines reasonably short (~100 chars).
- Modules and functions use `snake_case`; classes use `PascalCase`; keep Windows-specific logic isolated in helpers like `base.py`.
- Prefer dataclasses for simple data containers and keep public APIs small and explicit.

## Testing Guidelines

- Use `pytest` with tests under `tests/`, mirroring the package layout (for example, `tests/test_manger.py`).
- Name test files and functions `test_*` and cover both success paths and failure cases (e.g., missing registry keys, invalid DLL paths).
- Aim for meaningful coverage of new behavior; run `pytest` (and optionally `pytest --cov=mmumu`) before opening a pull request.

## Commit & Pull Request Guidelines

- Write clear, descriptive commit messages in the present tense (for example, `Update MuMu 5.0 registry path`), referencing related issues with `(#123)` when relevant.
- For pull requests, include a short summary, rationale, any user-facing behavior changes, and notes about required environment (Windows version, MuMu version).
- Ensure tests pass locally, update `README.md` for new public APIs, and keep changes focused and small where possible.

## MuMu & Environment Notes

- This project targets Windows and assumes a local MuMu installation; `get_mumu_path` reads from the `SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\MuMuPlayer` registry key.
- When changing paths, registry access, or DLL loading behavior, maintain backward compatibility where possible and clearly document breaking changes.

