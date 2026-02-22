from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from seker.bader_ofer import allocate_seats


SCALE = 10_000_000


def run_simulation(
    poll_results: dict[str, float],
    sample_size: int,
    surplus_agreements: list[tuple[str, str]],
    n_iterations: int = 100_000,
    seed: int = 42,
) -> dict[str, NDArray[np.int_]]:
    parties = list(poll_results.keys())
    alpha = np.array([poll_results[p] * sample_size for p in parties])

    rng = np.random.default_rng(seed)
    samples = rng.dirichlet(alpha, size=n_iterations)

    seat_arrays = {p: np.zeros(n_iterations, dtype=np.int_) for p in parties}

    for i in range(n_iterations):
        scaled = np.round(samples[i] * SCALE).astype(np.int64)
        votes = {p: int(scaled[j]) for j, p in enumerate(parties)}
        result = allocate_seats(votes, surplus_agreements, rng=rng)
        for p in parties:
            seat_arrays[p][i] = result[p]

    return seat_arrays
