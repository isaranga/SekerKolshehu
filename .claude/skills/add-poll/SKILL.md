---
name: add-poll
description: Extract Israeli election poll results from a PDF URL (usually a gov.il survey disclosure) and write a poll JSON file under data/<election>/polls/. Use when the user gives a poll PDF link and asks to add, extract, or import the poll.
argument-hint: <pdf-url> [election folder]
---

# Add a poll from a PDF

Input: a URL to a poll PDF (`$ARGUMENTS`). The election folder defaults to the latest one under `data/` (for example `data/26th-Knesset-2026/`) unless the user names another.

## 1. Fetch and read

- Download the PDF into the scratchpad directory with `curl -sSL -o <file>.pdf '<url>'`, then open it with the Read tool. Use the `pages` parameter for PDFs over 10 pages.
- Read `data/<election>/parties.json` and one or two existing files in `data/<election>/polls/` so the output matches their structure.

## 2. Extract

From the PDF, collect:

| Field | Source |
|---|---|
| `date` | The date the poll was conducted (not the publication date), as `YYYY-MM-DD` |
| `media` | The outlet that commissioned the poll (מזמין הסקר). Reuse the exact Hebrew spelling already in the repo: `חדשות 12`, `כאן 11`, `מעריב`, `ישראל היום`, `עכשיו 14` |
| `pollster` | The firm that ran the poll (עורך הסקר). Reuse existing spellings when the firm already appears (for example `לזר מחקרים`, `מדגם`, `Data Next`, `Direct Polls`) |
| `sample_size` | The number of respondents (מספר המשיבים), **not** the initial sample (גודל המדגם ההתחלתי) |
| `link` | The URL the user gave |
| results | The **raw vote percentage** of every party listed, including the ones below the threshold. Use the percentage column, not the seat counts |

Leave out "undecided" (לא החליטו), "won't vote", and similar rows. Note their values so you can report them.

Map each party name to its ballot symbol (the key in `parties.json`). Names in the PDF often differ from `parties.json`, because PDFs add "בראשות <leader>", use short names, or use the component party names (for example "יחד בראשות נפתלי בנט" → `רק`, "חד"ש-תע"ל-בל"ד" → `ודם`, "אח"י" → `צבי`). If a mapping is ambiguous or a party isn't in `parties.json`, ask the user. Don't guess.

Filename: `data/<election>/polls/<date>-<media-slug>.json`, using the slugs already in use: `news12`, `kan11`, `maariv`, `israeltoday`, `now14`. For a new outlet, pick a similar short lowercase slug.

## 3. Check the sum. Ask if it isn't 100%

Write a draft JSON to the scratchpad. It has the same fields as a poll file, but `results` holds the raw percentages exactly as printed (`24.9`, not `0.249`). Then run:

```bash
PYTHONIOENCODING=utf-8 python .claude/skills/add-poll/scripts/write_poll.py <draft.json> data/<election>/polls/<name>.json data/<election>/parties.json
```

The script checks every symbol against `parties.json`. It exits with code 2 if the percentages don't add up to 100.

**If they don't add up to 100%, stop and warn the user before writing anything.** Show:
- a table of party, symbol, and %
- the total above the threshold (and whether it matches any total printed in the PDF), the total below the threshold, and the overall total
- what explains the gap: undecided %, unnamed small parties, and so on

Then ask with AskUserQuestion. Offer **Normalize to 1.0 (Recommended)** first, then **Keep raw values**.

If the user picks normalize, re-run the script with `--normalize`. The script rounds to 3 decimals using largest remainder and **keeps tied parties tied**: parties with the same raw % always get the same value, and the leftover 0.001 goes to the party with the next-largest remainder. Tell the user which parties gained or lost 0.001 to rounding.

If the user picks keep raw values, re-run the script with `--raw`.

## 4. Report

Give the file path, the date, outlet, pollster, and sample size, any party-name mappings that weren't obvious, and any choices you made (for example respondents vs. the initial sample). Don't run the simulation unless asked. Mention the command for it: `seker run --election <election> --poll <name>`.
