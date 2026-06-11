import pytest
from app.engine.ev import expected_value, ev_score


class TestExpectedValue:
    def test_positive_ev(self):
        ev = expected_value(win_prob=0.6, odds=2.0, stake=100)
        assert ev == pytest.approx(20.0, rel=1e-2)

    def test_zero_ev(self):
        ev = expected_value(win_prob=0.5, odds=2.0, stake=100)
        assert ev == pytest.approx(0.0, abs=1e-2)

    def test_negative_ev(self):
        ev = expected_value(win_prob=0.4, odds=2.0, stake=100)
        assert ev == pytest.approx(-20.0, rel=1e-2)


class TestEVScore:
    def test_higher_odds_score_higher(self):
        score_low = ev_score(win_prob=0.3, odds=3.0)
        score_high = ev_score(win_prob=0.3, odds=5.0)
        assert score_high > score_low

    def test_odds_2_vs_10(self):
        s2 = ev_score(win_prob=0.5, odds=2.0)
        s10 = ev_score(win_prob=0.1, odds=10.0)
        assert s10 > s2

    def test_zero_for_invalid(self):
        assert ev_score(win_prob=0.5, odds=1.0) == 0.0
