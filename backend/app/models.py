from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class BetType(str, Enum):
    WIN_DRAW_LOSS = "win_draw_loss"  # 胜平负
    HANDICAP = "handicap"  # 让球盘
    OVER_UNDER = "over_under"  # 大小球
    CORRECT_SCORE = "correct_score"  # 比分
    BOTH_TEAMS_SCORE = "both_teams_score"  # 双方进球


class RiskLevel(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class Match(BaseModel):
    id: str
    league: str
    home_team: str
    away_team: str
    match_time: datetime
    odds: dict[str, float]  # {"home": 1.85, "draw": 3.40, "away": 4.20}
    bet_type: BetType
    source: str
    scraped_at: datetime = Field(default_factory=datetime.now)


class BetRecommendation(BaseModel):
    match_id: str
    match_summary: str
    bet_type: BetType
    selection: str  # "home", "draw", "away", "over", "under", etc.
    odds: float
    stake: float  # Amount to bet (RMB)
    potential_return: float
    kelly_fraction: float  # Optimal fraction from Kelly
    ev_score: float  # Expected value score
    confidence: float  # 0-1 confidence score


class OptimizeRequest(BaseModel):
    budget: float = Field(gt=0, le=100000)
    risk_level: RiskLevel = RiskLevel.MODERATE
    bet_types: list[BetType] = Field(default_factory=list)
    max_matches: int = Field(default=5, ge=1, le=10)
    min_odds: float = Field(default=1.5, ge=1.0)
    max_odds: float = Field(default=20.0, le=100.0)


class OptimizeResponse(BaseModel):
    budget: float
    risk_level: RiskLevel
    recommendations: list[BetRecommendation]
    total_stake: float
    max_potential_return: float
    average_ev: float
    generated_at: datetime = Field(default_factory=datetime.now)
