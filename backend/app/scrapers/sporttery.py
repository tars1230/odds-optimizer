"""竞彩官网 scraper — sporttery.cn"""

import re
from datetime import datetime
from playwright.async_api import async_playwright

from app.scrapers.base import BaseScraper
from app.models import Match, BetType
from app.config import settings


class SportteryScraper(BaseScraper):
    """Scraper for sporttery.cn official lottery odds."""

    URL = "https://www.sporttery.cn/jc/jsq/index.html"

    async def fetch_matches(self) -> list[Match]:
        """Fetch football matches from 竞彩官网."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(self.URL, timeout=settings.SCRAPER_TIMEOUT * 1000)
                await page.wait_for_load_state("networkidle")
                return await self._parse_table(page)
            finally:
                await browser.close()

    async def _parse_table(self, page) -> list[Match]:
        """Parse match data from table rows."""
        matches = []
        rows = await page.query_selector_all("tr")

        for row in rows:
            text = await row.inner_text()
            lines = [l.strip() for l in text.strip().split("\n") if l.strip()]

            # Match rows have 11 lines: day, id+league+date, time+teams, handicap info x3, odds x2, footer
            if len(lines) < 7:
                continue

            match = self._parse_match(lines)
            if match:
                matches.append(match)

        return matches

    def _parse_match(self, lines: list[str]) -> Match | None:
        """Parse a match from its text lines."""
        try:
            # Line 1: "001\t世界杯\t06-12"
            id_line = lines[1]
            id_match = re.match(r"(\d{3})\t(.+?)\t(\d{2}-\d{2})", id_line)
            if not id_match:
                return None

            match_num = id_match.group(1)
            league = id_match.group(2)
            date_str = id_match.group(3)

            # Line 2: "03:00\t[A组1]墨西哥VS南非[A组2]"
            time_line = lines[2]
            time_match = re.match(r"(\d{2}:\d{2})\t(.+)", time_line)
            if not time_match:
                return None

            time_str = time_match.group(1)
            teams_raw = time_match.group(2)

            # Parse teams: "[A组1]墨西哥VS南非[A组2]" -> "墨西哥", "南非"
            team_match = re.search(r"(?:\[.*?\])?(.+?)VS(.+?)(?:\[.*?\])?$", teams_raw)
            if not team_match:
                return None

            home_team = team_match.group(1).strip()
            away_team = team_match.group(2).strip()

            # Parse datetime
            month, day = date_str.split("-")
            hour, minute = time_str.split(":")
            match_time = datetime(
                datetime.now().year, int(month), int(day), int(hour), int(minute)
            )

            # Find odds line: "1.264.459.00" format
            odds = None
            for line in lines[3:]:
                odds = self._parse_odds_line(line)
                if odds:
                    break

            if not odds:
                return None

            return Match(
                id=f"sporttery_{match_num}",
                league=league,
                home_team=home_team,
                away_team=away_team,
                match_time=match_time,
                odds=odds,
                bet_type=BetType.WIN_DRAW_LOSS,
                source="sporttery",
            )

        except Exception:
            return None

    def _parse_odds_line(self, line: str) -> dict[str, float] | None:
        """Parse odds from a line like '1.264.459.00' or '------'."""
        line = line.strip()

        # Skip invalid lines
        if "------" in line or "未开售" in line or not line:
            return None

        # Try concatenated format: "1.264.459.00"
        match = re.match(r"^(\d+\.\d{2})(\d+\.\d{2})(\d+\.\d{2})$", line)
        if match:
            home = float(match.group(1))
            draw = float(match.group(2))
            away = float(match.group(3))
            if self._valid_odds(home, draw, away):
                return {"home": home, "draw": draw, "away": away}

        return None

    def _valid_odds(self, home: float, draw: float, away: float) -> bool:
        """Validate odds are reasonable."""
        return (
            1.01 <= home <= 100
            and 1.01 <= draw <= 100
            and 1.01 <= away <= 100
        )

    async def fetch_match_detail(self, match_id: str) -> Match | None:
        """Fetch detailed odds for a specific match."""
        return None
