# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install in development mode with dev deps (from repo root)
uv sync
# or with pip (>= 25.1, which supports dependency groups):
pip install -e . --group dev

# Run all tests
pytest

# Run a single test file
pytest tests/test_bader_ofer.py

# Run a single test
pytest tests/test_bader_ofer.py::test_name

# Run simulations for all new (pending) polls
seker run

# Run a specific poll (overrides existing output)
seker run --election 25th-Knesset-2022 --poll 2022-10-27-kan11

# Regenerate HTML visualizations (all existing outputs, or a specific poll)
seker viz
seker viz --election 25th-Knesset-2022 --poll 2022-10-27-kan11
```

## Architecture

This is a Monte Carlo simulator for Israeli election polls. It models seat allocation uncertainty using the Bader-Ofer method (used in actual Israeli elections).

**Data flow:**
1. Input: `/data/<election>/parties.json` + `/data/<election>/polls/<poll>.json`
2. Simulation: Dirichlet-sampled vote fractions → `bader_ofer.allocate_seats()` × 100,000 iterations
3. Output: `/output/<election>/<poll>/stats.json` + `seat_counts.csv` + `visualization.html`

**Module responsibilities:**
- `bader_ofer.py` — Pure seat allocation logic implementing the Bader-Ofer method (quota + surplus agreements)
- `simulation.py` — Runs 100k Dirichlet-sampled iterations, calls `allocate_seats` per iteration
- `stats.py` — Aggregates simulation results into mean, CI bounds, threshold probability
- `visualization.py` — Builds a self-contained Hebrew (RTL) `visualization.html` per poll by injecting a JSON payload into `templates/visualization.html` (vanilla JS + inline SVG)
- `io.py` — File I/O: loading parties/polls, writing outputs, discovering pending polls
- `cli.py` — Entry point (`seker run`); resolves paths relative to project root (3 levels up from `cli.py`)

**Key data formats:**
- Poll JSON: `{ "sample_size": int, "results": { "<Hebrew symbol>": float, ... } }` — fractions (not percentages)
- `parties.json`: contains party name mapping + `surplus_agreements` list of `[symbol, symbol]` pairs
- `seat_counts.csv`: rows = parties, columns = `0_seats` through `120_seats`

**Important constants** (in `bader_ofer.py`/`simulation.py`):
- 120 total Knesset seats
- 3.25% electoral threshold
- Simulation uses `SCALE = 10_000_000` to convert fractions to integer vote counts
- Default seed: 42
