# סקר כלשהו

**A Monte Carlo seat simulator for Israeli election polls.**

Media outlets usually report a poll as a list of fixed numbers: Party A gets 34 seats, Party B gets 28, Party C gets 11. Those numbers hide a lot of uncertainty. Polls have sampling error, and Israeli seat allocation is sensitive to small shifts near the 3.25% electoral threshold.

This project takes a single published poll and estimates, for each party:

- the **probability distribution** of its seat count (the chance of winning 0, 1, 2, … 120 seats),
- its **average** seat count,
- a **90% confidence interval** for its seat count,
- its **probability of passing the electoral threshold**.

Each poll also gets a self-contained Hebrew (RTL) HTML page that shows these results.

---

## How it works

A poll is a snapshot of a few hundred or a few thousand respondents, so the real vote shares could easily be a bit higher or lower than the published figures. The simulator makes that uncertainty explicit:

1. **Simulate many plausible outcomes.** Starting from the poll's figures, it generates 100,000 random variations of the vote shares. Each variation is the kind of result that could plausibly have produced this poll. The larger the poll's sample, the closer the variations stay to the published figures.
2. **Allocate seats for each one.** It turns every variation into 120 Knesset seats with the **Bader-Ofer method**, the same method used in real Israeli elections. That includes the 3.25% electoral threshold and surplus agreements between parties.
3. **Count the results.** It tallies how often each party ended up with each seat count. That gives each party's seat distribution, its average, its 90% range and its chance of passing the threshold.

The random seed is fixed, so running the same poll again gives the same results.

For the exact model and the full seat-allocation rules, see [`specs.md`](specs.md).

---

## Installation

Requires Python ≥ 3.11. The only runtime dependency is NumPy.

```bash
# With uv (recommended)
uv sync

# Or with pip (>= 25.1, which supports dependency groups)
pip install -e . --group dev
```

This installs the `seker` command-line tool.

---

## Usage

### Run simulations

```bash
# Simulate every poll that doesn't yet have an output folder
seker run

# Simulate (or re-simulate, overwriting the existing output) a specific poll
seker run --election 26th-Knesset-2026 --poll 2026-09-30-maariv

# Optional: change the number of iterations or the seed
seker run --election 26th-Knesset-2026 --poll 2026-09-30-maariv --iterations 200000 --seed 7
```

By default, `seker run` processes only **pending** polls: files in `data/<election>/polls/` that have no matching folder in `output/<election>/`. Pass `--election` and `--poll` together to force a re-run of one poll.

### Regenerate visualizations

`seker run` already writes the HTML page. Use `seker viz` to rebuild the pages without re-running the simulation, for example after you edit the template or party names:

```bash
seker viz                                   # all existing outputs
seker viz --election 26th-Knesset-2026      # all polls of one election
seker viz --election 26th-Knesset-2026 --poll 2026-09-30-maariv
```

You can also run the tool as a module with `python -m seker …`.

---

## Adding data

### A new election cycle

Create `data/<election-name>/parties.json`:

```json
{
  "parties": {
    "מחל": "הליכוד",
    "ט": "הציונות הדתית וזהות",
    "...": "..."
  },
  "surplus_agreements": [
    ["מחל", "ט"],
    ["עם", "ודם"]
  ]
}
```

- `parties` maps each party's Hebrew ballot symbol (1–4 letters) to its display name.
- `surplus_agreements` lists pairs of symbols. A pair is used only when both parties appear in the poll and both pass the threshold.

### A new poll

Add a JSON file to `data/<election-name>/polls/`. The file name (without `.json`) becomes the poll's ID, and the convention is `YYYY-MM-DD-<outlet>`:

```json
{
  "date": "2026-09-30",
  "media": "מעריב",
  "pollster": "לזר מחקרים",
  "sample_size": 610,
  "link": "https://…/Survey_4177.pdf",
  "results": {
    "דרך": 0.154,
    "מחל": 0.148,
    "רק": 0.113
  }
}
```

- `sample_size` and `results` are required. `date`, `media`, `pollster` and `link` are optional and appear only in the visualization.
- `results` values are **fractions of respondents** (`0.154` = 15.4%), not seat counts. They should sum to about 1.

Then run `seker run`.

---

## Output

Results go into `output/<election>/<poll>/`, which mirrors the `data/` layout:

| File | Contents |
|---|---|
| `stats.json` | Per party: `avg_seats`, `prob_pass_threshold`, `ci_lower`, `ci_upper` (5th and 95th percentiles) |
| `seat_counts.csv` | Frequency matrix. One row per party, columns `0_seats`, `1_seat`, `2_seats` … `120_seats`. Each cell is the number of iterations in which the party won that many seats. |
| `visualization.html` | A self-contained Hebrew (RTL) page with no external dependencies. Open it directly in a browser. |

Example `stats.json` entry:

```jsonc
// stats.json (excerpt)
"דרך": {
  "avg_seats": 19.91,
  "prob_pass_threshold": 1.0,
  "ci_lower": 17,
  "ci_upper": 23
}
```

---

## Project structure

```
data/                     Input: parties.json + polls/ per election cycle
output/                   Generated results (mirrors data/)
specs.md                  Full specification
src/seker/
  bader_ofer.py           Pure seat-allocation logic (threshold, quota, surplus agreements)
  simulation.py           Dirichlet sampling + 100k allocation iterations
  stats.py                Mean, 90% CI, threshold probability, seat histograms
  io.py                   Loading inputs, writing outputs, discovering pending polls
  visualization.py        Injects a JSON payload into templates/visualization.html
  templates/              HTML template (vanilla JS + inline SVG)
  cli.py                  `seker run` / `seker viz` entry point
tests/                    pytest suite
```

---

## Development

```bash
pytest                                   # all tests
pytest tests/test_bader_ofer.py          # one file
pytest tests/test_bader_ofer.py::test_x  # one test
```
