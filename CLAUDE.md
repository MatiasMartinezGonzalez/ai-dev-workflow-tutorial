# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This repo is the working directory for an "AI-Assisted Development Workflow" tutorial (see `README.md`). The tutorial content itself (`pre-work-setup.md`, `workshop-build-deploy.md`, `codex-companion.md`, `capstone-tools.md`) is instructional material for the student, not part of the shipped application — don't treat edits there as feature work. The actual deliverable being built is a Streamlit sales dashboard: `app.py`, `calculations.py`, `charts.py`, and `tests/`.

## Commands

```bash
# Activate the virtual environment (created with `python -m venv venv`)
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py

# Run the full test suite
pytest -v

# Run one test file
pytest tests/test_calculations.py -v

# Run tests matching a name
pytest tests/test_calculations.py -k top_products -v
```

There is no build step, linter, or type-checker configured in this project — `pytest` is the only verification command.

## Architecture

Data flows one direction through three files:

```
app.py  →  calculations.py  →  charts.py
(load,     (pure aggregation   (Plotly figure
 render)    functions)          builders)
```

- **`calculations.py`** — pure functions only (`total_sales`, `total_orders`, `sales_by_month`, `sales_by_category`, `sales_by_region`, `top_products`). No Streamlit or file I/O imports. Each function takes the loaded DataFrame and returns a plain value (`float`/`int`/`Series`/`DataFrame`). This is the only module with unit tests (`tests/test_calculations.py`), because it has no I/O to mock — tests build small in-memory DataFrames and assert on exact values. Sorting for ranked outputs (category, region, top products) happens here, not in `charts.py`, so tests can assert order directly.
- **`charts.py`** — takes a `calculations.py` result and returns a `plotly.graph_objects.Figure`. Not unit tested; verified by running the app manually. The pattern for every builder: `reset_index()` the Series/DataFrame, rename columns, build the figure, then `fig.update_traces(hovertemplate=...)` for the interactive tooltip requirement.
- **`app.py`** — the Streamlit page. `load_data(path)` (module-level, imported by `tests/test_app.py`) reads the CSV, validates columns against `EXPECTED_COLUMNS`, and raises `FileNotFoundError`/`ValueError` on bad input. All page logic lives in `main()`, guarded by `if __name__ == "__main__":` — this is what keeps `load_data` importable and testable without triggering Streamlit calls at import time, while still behaving normally under `streamlit run app.py` (which executes the file as `__main__`). `main()` catches `load_data`'s exceptions and calls `st.error()` + `st.stop()` rather than letting a traceback reach the page — required for a missing CSV or a mismatched column set.

Currency/comma formatting (`$X,XXX,XXX`) happens in `app.py` at render time via f-strings or `st.column_config`, never in `calculations.py`, which stays numeric so it's simple to test and correct to sort.

## Conventions specific to this project

- **`TASKS.md` is the milestone board.** Tasks move through `To Do` → `In Progress` → `Done` sections (not checkboxes on a single list). Moving a task requires editing all three of: the acceptance-criteria checkboxes (`[ ]` → `[x]`), the `Commit:` line (the hash of the task's last code commit), and a `Notes:` line ("clean" or what changed/went wrong).
- **Every commit message includes the milestone ID** (e.g. `TASK-3: ...`), per the Definition of Done in `TASKS.md`.
- **The implementation plan and design doc** for the current build live in `docs/superpowers/plans/` and `docs/superpowers/specs/` — check there for the authoritative task breakdown, interfaces between tasks, and any documented rulings/deviations before assuming scope.
- **The Top 5 Products table** (`top_products` in `calculations.py`, rendered in `app.py`) is an intentional addition beyond the PRD's Phase 1 scope. It must stay labeled "Extra feature, personal brainstorming" in code comments/docstrings and in the UI caption — don't remove that labeling when touching this feature.
- **TASK-7 (deployment to Streamlit Community Cloud) is human-executed**, done from `main` after this branch is merged — it's not something to implement or automate from a feature branch.
- The PRD (`prd/ecommerce-analytics.md`) defines the source-of-truth acceptance numbers used throughout: 482 transaction records, ~$116,500 total sales, 5 categories, 4 regions.

## Lessons

Every `Notes:` line in `TASKS.md` through TASK-6 reads "clean" — no deviations, mistakes, or corrections have been recorded yet. There are no rules to extract from real experience so far. When a future task's `Notes:` line records something other than "clean," pull the rule it implies into this section so it isn't re-learned on the next pass.
