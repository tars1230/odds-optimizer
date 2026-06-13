"""Budget optimization algorithm with proper stake rounding for China Sports Lottery."""

from app.models import Match, BetRecommendation, BetType
from app.engine.ev import ev_score


# China Sports Lottery rules
MIN_STAKE = 2.0      # Minimum bet is 2 RMB
STAKE_UNIT = 2.0     # Must be multiples of 2 RMB
MAX_STAKE = 50000.0  # Maximum single bet
MAX_TICKET = 20000.0 # Maximum per ticket


def implied_probability(odds: float) -> float:
    """Convert decimal odds to implied probability."""
    return 1.0 / odds


# Risk profiles: (max_bets, min_odds, power)
RISK_PROFILES = {
    "conservative": (10, 1.8, 0.3),
    "moderate":     (6,  1.5, 1.0),
    "aggressive":   (3,  2.5, 3.0),
}


def round_stake(amount: float) -> float:
    """Round stake to valid amount (multiples of 2 RMB, minimum 2)."""
    if amount < MIN_STAKE:
        return 0.0
    rounded = round(amount / STAKE_UNIT) * STAKE_UNIT
    return min(rounded, MAX_STAKE)


def optimize_budget(
    matches: list[Match],
    budget: float,
    risk_level: str = "moderate",
    max_matches: int = 5,
    min_odds: float = 1.5,
    max_odds: float = 20.0,
) -> list[BetRecommendation]:
    """
    Generate optimal betting plan with proper stake rounding.

    Rules:
    - Minimum stake: 2 RMB
    - Stakes must be multiples of 2 RMB
    - Total must not exceed budget
    """
    if not matches or budget < MIN_STAKE:
        return []

    profile = RISK_PROFILES.get(risk_level, RISK_PROFILES["moderate"])
    num_bets, profile_min_odds, power = profile
    effective_min_odds = max(min_odds, profile_min_odds)

    # Collect candidates
    candidates = []
    for match in matches:
        for selection, odds in match.odds.items():
            if odds < effective_min_odds or odds > max_odds:
                continue

            implied = implied_probability(odds)
            score = ev_score(implied, odds)
            if score <= 0:
                continue

            candidates.append({
                "match": match,
                "selection": selection,
                "odds": odds,
                "implied_prob": implied,
                "score": score,
            })

    if not candidates:
        return []

    candidates.sort(key=lambda x: x["score"], reverse=True)
    top_candidates = candidates[:num_bets]

    # Calculate weights for all top candidates at once
    total_weight = sum(c["score"] ** power for c in top_candidates)
    if total_weight <= 0:
        return []

    # Initial allocation
    allocations = []
    for candidate in top_candidates:
        weight = candidate["score"] ** power
        raw_stake = (weight / total_weight) * budget
        stake = round_stake(raw_stake)

        if stake >= MIN_STAKE:
            allocations.append({
                "candidate": candidate,
                "stake": stake,
            })

    if not allocations:
        return []

    # Calculate total and adjust
    total_allocated = sum(a["stake"] for a in allocations)
    remaining = budget - total_allocated

    # Distribute remaining budget to top picks
    if remaining >= STAKE_UNIT:
        for allocation in allocations:
            if remaining < STAKE_UNIT:
                break
            add_amount = min(STAKE_UNIT, remaining)
            allocation["stake"] += add_amount
            remaining -= add_amount

    # If still over budget, reduce from lowest-weighted bets
    total_allocated = sum(a["stake"] for a in allocations)
    if total_allocated > budget:
        # Remove lowest-weighted bets until under budget
        allocations.reverse()
        while allocations and sum(a["stake"] for a in allocations) > budget:
            allocations.pop(0)
        allocations.reverse()

    # Build final recommendations
    result = []
    for allocation in allocations:
        candidate = allocation["candidate"]
        stake = allocation["stake"]
        potential_return = stake * candidate["odds"]

        result.append(BetRecommendation(
            match_id=candidate["match"].id,
            match_summary=f"{candidate['match'].home_team} vs {candidate['match'].away_team}",
            bet_type=BetType.WIN_DRAW_LOSS,
            selection=candidate["selection"],
            odds=candidate["odds"],
            stake=stake,
            potential_return=round(potential_return, 2),
            kelly_fraction=0,
            ev_score=round(candidate["score"], 4),
            confidence=round(candidate["implied_prob"], 4),
        ))

    return result
