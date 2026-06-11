"""Kelly Criterion calculator for optimal bet sizing."""


def kelly_criterion(win_prob: float, odds: float) -> float:
    """
    Calculate optimal Kelly fraction.
    
    f* = (p * b - q) / b
    where:
        p = probability of winning
        q = 1 - p (probability of losing)
        b = odds - 1 (net odds received on the bet)
    
    Args:
        win_prob: Estimated probability of winning (0, 1]
        odds: Decimal odds (must be > 1)
    
    Returns:
        Optimal fraction of bankroll to bet (can be negative = don't bet)
    """
    if odds <= 1.0:
        raise ValueError(f"Odds must be > 1.0, got {odds}")
    if win_prob <= 0 or win_prob >= 1:
        raise ValueError(f"Win probability must be in (0, 1), got {win_prob}")
    
    b = odds - 1.0
    q = 1.0 - win_prob
    
    return (win_prob * b - q) / b


def fractional_kelly(win_prob: float, odds: float, fraction: float = 0.5) -> float:
    """
    Apply fractional Kelly for reduced variance.
    
    Uses a fraction of the full Kelly bet to reduce volatility
    while maintaining positive expected value.
    
    Args:
        win_prob: Estimated probability of winning
        odds: Decimal odds
        fraction: Kelly fraction to use (0, 1], default 0.5 (half Kelly)
    
    Returns:
        Reduced Kelly fraction
    """
    full_kelly = kelly_criterion(win_prob, odds)
    return full_kelly * fraction