from fastapi import APIRouter, HTTPException
from app.models import OptimizeRequest, OptimizeResponse
from app.engine.optimizer import optimize_budget
from app.database import get_cached_matches, cache_matches
from app.scrapers.sporttery import SportteryScraper
from app.scrapers.mock import get_mock_matches
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=OptimizeResponse)
async def optimize_budget_endpoint(request: OptimizeRequest) -> OptimizeResponse:
    """Generate optimal betting plan for given budget."""
    # Get available matches, refresh if empty
    matches = await get_cached_matches()

    if not matches:
        # Try fetching fresh data
        try:
            scraper = SportteryScraper()
            matches = await scraper.fetch_matches()
            if matches:
                await cache_matches(matches)
        except Exception as e:
            logger.warning(f"Scraper failed, using mock: {e}")
            matches = get_mock_matches()
            await cache_matches(matches)

    if not matches:
        return OptimizeResponse(
            budget=request.budget,
            risk_level=request.risk_level,
            recommendations=[],
            total_stake=0,
            max_potential_return=0,
            average_ev=0,
        )

    # Filter by bet types if specified
    if request.bet_types:
        matches = [m for m in matches if m.bet_type in request.bet_types]

    # Run optimizer
    try:
        recommendations = optimize_budget(
            matches=matches,
            budget=request.budget,
            risk_level=request.risk_level.value,
            max_matches=request.max_matches,
            min_odds=request.min_odds,
            max_odds=request.max_odds,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

    total_stake = sum(r.stake for r in recommendations)
    max_return = sum(r.potential_return for r in recommendations)
    avg_ev = sum(r.ev_score for r in recommendations) / len(recommendations) if recommendations else 0

    return OptimizeResponse(
        budget=request.budget,
        risk_level=request.risk_level,
        recommendations=recommendations,
        total_stake=round(total_stake, 2),
        max_potential_return=round(max_return, 2),
        average_ev=round(avg_ev, 4),
    )
