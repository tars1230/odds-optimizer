import pytest
from app.engine.ev import expected_value, ev_score


class TestExpectedValue:
    def test_positive_ev(self):
        # 60% win at 2.0 odds → EV = 0.6*2 - 1 = 0.2
        ev = expected_value(win_prob=0.6, odds=2.0, stake=100)
        assert ev == pytest.approx(20.0, rel=1e-2)

    def test_zero_ev(self):
        # 50% win at 2.0 odds → EV = 0
        ev = expected_value(win_prob=0.5, odds=2.0, stake=100)
        assert ev == pytest.approx(0.0, abs=1e-2)

    def test_negative_ev(self):
        # 40% win at 2.0 odds → EV = -0.2
        ev = expected_value(win_prob=0.4, odds=2.0, stake=100)
        assert ev == pytest.approx(-20.0, rel=1e-2)


class TestEVScore:
    def test_ranking(self):
        # Higher EV score should rank better
        score_a = ev_score(win_prob=0.6, odds=2.0)
        score_b = ev_score(win_prob=0.5, odds=2.0)
        assert score_a > score_b

    def test_high_odds_bonus(self):
        # Higher odds with same prob should score higher
        score_low = ev_score(win_prob=0.3, odds=3.0)
        score_high = ev_score(win_prob=0.3, odds=5.0)
        assert score_high > score_low