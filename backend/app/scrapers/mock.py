"""Mock data for development and demo."""

from datetime import datetime, timedelta
from app.models import Match, BetType


def get_mock_matches() -> list[Match]:
    """Return realistic mock match data for demo."""
    now = datetime.now()
    today = now.date()

    return [
        Match(
            id="mock_1",
            league="英超",
            home_team="利物浦",
            away_team="曼城",
            match_time=datetime.combine(today, datetime.strptime("20:00", "%H:%M").time()),
            odds={"home": 2.10, "draw": 3.40, "away": 3.20},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="mock",
        ),
        Match(
            id="mock_2",
            league="西甲",
            home_team="巴塞罗那",
            away_team="皇家马德里",
            match_time=datetime.combine(today, datetime.strptime("22:00", "%H:%M").time()),
            odds={"home": 1.95, "draw": 3.50, "away": 3.60},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="mock",
        ),
        Match(
            id="mock_3",
            league="德甲",
            home_team="拜仁慕尼黑",
            away_team="多特蒙德",
            match_time=datetime.combine(today, datetime.strptime("21:30", "%H:%M").time()),
            odds={"home": 1.65, "draw": 4.00, "away": 4.80},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="mock",
        ),
        Match(
            id="mock_4",
            league="意甲",
            home_team="国际米兰",
            away_team="AC米兰",
            match_time=datetime.combine(today, datetime.strptime("19:30", "%H:%M").time()),
            odds={"home": 2.05, "draw": 3.30, "away": 3.50},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="mock",
        ),
        Match(
            id="mock_5",
            league="法甲",
            home_team="巴黎圣日耳曼",
            away_team="马赛",
            match_time=datetime.combine(today, datetime.strptime("23:00", "%H:%M").time()),
            odds={"home": 1.45, "draw": 4.50, "away": 6.50},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="mock",
        ),
        Match(
            id="mock_6",
            league="英超",
            home_team="阿森纳",
            away_team="切尔西",
            match_time=datetime.combine(today, datetime.strptime("20:30", "%H:%M").time()),
            odds={"home": 1.80, "draw": 3.60, "away": 4.20},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="mock",
        ),
        Match(
            id="mock_7",
            league="西甲",
            home_team="马德里竞技",
            away_team="皇家社会",
            match_time=datetime.combine(today, datetime.strptime("18:00", "%H:%M").time()),
            odds={"home": 1.70, "draw": 3.80, "away": 4.60},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="mock",
        ),
        Match(
            id="mock_8",
            league="亚冠",
            home_team="上海海港",
            away_team="川崎前锋",
            match_time=datetime.combine(today, datetime.strptime("19:00", "%H:%M").time()),
            odds={"home": 2.30, "draw": 3.20, "away": 2.90},
            bet_type=BetType.WIN_DRAW_LOSS,
            source="mock",
        ),
    ]
