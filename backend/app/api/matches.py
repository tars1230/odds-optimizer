import logging
from datetime import datetime

from fastapi import APIRouter
from app.scrapers.sporttery import SportteryScraper
from app.scrapers.mock import get_mock_matches
from app.database import cache_matches, get_cached_matches

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_matches(refresh: bool = False, include_expired: bool = False) -> dict:
    """Get today's matches with odds.

    By default only returns future (betttable) matches.
    Set include_expired=true to see all matches.
    """
    # Try cache first
    if not refresh:
        cached = await get_cached_matches()
        if cached:
            matches = cached
            if not include_expired:
                now = datetime.now()
                matches = [m for m in matches if m.match_time > now]
            return {
                "matches": [m.model_dump() for m in matches],
                "source": "cache",
                "count": len(matches),
            }

    # Try official site
    try:
        scraper = SportteryScraper()
        matches = await scraper.fetch_matches()
        if matches:
            await cache_matches(matches)
            display = matches
            if not include_expired:
                now = datetime.now()
                display = [m for m in matches if m.match_time > now]
            return {
                "matches": [m.model_dump() for m in display],
                "source": "sporttery",
                "count": len(display),
            }
    except Exception as e:
        logger.warning(f"Sporttery scraper failed: {e}")

    # Fallback to mock data
    matches = get_mock_matches()
    await cache_matches(matches)
    return {
        "matches": [m.model_dump() for m in matches],
        "source": "mock",
        "count": len(matches),
    }


@router.get("/{match_id}")
async def get_match(match_id: str) -> dict:
    """Get specific match details."""
    cached = await get_cached_matches(max_age_seconds=3600)
    for match in cached:
        if match.id == match_id:
            return match.model_dump()
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Match not found")
