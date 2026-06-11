import pytest
from datetime import datetime
from app.engine.optimizer import optimize_budget
from app.models import Match, BetType


@pytest.fixture
def sample_matches():
    """Odds include ~5% bookmaker margin. After margin removal, some have positive edge."""
    # Fair odds would be: home=2.105, draw=3.57, away=3.57 (sum of implied > 1)
    # These odds have margin baked in
    return [
        Match(
            id="m1",
            league="英超",
            home_team="利物浦",
            away_team="曼城",
            match_time=datetime(2025, 1, 15, 20, 0),
            odds={"home": 2.10, "draw": 3.40, "away": 3.40},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="test",
        ),
        Match(
            id="m2",
            league="西甲",
            home_team="巴萨",
            away_team="皇马",
            match_time=datetime(2025, 1, 15, 22, 0),
            odds={"home": 1.95, "draw": 3.50, "away": 3.80},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="test",
        ),
        Match(
            id="m3",
            league="德甲",
            home_team="拜仁",
            away_team="多特",
            match_time=datetime(2025, 1, 15, 21, 0),
            odds={"home": 1.75, "draw": 3.80, "away": 4.50},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="test",
        ),
    ]


class TestOptimizeBudget:
    def test_returns_recommendations(self, sample_matches):
        # Our model estimates true probabilities higher than implied (value bets)
        true_probs = {
            "m1:home": 0.52,   # odds 2.10 implies 0.476, we think 52%
            "m2:home": 0.55,   # odds 1.95 implies 0.513, we think 55%
            "m3:home": 0.60,   # odds 1.75 implies 0.571, we think 60%
        }
        result = optimize_budget(
            matches=sample_matches,
            budget=500,
            risk_level="moderate",
            margin=0.0,
            true_probs=true_probs,
        )
        assert len(result) > 0
        assert len(result) <= 5  # max_matches default

    def test_respects_budget(self, sample_matches):
        true_probs = {
            "m1:home": 0.52,
            "m2:home": 0.55,
            "m3:home": 0.60,
        }
        result = optimize_budget(
            matches=sample_matches,
            budget=500,
            risk_level="moderate",
            margin=0.0,
            true_probs=true_probs,
        )
        total_stake = sum(r.stake for r in result)
        assert total_stake <= 500

    def test_budget_100(self, sample_matches):
        true_probs = {
            "m1:home": 0.52,
            "m2:home": 0.55,
            "m3:home": 0.60,
        }
        result = optimize_budget(
            matches=sample_matches,
            budget=100,
            risk_level="conservative",
            margin=0.0,
            true_probs=true_probs,
        )
        total_stake = sum(r.stake for r in result)
        assert total_stake <= 100

    def test_aggressive_risk(self, sample_matches):
        true_probs = {
            "m1:home": 0.52,
            "m2:home": 0.55,
            "m3:home": 0.60,
        }
        result = optimize_budget(
            matches=sample_matches,
            budget=500,
            risk_level="aggressive",
            margin=0.0,
            true_probs=true_probs,
        )
        # Aggressive should allocate more per bet
        assert len(result) > 0

    def test_empty_matches(self):
        result = optimize_budget(
            matches=[],
            budget=500,
            risk_level="moderate",
        )
        assert result == []