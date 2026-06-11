"""Budget optimization algorithm — full deployment mode."""

from app.models import Match, BetRecommendation, BetType
from app.engine.ev import ev_score


def implied_probability(odds: float) -> float:
    """Convert decimal odds to implied probability."""
    return 1.0 / odds


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
    
    Strategy:
    1. Score each selection by EV * log(odds) — prioritizes high-odds value
    2. Rank and pick top N
    3. Allocate full budget weighted by score (higher score = more money)
    
    Args:
        matches: Available matches with odds
        budget: Total budget in RMB (fully deployed)
        risk_level: "conservative", "moderate", or "aggressive"
        max_matches: Maximum number of bets
        min_odds: Minimum odds threshold
        max_odds: Maximum odds threshold
    
    Returns:
        List of betting recommendations totaling ~budget
    """
    if not matches:
        return []

    # Risk multipliers control concentration
    # conservative = spread evenly, aggressive = concentrate on top picks
    concentration = {
        "conservative": 0.6,   # More even spread
        "moderate": 1.0,       # Standard weighted
        "aggressive": 1.5,     # Concentrate on top picks
    }
    power = concentration.get(risk_level, 1.0)

    candidates = []

    for match in matches:
        for selection, odds in match.odds.items():
            if odds < min_odds or odds > max_odds:
                continue

            implied = implied_probability(odds)
            # EV score: positive means our estimated edge
            score = ev_score(implied, odds)
            if score <= 0:
                continue  # skip invalid odds

            candidates.append({
                "match": match,
                "selection": selection,
                "odds": odds,
                "implied_prob": implied,
                "score": score,
            })

    if not candidates:
        return []

    # Sort by score (highest = best risk-reward)
    candidates.sort(key=lambda x: x["score"], reverse=True)

    # Take top N
    top = candidates[:max_matches]

    # Weighted allocation: score^power gives more weight to top picks
    total_weight = sum(c["score"] ** power for c in top)
    if total_weight <= 0:
        return []

    recommendations = []
    allocated = 0.0

    for i, candidate in enumerate(top):
        # Calculate proportional stake
        weight = candidate["score"] ** power
        stake = (weight / total_weight) * budget

        # Last bet gets remainder to avoid rounding gaps
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
