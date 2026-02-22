import csv
import json
from pathlib import Path

from seker.io import (
    load_parties,
    load_poll,
    discover_pending_polls,
    write_stats,
    write_seat_counts,
)


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class TestLoadParties:
    def test_loads_symbols_and_names(self):
        symbols, agreements = load_parties(
            DATA_DIR / "25th-Knesset-2022" / "parties.json"
        )
        assert symbols["מחל"] == "הליכוד"
        assert isinstance(agreements, list)
        assert all(isinstance(pair, tuple) and len(pair) == 2 for pair in agreements)

    def test_surplus_agreements_content(self):
        _, agreements = load_parties(
            DATA_DIR / "25th-Knesset-2022" / "parties.json"
        )
        assert ("מחל", "ט") in agreements


class TestLoadPoll:
    def test_loads_poll_data(self):
        poll = load_poll(
            DATA_DIR / "25th-Knesset-2022" / "polls" / "2022-10-27-now14.json"
        )
        assert poll["sample_size"] == 2385
        assert "results" in poll
        assert poll["results"]["מחל"] == 0.283


class TestDiscoverPendingPolls:
    def test_finds_pending_polls(self, tmp_path):
        data_dir = tmp_path / "data"
        output_dir = tmp_path / "output"
        election = "test-election"
        polls_dir = data_dir / election / "polls"
        polls_dir.mkdir(parents=True)
        (polls_dir / "poll1.json").write_text("{}")
        (polls_dir / "poll2.json").write_text("{}")
        # poll1 already has output
        (output_dir / election / "poll1").mkdir(parents=True)

        pending = discover_pending_polls(data_dir, output_dir, election)
        assert pending == ["poll2"]

    def test_no_pending_when_all_done(self, tmp_path):
        data_dir = tmp_path / "data"
        output_dir = tmp_path / "output"
        election = "test"
        polls_dir = data_dir / election / "polls"
        polls_dir.mkdir(parents=True)
        (polls_dir / "p1.json").write_text("{}")
        (output_dir / election / "p1").mkdir(parents=True)

        assert discover_pending_polls(data_dir, output_dir, election) == []


class TestWriteStats:
    def test_writes_json(self, tmp_path):
        stats = {"מחל": {"avg_seats": 31.5}}
        path = tmp_path / "sub" / "stats.json"
        write_stats(path, stats)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded["מחל"]["avg_seats"] == 31.5


class TestWriteSeatCounts:
    def test_writes_csv(self, tmp_path):
        counts = {"A": [100] + [0] * 120, "B": [0] + [100] + [0] * 119}
        path = tmp_path / "seat_counts.csv"
        write_seat_counts(path, counts)
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            assert header[0] == "party"
            assert header[1] == "0_seats"
            assert header[2] == "1_seat"
            assert header[3] == "2_seats"
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0][0] == "A"
        assert rows[0][1] == "100"
