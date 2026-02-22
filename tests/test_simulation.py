import numpy as np

from seker.simulation import run_simulation
from seker.stats import compute_stats, compute_seat_counts


class TestSimulation:
    def test_deterministic_with_seed(self):
        poll = {"A": 0.6, "B": 0.4}
        r1 = run_simulation(poll, 1000, [], n_iterations=100, seed=42)
        r2 = run_simulation(poll, 1000, [], n_iterations=100, seed=42)
        np.testing.assert_array_equal(r1["A"], r2["A"])
        np.testing.assert_array_equal(r1["B"], r2["B"])

    def test_seats_sum_to_120(self):
        poll = {"A": 0.5, "B": 0.3, "C": 0.2}
        result = run_simulation(poll, 500, [], n_iterations=100, seed=42)
        totals = sum(result[p] for p in poll)
        assert np.all(totals == 120)

    def test_below_threshold_party_gets_zero_mostly(self):
        poll = {"A": 0.95, "B": 0.02, "C": 0.03}
        result = run_simulation(poll, 1000, [], n_iterations=500, seed=42)
        # B at 2% is almost always below 3.25% threshold
        assert np.mean(result["B"] == 0) > 0.95


class TestStats:
    def test_compute_stats_structure(self):
        arrays = {
            "A": np.array([30, 31, 32, 29, 30]),
            "B": np.array([90, 89, 88, 91, 90]),
        }
        stats = compute_stats(arrays)
        for party in ["A", "B"]:
            assert "avg_seats" in stats[party]
            assert "prob_pass_threshold" in stats[party]
            assert "ci_lower" in stats[party]
            assert "ci_upper" in stats[party]

    def test_avg_seats_correct(self):
        arrays = {"A": np.array([10, 20, 30])}
        stats = compute_stats(arrays)
        assert stats["A"]["avg_seats"] == 20.0

    def test_prob_pass_threshold(self):
        arrays = {"A": np.array([0, 0, 5, 5])}
        stats = compute_stats(arrays)
        assert stats["A"]["prob_pass_threshold"] == 0.5

    def test_ci_bounds_are_integers(self):
        arrays = {"A": np.arange(100)}
        stats = compute_stats(arrays)
        assert isinstance(stats["A"]["ci_lower"], int)
        assert isinstance(stats["A"]["ci_upper"], int)


class TestSeatCounts:
    def test_counts_sum_to_iterations(self):
        arrays = {"A": np.array([0, 1, 2, 1, 0])}
        counts = compute_seat_counts(arrays)
        assert sum(counts["A"]) == 5

    def test_counts_length_121(self):
        arrays = {"A": np.array([0, 120])}
        counts = compute_seat_counts(arrays)
        assert len(counts["A"]) == 121

    def test_counts_correct_bins(self):
        arrays = {"A": np.array([3, 3, 3, 5])}
        counts = compute_seat_counts(arrays)
        assert counts["A"][3] == 3
        assert counts["A"][5] == 1
