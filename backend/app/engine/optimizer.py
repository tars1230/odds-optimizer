"""Budget optimization algorithm — full deployment mode."""

from app.models import Match, BetRecommendation, BetType
from app.engine.ev import ev_score


def implied_probability(odds: float) -> float:
    """Convert decimal odds to implied probability."""
    return 1.0 / odds


# Risk profiles: (max_bets, min_odds, power)
# power controls how concentrated the allocation is
RISK_PROFILES = {
    "conservative": (10, 1.8, 0.3),   # More bets, higher min odds, very even spread
    "moderate":     (6,  1.5, 1.0),   # Balanced
    "aggressive":   (3,  2.5, 3.0),   # Few bets, high odds only, very concentrated
}


def optimize_budget(
    matches: list[Match],
    budget: float,
    risk_level: str = "moderate",
    max_matches: int = 5,
    min_odds: float = 1.5,
    max_odds: float = 20.0,
) -> list[BetRecommendation]:
    """
    Generate optimal betting plan — full budget deployment.

    Risk levels have meaningfully different strategies:
    - conservative: 10 bets, spread evenly, lower odds, safer
    - moderate: 6 bets, weighted by score, balanced
    - aggressive: 3 bets, concentrate on top high-odds picks, maximum upside
    """
    if not matches:
        return []

    profile = RISK_PROFILES.get(risk_level, RISK_PROFILES["moderate"])
    num_bets, profile_min_odds, power = profile
    effective_min_odds = max(min_odds, profile_min_odds)

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
    top = candidates[:num_bets]

    total_weight = sum(c["score"] ** power for c in top)
    if total_weight <= 0:
        return []

    recommendations = []
    allocated = 0.0

    for i, candidate in enumerate(top):
        weight = candidate["score"] ** power
        stake = (weight / total_weight) * budget

        if i == len(top) - 1:
            stake = budget - allocated

        stake = round(stake, 2)
        if stake < 1.0:
            continue

        potential_return = stake * candidate["odds"]

        recommendations.append(BetRecommendation(
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

        allocated += stake

    return recommendations
