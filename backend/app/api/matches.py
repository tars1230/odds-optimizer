import logging

from fastapi import APIRouter, HTTPException
from app.scrapers import AokeScraper
from app.scrapers.mock import get_mock_matches
from app.database import cache_matches, get_cached_matches

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def get_matches(refresh: bool = False) -> dict:
    """Get today's matches with odds.
    
    Args:
        refresh: Force refresh from source (ignore cache)
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
    
    # Fetch fresh data
    try:
        scraper = AokeScraper()
        matches = await scraper.fetch_matches()
        
        # Cache results
        await cache_matches(matches)
        
        return {
            "matches": [m.model_dump() for m in matches],
            "source": "live",
            "count": len(matches),
        }
    except Exception as e:
        logger.warning(f"Scraper failed, using mock data: {e}")
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
    raise HTTPException(status_code=404, detail="Match not found")
