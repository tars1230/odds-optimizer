"""Budget optimization algorithm using Kelly Criterion."""

from app.models import Match, BetRecommendation, BetType
from app.engine.kelly import kelly_criterion
from app.engine.ev import ev_score


# Risk multipliers for fractional Kelly
RISK_FRACTIONS = {
    "conservative": 0.25,  # Quarter Kelly
    "moderate": 0.5,       # Half Kelly
    "aggressive": 0.75,    # Three-quarter Kelly
}


def implied_probability(odds: float) -> float:
    """Convert decimal odds to implied probability."""
    return 1.0 / odds


def estimate_true_probability(odds: float, margin: float = 0.05) -> float:
    """
    Estimate true probability from odds.
    
    Bookmakers add margin (~5% typically).
    We estimate true prob = implied_prob * (1 - margin).
    """
    implied = implied_probability(odds)
    return implied * (1 - margin)


def optimize_budget(
    matches: list[Match],
    budget: float,
    risk_level: str = "moderate",
    max_matches: int = 5,
    min_odds: float = 1.5,
    max_odds: float = 20.0,
    margin: float = 0.05,
    true_probs: dict[str, float] | None = None,
) -> list[BetRecommendation]:
    """
    Generate optimal betting plan for given budget.
    
    Algorithm:
    1. Score each possible bet by EV * log(odds)
    2. Rank by score (highest first)
    3. Allocate budget using Kelly fractions
    4. Apply risk adjustment
    
    Args:
        matches: Available matches with odds
        budget: Total budget in RMB
        risk_level: "conservative", "moderate", or "aggressive"
        max_matches: Maximum number of matches to include
        min_odds: Minimum odds threshold
        max_odds: Maximum odds threshold
        margin: Bookmaker margin to remove from odds (default 5%)
        true_probs: Optional dict mapping "match_id:selection" to our estimated true probability
    
    Returns:
        List of betting recommendations
    """
    if not matches:
        return []
    
    fraction = RISK_FRACTIONS.get(risk_level, 0.5)
    candidates = []
    
    for match in matches:
        for selection, odds in match.odds.items():
            if odds < min_odds or odds > max_odds:
                continue
            
            key = f"{match.id}:{selection}"
            if true_probs and key in true_probs:
                true_prob = true_probs[key]
            else:
                true_prob = estimate_true_probability(odds, margin)
            
            kelly_f = kelly_criterion(true_prob, odds)
            
            if kelly_f <= 0:
                continue  # Skip negative EV bets
            
            score = ev_score(true_prob, odds)
            
            candidates.append({
                "match": match,
                "selection": selection,
                "odds": odds,
                "true_prob": true_prob,
                "kelly_fraction": kelly_f,
                "score": score,
            })
    
    # Sort by score (highest = best risk-reward)
    candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Take top N
    top_candidates = candidates[:max_matches]
    
    # Allocate budget using fractional Kelly
    recommendations = []
    remaining_budget = budget
    
    for candidate in top_candidates:
        if remaining_budget <= 0:
            break
        
        # Calculate stake
        optimal_stake = budget * candidate["kelly_fraction"] * fraction
        stake = min(optimal_stake, remaining_budget)
        
        if stake < 1.0:  # Minimum bet
            continue
        
        potential_return = stake * candidate["odds"]
        
        recommendations.append(BetRecommendation(
            match_id=candidate["match"].id,
            match_summary=f"{candidate['match'].home_team} vs {candidate['match'].away_team}",
            bet_type=BetType.WIN_DRAW_LOSS,
            selection=candidate["selection"],
            odds=candidate["odds"],
            stake=round(stake, 2),
            potential_return=round(potential_return, 2),
            kelly_fraction=round(candidate["kelly_fraction"], 4),
            ev_score=round(candidate["score"], 4),
            confidence=round(candidate["true_prob"], 4),
        ))
        
        remaining_budget -= stake
    
    return recommendations