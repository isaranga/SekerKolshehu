import numpy as np
import pytest

from seker.bader_ofer import allocate_seats, _apply_threshold, _compute_initial_seats


class TestThreshold:
    def test_parties_below_threshold_get_zero(self):
        votes = {"A": 400, "B": 300, "C": 10}
        result = allocate_seats(votes, [], total_seats=120)
        assert result["C"] == 0

    def test_party_exactly_at_threshold(self):
        # 3.25% of 10000 = 325
        votes = {"A": 5000, "B": 4675, "C": 325}
        passing = _apply_threshold(votes, 120)
        assert "C" in passing

    def test_party_just_below_threshold(self):
        votes = {"A": 5000, "B": 4676, "C": 324}
        passing = _apply_threshold(votes, 120)
        assert "C" not in passing


class TestSimpleAllocation:
    def test_two_parties_no_surplus(self):
        # 60% vs 40% of votes -> should get ~72 and ~48 seats
        votes = {"A": 6000, "B": 4000}
        result = allocate_seats(votes, [], total_seats=120)
        assert result["A"] + result["B"] == 120
        assert result["A"] == 72
        assert result["B"] == 48

    def test_all_seats_distributed(self):
        votes = {"A": 5000, "B": 3000, "C": 2000}
        result = allocate_seats(votes, [], total_seats=120)
        assert sum(result.values()) == 120


class TestSurplusAgreements:
    def test_surplus_pair_benefits_from_agreement(self):
        # Two parties that agree vs one that doesn't
        votes = {"A": 4000, "B": 3500, "C": 2500}
        no_surplus = allocate_seats(votes, [], total_seats=10)
        with_surplus = allocate_seats(votes, [("A", "B")], total_seats=10)
        # The pair should get at least as many combined seats
        assert (with_surplus["A"] + with_surplus["B"]) >= (
            no_surplus["A"] + no_surplus["B"]
        )
        assert sum(with_surplus.values()) == 10

    def test_voided_agreement_one_below_threshold(self):
        # C is below threshold, so (B, C) agreement is voided
        votes = {"A": 6000, "B": 3900, "C": 100}
        result = allocate_seats(votes, [("B", "C")], total_seats=120)
        assert result["C"] == 0
        assert result["A"] + result["B"] == 120


class TestInternalApportionment:
    def test_internal_split_proportional(self):
        votes = {"A": 6000, "B": 2000, "C": 2000}
        result = allocate_seats(votes, [("B", "C")], total_seats=10)
        # B and C have equal votes, so should split evenly
        assert result["B"] == result["C"]


class TestTieBreaking:
    def test_deterministic_with_fixed_rng(self):
        votes = {"A": 5000, "B": 5000}
        rng1 = np.random.default_rng(42)
        rng2 = np.random.default_rng(42)
        r1 = allocate_seats(votes, [], total_seats=120, rng=rng1)
        r2 = allocate_seats(votes, [], total_seats=120, rng=rng2)
        assert r1 == r2


class TestRealElection:
    def test_25th_knesset_results(self):
        """Regression test against actual 25th Knesset 2022 election results."""
        # Actual vote counts from the 25th Knesset election
        votes = {
            "מחל": 1115336,
            "פה": 847435,
            "ט": 516470,
            "כן": 432482,
            "שס": 392964,
            "ג": 280194,
            "ל": 213687,
            "אמת": 175992,
            "ום": 178735,
            "עם": 194047,
            "מרצ": 150707,
            "ב": 130076,
            "ד": 138189,
        }
        surplus = [
            ("שס", "ג"),
            ("אמת", "מרצ"),
            ("מחל", "ט"),
            ("כן", "פה"),
        ]
        # Expected official results
        expected = {
            "מחל": 32,
            "פה": 24,
            "ט": 14,
            "כן": 12,
            "שס": 11,
            "ג": 7,
            "ל": 6,
            "אמת": 4,
            "ום": 5,
            "עם": 5,
            "מרצ": 0,
            "ב": 0,
            "ד": 0,
        }
        result = allocate_seats(votes, surplus, total_seats=120)
        assert result == expected
