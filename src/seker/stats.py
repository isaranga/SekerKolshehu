from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def compute_stats(seat_arrays: dict[str, NDArray[np.int_]]) -> dict:
    stats = {}
    for party, arr in seat_arrays.items():
        stats[party] = {
            "avg_seats": round(float(np.mean(arr)), 2),
            "prob_pass_threshold": round(float(np.mean(arr > 0)), 4),
            "ci_lower": int(np.percentile(arr, 5)),
            "ci_upper": int(np.percentile(arr, 95)),
        }
    return stats


def compute_seat_counts(seat_arrays: dict[str, NDArray[np.int_]]) -> dict[str, list[int]]:
    counts = {}
    for party, arr in seat_arrays.items():
        bins = np.bincount(arr, minlength=121)
        counts[party] = bins[:121].tolist()
    return counts
