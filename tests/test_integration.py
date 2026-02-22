import csv
import json
from pathlib import Path

import numpy as np

from seker.cli import run_poll


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class TestIntegration:
    def test_end_to_end_small(self, tmp_path):
        """Run a small simulation on real poll data and verify outputs."""
        output_dir = tmp_path / "output"
        run_poll(
            data_dir=DATA_DIR,
            output_dir=output_dir,
            election="25th-Knesset-2022",
            poll_name="2022-10-27-now14",
            n_iterations=1000,
            seed=42,
        )

        poll_output = output_dir / "25th-Knesset-2022" / "2022-10-27-now14"
        assert (poll_output / "stats.json").exists()
        assert (poll_output / "seat_counts.csv").exists()

        # Verify stats.json structure
        with open(poll_output / "stats.json", encoding="utf-8") as f:
            stats = json.load(f)
        assert "מחל" in stats
        assert stats["מחל"]["avg_seats"] > 25
        assert stats["מחל"]["avg_seats"] < 40
        assert 0.0 <= stats["מחל"]["prob_pass_threshold"] <= 1.0
        assert stats["מחל"]["ci_lower"] <= stats["מחל"]["ci_upper"]

        # Verify seat_counts.csv
        with open(poll_output / "seat_counts.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            assert len(header) == 122  # party + 0..120
            rows = list(reader)

        # Each row should sum to n_iterations
        for row in rows:
            counts = [int(x) for x in row[1:]]
            assert sum(counts) == 1000

        # Parties below threshold should have prob < 1
        # ד at 2.1% is usually below threshold
        assert stats["ד"]["prob_pass_threshold"] < 1.0

    def test_big_parties_reasonable_seats(self, tmp_path):
        """Big parties should have reasonable average seat counts."""
        output_dir = tmp_path / "output"
        run_poll(
            data_dir=DATA_DIR,
            output_dir=output_dir,
            election="25th-Knesset-2022",
            poll_name="2022-10-27-now14",
            n_iterations=1000,
            seed=42,
        )
        poll_output = output_dir / "25th-Knesset-2022" / "2022-10-27-now14"
        with open(poll_output / "stats.json", encoding="utf-8") as f:
            stats = json.load(f)

        # מחל (Likud) at 28.3% should get ~30+ seats
        assert stats["מחל"]["avg_seats"] > 25
        # פה (Yesh Atid) at 18.3% should get ~20+ seats
        assert stats["פה"]["avg_seats"] > 15
        # All parties that always pass should have prob 1.0
        assert stats["מחל"]["prob_pass_threshold"] == 1.0
