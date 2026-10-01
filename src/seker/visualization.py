import json
from importlib.resources import files
from pathlib import Path

from seker.bader_ofer import THRESHOLD, TOTAL_SEATS
from seker.io import load_parties, load_poll, load_seat_counts, load_stats

DATA_PLACEHOLDER = "/*__DATA__*/null"
OUTPUT_FILENAME = "visualization.html"
# Parties passing the threshold in fewer than this fraction of simulations go to the footnote
MIN_PASS_FRACTION = 0.001


def build_payload(
    symbols_to_names: dict[str, str],
    poll: dict,
    stats: dict,
    seat_counts: dict[str, list[int]],
    election: str,
    poll_name: str,
) -> dict:
    results = poll["results"]
    parties = [
        {
            "symbol": symbol,
            "name": symbols_to_names.get(symbol, symbol),
            "poll_share": results.get(symbol, 0.0),
            **party_stats,
            "counts": seat_counts[symbol],
            # From raw counts: prob_pass_threshold is rounded and can hide rare passes
            "pass_count": sum(seat_counts[symbol]) - seat_counts[symbol][0],
        }
        for symbol, party_stats in stats.items()
    ]
    parties.sort(key=lambda p: (p["avg_seats"], p["poll_share"]), reverse=True)
    iterations = sum(next(iter(seat_counts.values()))) if seat_counts else 0
    min_pass_count = iterations * MIN_PASS_FRACTION
    return {
        "election": election,
        "poll_name": poll_name,
        "meta": {
            "date": poll.get("date"),
            "media": poll.get("media"),
            "pollster": poll.get("pollster"),
            "sample_size": poll.get("sample_size"),
            "link": poll.get("link"),
        },
        "iterations": iterations,
        "min_pass_fraction": MIN_PASS_FRACTION,
        "min_pass_count": min_pass_count,
        "threshold": THRESHOLD,
        "total_seats": TOTAL_SEATS,
        "parties": parties,
    }


def render_html(payload: dict) -> str:
    template = (files("seker") / "templates" / OUTPUT_FILENAME).read_text(encoding="utf-8")
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    return template.replace(DATA_PLACEHOLDER, data)


def build_visualization(
    data_dir: Path, output_dir: Path, election: str, poll_name: str
) -> Path:
    symbols_to_names, _ = load_parties(data_dir / election / "parties.json")
    poll = load_poll(data_dir / election / "polls" / f"{poll_name}.json")
    poll_output = output_dir / election / poll_name
    stats = load_stats(poll_output / "stats.json")
    seat_counts = load_seat_counts(poll_output / "seat_counts.csv")

    payload = build_payload(symbols_to_names, poll, stats, seat_counts, election, poll_name)
    output_path = poll_output / OUTPUT_FILENAME
    output_path.write_text(render_html(payload), encoding="utf-8")
    return output_path
