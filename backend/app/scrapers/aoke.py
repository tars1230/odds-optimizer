"""澳客网 odds scraper."""

import asyncio
from datetime import datetime
from playwright.async_api import async_playwright

from app.scrapers.base import BaseScraper
from app.scrapers.parser import parse_odds_page
from app.models import Match, BetType
from app.config import settings


class AokeScraper(BaseScraper):
    """Scraper for aoke8.com odds data."""
    
    BASE_URL = "https://www.aoke8.com/jczq/"
    
    async def fetch_matches(self) -> list[Match]:
        """Fetch today's football matches from 澳客网."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(self.BASE_URL, timeout=settings.SCRAPER_TIMEOUT * 1000)
                await page.wait_for_load_state("networkidle")
                
                # Get page content
                html = await page.content()
                
                # Parse matches
                raw_matches = parse_odds_page(html)
                
                matches = []
                for raw in raw_matches:
                    match = Match(
                        id=f"aoke_{hash(raw['home_team'] + raw['away_team'])}",
                        league=raw["league"],
                        home_team=raw["home_team"],
                        away_team=raw["away_team"],
                        match_time=raw["match_time"],
                        odds=raw["odds"],
                        bet_type=BetType.WIN_DRAW_LOSS,
                        source="aoke",
                        scraped_at=datetime.now(),
                    )
                    matches.append(match)
                
                return matches
                
            finally:
                await browser.close()
    
    async def fetch_match_detail(self, match_id: str) -> Match | None:
        """Fetch detailed odds for a specific match."""
        # TODO: Implement match detail page scraping
        return None