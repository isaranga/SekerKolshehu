import argparse
import logging
from pathlib import Path

from seker.io import (
    load_parties,
    load_poll,
    discover_pending_polls,
    write_stats,
    write_seat_counts,
)
from seker.simulation import run_simulation
from seker.stats import compute_stats, compute_seat_counts

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def run_poll(
    data_dir: Path,
    output_dir: Path,
    election: str,
    poll_name: str,
    n_iterations: int,
    seed: int,
) -> None:
    parties_path = data_dir / election / "parties.json"
    poll_path = data_dir / election / "polls" / f"{poll_name}.json"

    _, surplus_agreements = load_parties(parties_path)
    poll = load_poll(poll_path)

    poll_parties = set(poll["results"].keys())
    filtered_agreements = [
        (a, b)
        for a, b in surplus_agreements
        if a in poll_parties and b in poll_parties
    ]

    logger.info(f"Running {election}/{poll_name} ({n_iterations} iterations, seed={seed})...")
    seat_arrays = run_simulation(
        poll["results"],
        poll["sample_size"],
        filtered_agreements,
        n_iterations=n_iterations,
        seed=seed,
    )

    stats = compute_stats(seat_arrays)
    counts = compute_seat_counts(seat_arrays)

    poll_output = output_dir / election / poll_name
    write_stats(poll_output / "stats.json", stats)
    write_seat_counts(poll_output / "seat_counts.csv", counts)
    logger.info(f"Output written to {poll_output}")


def cmd_run(args: argparse.Namespace) -> None:
    root = _project_root()
    data_dir = root / "data"
    output_dir = root / "output"

    if args.election and args.poll:
        run_poll(data_dir, output_dir, args.election, args.poll, args.iterations, args.seed)
        return

    elections = sorted(p.name for p in data_dir.iterdir() if p.is_dir())
    any_run = False
    for election in elections:
        pending = discover_pending_polls(data_dir, output_dir, election)
        for poll_name in pending:
            run_poll(data_dir, output_dir, election, poll_name, args.iterations, args.seed)
            any_run = True

    if not any_run:
        logger.info("No pending polls found.")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="seker", description="Election poll Monte Carlo simulator")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run simulations")
    run_parser.add_argument("--election", type=str, default=None, help="Election cycle name")
    run_parser.add_argument("--poll", type=str, default=None, help="Poll name (without .json)")
    run_parser.add_argument("--iterations", type=int, default=100_000, help="Number of iterations")
    run_parser.add_argument("--seed", type=int, default=42, help="Random seed")

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    if args.command == "run":
        cmd_run(args)
    else:
        parser.print_help()
