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
    Calculate EV-based score for ranking bets.
    
    Combines expected value with odds magnitude to favor
    higher-odds bets with positive EV (your core requirement).
    
    Score = EV * log(odds)
    
    This prioritizes bets that are:
    1. Positive EV (mathematically profitable)
    2. Higher odds (more upside potential)
    
    Args:
        win_prob: Probability of winning
        odds: Decimal odds
    
    Returns:
        Score for ranking (higher = better)
    """
    ev = win_prob * odds - 1.0  # EV per unit
    if ev <= 0:
        return -1.0  # Penalize negative EV bets
    return ev * math.log(odds)
