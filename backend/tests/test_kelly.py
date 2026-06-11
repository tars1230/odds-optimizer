import pytest
from app.engine.kelly import kelly_criterion, fractional_kelly


class TestKellyCriterion:
    def test_positive_edge(self):
        # Win prob 60%, odds 2.0 → positive edge
        result = kelly_criterion(win_prob=0.6, odds=2.0)
        assert result > 0
        assert result == pytest.approx(0.2, rel=1e-2)  # 20% of bankroll

    def test_no_edge(self):
        # Win prob 50%, odds 2.0 → break even, no edge
        result = kelly_criterion(win_prob=0.5, odds=2.0)
        assert result == pytest.approx(0.0, abs=1e-2)

    def test_negative_edge(self):
        # Win prob 40%, odds 2.0 → negative edge
        result = kelly_criterion(win_prob=0.4, odds=2.0)
        assert result < 0

    def test_high_odds_low_prob(self):
        # Win prob 15%, odds 10.0 → positive edge (15% > 10% implied)
        result = kelly_criterion(win_prob=0.15, odds=10.0)
        assert result > 0

    def test_invalid_odds(self):
        with pytest.raises(ValueError):
            kelly_criterion(win_prob=0.5, odds=1.0)

    def test_invalid_prob(self):
        with pytest.raises(ValueError):
            kelly_criterion(win_prob=0.0, odds=2.0)


class TestFractionalKelly:
    def test_half_kelly(self):
        full = kelly_criterion(win_prob=0.6, odds=2.0)
        half = fractional_kelly(win_prob=0.6, odds=2.0, fraction=0.5)
        assert half == pytest.approx(full * 0.5, rel=1e-2)

    def test_quarter_kelly(self):
        full = kelly_criterion(win_prob=0.6, odds=2.0)
        quarter = fractional_kelly(win_prob=0.6, odds=2.0, fraction=0.25)
        assert quarter == pytest.approx(full * 0.25, rel=1e-2)