import logging

from fastapi import APIRouter
from app.scrapers.sporttery import SportteryScraper
from app.scrapers.mock import get_mock_matches
from app.database import cache_matches, get_cached_matches

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_matches(refresh: bool = False) -> dict:
    """Get today's matches with odds.

    Tries sporttery.cn first, falls back to mock data.
    """
    # Try cache first
    if not refresh:
        cached = await get_cached_matches()
        if cached:
            return {
                "matches": [m.model_dump() for m in cached],
                "source": "cache",
                "count": len(cached),
            }

    # Try official site
    try:
        scraper = SportteryScraper()
        matches = await scraper.fetch_matches()
        if matches:
            await cache_matches(matches)
            return {
                "matches": [m.model_dump() for m in matches],
                "source": "sporttery",
                "count": len(matches),
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
