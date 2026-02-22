from numpy.random import Generator


TOTAL_SEATS = 120
THRESHOLD = 0.0325


def allocate_seats(
    votes: dict[str, float],
    surplus_agreements: list[tuple[str, str]],
    total_seats: int = TOTAL_SEATS,
    rng: Generator | None = None,
) -> dict[str, int]:
    parties = list(votes.keys())
    passing = _apply_threshold(votes, total_seats)
    seats = _compute_initial_seats(votes, passing, total_seats)
    valid_agreements = [
        (a, b)
        for a, b in surplus_agreements
        if a in passing and b in passing
    ]
    seats = _distribute_remaining(votes, seats, valid_agreements, total_seats, rng)
    seats = _internal_apportion(votes, seats, valid_agreements, rng)
    return {p: seats.get(p, 0) for p in parties}


def _apply_threshold(
    votes: dict[str, float], total_seats: int
) -> set[str]:
    total = sum(votes.values())
    min_votes = total * THRESHOLD
    return {p for p, v in votes.items() if v >= min_votes}


def _compute_initial_seats(
    votes: dict[str, float],
    passing: set[str],
    total_seats: int,
) -> dict[str, int]:
    participating_votes = sum(votes[p] for p in passing)
    if participating_votes == 0:
        return {p: 0 for p in passing}
    quota = int(participating_votes // total_seats)
    if quota == 0:
        return {p: 0 for p in passing}
    return {p: int(votes[p] // quota) for p in passing}


def _distribute_remaining(
    votes: dict[str, float],
    seats: dict[str, int],
    valid_agreements: list[tuple[str, str]],
    total_seats: int,
    rng: Generator | None,
) -> dict[str, int]:
    seats = dict(seats)
    distributed = sum(seats.values())
    remaining = total_seats - distributed

    paired = {}
    for a, b in valid_agreements:
        paired[a] = b
        paired[b] = a

    entities: list[tuple[str, ...]] = []
    seen = set()
    for a, b in valid_agreements:
        entities.append((a, b))
        seen.add(a)
        seen.add(b)
    for p in seats:
        if p not in seen:
            entities.append((p,))

    for _ in range(remaining):
        best_quota = -1.0
        best_entities: list[tuple[str, ...]] = []
        for entity in entities:
            entity_votes = sum(votes[p] for p in entity)
            entity_seats = sum(seats[p] for p in entity)
            eq = entity_votes / (entity_seats + 1)
            if eq > best_quota:
                best_quota = eq
                best_entities = [entity]
            elif eq == best_quota:
                best_entities.append(entity)

        if len(best_entities) > 1 and rng is not None:
            winner = best_entities[rng.integers(len(best_entities))]
        else:
            winner = best_entities[0]

        # Award the seat to the first party in the entity
        # (for pairs, internal apportionment handles redistribution later)
        seats[winner[0]] = seats.get(winner[0], 0) + 1

    return seats


def _internal_apportion(
    votes: dict[str, float],
    seats: dict[str, int],
    valid_agreements: list[tuple[str, str]],
    rng: Generator | None,
) -> dict[str, int]:
    seats = dict(seats)
    for a, b in valid_agreements:
        combined = seats.get(a, 0) + seats.get(b, 0)
        pair_votes = {a: votes[a], b: votes[b]}
        pair_passing = {a, b}
        pair_seats = _compute_initial_seats(pair_votes, pair_passing, combined)
        pair_seats = _distribute_remaining(
            pair_votes, pair_seats, [], combined, rng
        )
        seats[a] = pair_seats.get(a, 0)
        seats[b] = pair_seats.get(b, 0)
    return seats
