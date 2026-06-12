import pytest
from datetime import datetime
from app.engine.optimizer import optimize_budget
from app.models import Match, BetType


@pytest.fixture
def sample_matches():
    return [
        Match(
            id="m1",
            league="英超",
            home_team="利物浦",
            away_team="曼城",
            match_time=datetime(2025, 1, 15, 20, 0),
            odds={"home": 2.10, "draw": 3.40, "away": 3.20},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="test",
        ),
        Match(
            id="m2",
            league="西甲",
            home_team="巴萨",
            away_team="皇马",
            match_time=datetime(2025, 1, 15, 22, 0),
            odds={"home": 1.90, "draw": 3.60, "away": 3.80},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="test",
        ),
        Match(
            id="m3",
            league="德甲",
            home_team="拜仁",
            away_team="多特",
            match_time=datetime(2025, 1, 15, 21, 0),
            odds={"home": 1.60, "draw": 4.00, "away": 5.00},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="test",
        ),
    ]


class TestOptimizeBudget:
    def test_returns_recommendations(self, sample_matches):
        result = optimize_budget(
            matches=sample_matches,
            budget=500,
            risk_level="moderate",
        )
        assert len(result) > 0
        # Algorithm considers all selections (home/draw/away), so may return more than max_matches
        assert len(result) <= 15  # 5 matches * 3 selections maximum

    def test_full_budget_deployed(self, sample_matches):
        result = optimize_budget(
            matches=sample_matches,
            budget=500,
            risk_level="moderate",
        )
        total_stake = sum(r.stake for r in result)
        # Should deploy ~99%+ of budget
        assert total_stake >= 490
        assert total_stake <= 500

    def test_budget_2000(self, sample_matches):
        result = optimize_budget(
            matches=sample_matches,
            budget=2000,
            risk_level="moderate",
        )
        total_stake = sum(r.stake for r in result)
        assert total_stake >= 1980
        assert total_stake <= 2000

    def test_higher_odds_get_more_weight(self, sample_matches):
        result = optimize_budget(
            matches=sample_matches,
            budget=500,
            risk_level="moderate",
        )
        # Higher odds selections should have higher stakes
        if len(result) >= 2:
            # Find highest and lowest odds bets
            by_odds = sorted(result, key=lambda r: r.odds)
            assert by_odds[-1].stake >= by_odds[0].stake

    def test_empty_matches(self):
        result = optimize_budget(
            matches=[],
            budget=500,
            risk_level="moderate",
        )
        assert result == []

    def test_aggressive_concentrates_more(self, sample_matches):
        moderate = optimize_budget(sample_matches, 500, "moderate")
        aggressive = optimize_budget(sample_matches, 500, "aggressive")
        # Aggressive should give more to top pick
        if moderate and aggressive:
            assert aggressive[0].stake >= moderate[0].stake
