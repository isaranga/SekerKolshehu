import csv
import json
from pathlib import Path


def load_parties(path: str | Path) -> tuple[dict[str, str], list[tuple[str, str]]]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    symbols_to_names = data["parties"]
    surplus_agreements = [tuple(pair) for pair in data["surplus_agreements"]]
    return symbols_to_names, surplus_agreements


def load_poll(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def discover_pending_polls(
    data_dir: str | Path, output_dir: str | Path, election: str
) -> list[str]:
    data_dir = Path(data_dir)
    output_dir = Path(output_dir)
    polls_dir = data_dir / election / "polls"
    if not polls_dir.exists():
        return []
    pending = []
    for poll_file in sorted(polls_dir.glob("*.json")):
        poll_name = poll_file.stem
        output_path = output_dir / election / poll_name
        if not output_path.exists():
            pending.append(poll_name)
    return pending


def write_stats(output_path: str | Path, stats: dict) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def write_seat_counts(output_path: str | Path, seat_counts: dict[str, list[int]]) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    header = ["party"] + [f"{i}_seats" if i != 1 else "1_seat" for i in range(121)]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for party, counts in seat_counts.items():
            writer.writerow([party] + counts)
