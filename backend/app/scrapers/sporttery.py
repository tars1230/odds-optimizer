"""竞彩官网 scraper — JSON API (no Playwright needed)."""

import httpx
from datetime import datetime

from app.scrapers.base import BaseScraper
from app.models import Match, BetType


class SportteryScraper(BaseScraper):
    """Scraper using sporttery.cn JSON API — lightweight, no browser required."""

    API_URL = "https://webapi.sporttery.cn/gateway/uniform/football/getMatchCalculatorV1.qry"
    PARAMS = {"channel": "c"}
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://www.sporttery.cn/",
    }

    async def fetch_matches(self) -> list[Match]:
        """Fetch football matches from 竞彩官网 JSON API."""
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(self.API_URL, params=self.PARAMS, headers=self.HEADERS)
            resp.raise_for_status()
            data = resp.json()

        matches = []
        for day_group in data.get("value", {}).get("matchInfoList", []):
            for sub in day_group.get("subMatchList", []):
                match = self._parse_match(sub)
                if match:
                    matches.append(match)

        return matches

    def _parse_match(self, m: dict) -> Match | None:
        """Parse a single match from API response."""
        try:
            # Only include matches that are on sale
            if m.get("matchStatus") != "Selling":
                return None

            # HAD = 胜平负 odds
            had = m.get("had", {})
            home_odds = float(had.get("h", 0))
            draw_odds = float(had.get("d", 0))
            away_odds = float(had.get("a", 0))

            if not all([home_odds, draw_odds, away_odds]):
                return None

            # Parse time
            match_date = m.get("matchDate", "")  # "2026-06-13"
            match_time = m.get("matchTime", "")   # "03:00:00"
            dt = datetime.strptime(f"{match_date} {match_time[:5]}", "%Y-%m-%d %H:%M")

            return Match(
                id=f"sporttery_{m.get('matchNum')}",
                league=m.get("leagueAbbName", ""),
                home_team=m.get("homeTeamAbbName", ""),
                away_team=m.get("awayTeamAbbName", ""),
                match_time=dt,
                odds={"home": home_odds, "draw": draw_odds, "away": away_odds},
                bet_type=BetType.WIN_DRAW_LOSS,
                source="sporttery",
            )
        except Exception:
            return None

    async def fetch_match_detail(self, match_id: str) -> Match | None:
        return None
