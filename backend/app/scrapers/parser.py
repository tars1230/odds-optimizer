"""HTML parser for odds data."""

from bs4 import BeautifulSoup
import re
from datetime import datetime


def parse_odds_page(html: str) -> list[dict]:
    """Parse a full odds page HTML into match data."""
    soup = BeautifulSoup(html, "html.parser")
    matches = []
    
    # Find match rows (adjust selectors based on actual site structure)
    rows = soup.find_all("tr", class_=re.compile(r"match|row", re.I))
    
    for row in rows:
        match_data = parse_match_row(str(row))
        if match_data:
            matches.append(match_data)
    
    return matches


def parse_match_row(html: str) -> dict | None:
    """
    Parse a single match row from HTML.
    
    Returns dict with keys: league, home_team, away_team, match_time, odds
    """
    soup = BeautifulSoup(html, "html.parser")
    cells = soup.find_all(["td", "div"])
    
    if len(cells) < 7:
        return None
    
    try:
        league = cells[0].get_text(strip=True)
        home_team = cells[1].get_text(strip=True)
        away_team = cells[2].get_text(strip=True)
        match_time_str = cells[3].get_text(strip=True)
        
        # Parse odds
        home_odds = float(cells[4].get_text(strip=True))
        draw_odds = float(cells[5].get_text(strip=True))
        away_odds = float(cells[6].get_text(strip=True))
        
        # Parse time (try common formats)
        match_time = _parse_time(match_time_str)
        
        return {
            "league": league,
            "home_team": home_team,
            "away_team": away_team,
            "match_time": match_time,
            "odds": {
                "home": home_odds,
                "draw": draw_odds,
                "away": away_odds,
            },
        }
    except (ValueError, IndexError):
        return None


def _parse_time(time_str: str) -> datetime:
    """Try to parse various time formats."""
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%m-%d %H:%M",
        "%m/%d %H:%M",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    
    # Default to now if parsing fails
    return datetime.now()