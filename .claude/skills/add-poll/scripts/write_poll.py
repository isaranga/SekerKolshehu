"""Validate (and optionally normalize) raw poll percentages and write a poll JSON file.

Usage:
    python write_poll.py <draft.json> <output_poll.json> <parties.json> [--normalize | --raw]

The draft has the same fields as a poll file, but "results" holds the raw
percentages exactly as printed in the PDF (e.g. 24.9, not 0.249).

Without flags, the results are written as fractions (percent / 100), and the
script exits with code 2 if they don't sum to 100. With --raw, they are written
as fractions even if they don't sum to 100.
With --normalize, the results are scaled to sum to exactly 1.000 at 3-decimal
precision using largest-remainder rounding. Parties with equal raw values always
get equal rounded values: a tied group whose members can't all be rounded up is
skipped, and the next-largest remainder gets the leftover 0.001 instead.
"""

import json
import math
import sys
from itertools import groupby

UNITS = 1000  # 3-decimal precision


def normalize(raw: dict[str, float]) -> dict[str, int]:
    total = sum(raw.values())
    exact = {k: v / total * UNITS for k, v in raw.items()}
    units = {k: math.floor(x) for k, x in exact.items()}
    left = UNITS - sum(units.values())

    def remainder(k):
        return round(exact[k] - units[k], 9)

    ordered = sorted(exact, key=remainder, reverse=True)
    skipped = []
    for _, group in groupby(ordered, key=remainder):
        group = list(group)
        if left <= 0:
            break
        if len(group) <= left:
            for k in group:
                units[k] += 1
            left -= len(group)
        else:
            skipped.extend(group)
    if left:
        # Could not avoid breaking a tie; fall back to the order in the draft.
        print(f"WARNING: had to break a tie among {skipped}", file=sys.stderr)
        for k in skipped[:left]:
            units[k] += 1
    return units


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_normalize = "--normalize" in sys.argv
    draft_path, out_path, parties_path = args

    with open(draft_path, encoding="utf-8") as f:
        draft = json.load(f)
    with open(parties_path, encoding="utf-8") as f:
        parties = json.load(f)["parties"]

    raw = draft["results"]
    unknown = [k for k in raw if k not in parties]
    if unknown:
        sys.exit(f"ERROR: symbols not in parties.json: {unknown}")

    raw_sum = round(sum(raw.values()), 6)
    if do_normalize:
        units = normalize(raw)
    else:
        if raw_sum != 100 and "--raw" not in sys.argv:
            print(f"Raw results sum to {raw_sum}%, not 100%. Re-run with --normalize "
                  "after confirming with the user.", file=sys.stderr)
            sys.exit(2)
        units = {k: round(v * UNITS / 100) for k, v in raw.items()}

    if sum(units.values()) != UNITS and "--raw" not in sys.argv:
        sys.exit(f"ERROR: rounded results sum to {sum(units.values()) / UNITS}")

    lines = ",\n".join(f'    "{k}": {v / UNITS:.3f}' for k, v in units.items())
    out = (
        "{\n"
        f'  "date": "{draft["date"]}",\n'
        f'  "media": "{draft["media"]}",\n'
        f'  "pollster": "{draft["pollster"]}",\n'
        f'  "sample_size": {int(draft["sample_size"])},\n'
        f'  "link": "{draft["link"]}",\n'
        '  "results": {\n'
        f"{lines}\n"
        "  }\n"
        "}\n"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"Wrote {out_path} (raw sum {raw_sum}%, {len(units)} parties)")


if __name__ == "__main__":
    main()
