# GitHub Copilot Instructions for churn-retention-platform-v2

## Purpose
This repository is a Python-based churn retention platform prototype. The goal is to help engineers explore, extend, and test churn modeling, feature engineering, and decision logic.

## Project structure
- `src/main.py` — entrypoint that reads processed data, enriches features, and builds user state.
- `src/data_processing/` — feature engineering utilities.
- `src/state_engine/` — user state construction, scoring, urgency, and CLTV logic.
- `src/decision_engine/`, `src/evaluation/`, `src/models/`, `src/simulation/` — domain components for downstream retention workflows.
- `data/processed/` and `data/raw/` — sample input and transformed dataset artifacts.
- `tests/` — currently empty; recommended place for unit and integration tests.

## Important details
- The repository currently uses a local virtual environment: `venv/`.
- The project is Python-based. Use the active venv before running commands.
- `requirements.txt` is present but encoded as UTF-16; open or convert it carefully if installing dependencies.
- `src/main.py` currently uses a hardcoded processed CSV path and a fixed `EXPECTED_EXTENSION` value.

## Recommended commands
- Activate the venv (PowerShell):
  - `venv\Scripts\Activate.ps1`
- Install dependencies:
  - `python -m pip install -r requirements.txt`
- Run the sample workflow:
  - `python src/main.py`

## How to contribute
- Keep changes isolated under `src/` and avoid modifying raw data files unless necessary.
- Add tests to `tests/` when introducing new logic or refactoring existing modules.
- Prefer clear, small refactors in feature engineering and state engine modules.

## Useful prompts for copilots
- "Refactor `src/main.py` to accept input file and expected extension via command-line arguments."
- "Add unit tests for `src/data_processing/feature_builder.py` covering missing values and duplicate records."
- "Document the role of `src/state_engine/user_state_builder.py` and propose a small improvement for state construction."

## Notes for future agent customization
- A follow-up custom instruction could target `src/data_processing/` and `src/state_engine/` work specifically.
- Another useful customization is a test-focused agent for adding coverage and structuring `tests/`.