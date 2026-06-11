"""Expected value calculations for betting analysis."""

import math


def expected_value(win_prob: float, odds: float, stake: float = 1.0) -> float:
    """
    Calculate expected value of a bet.
    
    EV = (win_prob * odds * stake) - stake
       = stake * (win_prob * odds - 1)
    
    Args:
        win_prob: Probability of winning
        odds: Decimal odds
        stake: Amount bet
    
    Returns:
        Expected profit/loss
    """
    return stake * (win_prob * odds - 1.0)


def ev_score(win_prob: float, odds: float) -> float:
    """
    Score for ranking bets by risk-reward potential.
    
    Uses implied probability from odds (no edge assumption).
    Higher odds get exponentially more weight (log scaling).
    
    Score = log(odds) * odds
    
    This favors high-odds selections for maximum upside.
    
    Args:
        win_prob: Probability of winning (used for context, not in formula)
        odds: Decimal odds
    
    Returns:
        Score for ranking (higher = better)
    """
    if odds <= 1.0:
        return 0.0
    return math.log(odds) * odds
